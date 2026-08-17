-- =====================================================================
-- Sentiment-Aware Data Warehouse
-- Translates Chapter 4 (Tables 10-17) into SQLite DDL.
-- Every column name, key and domain below matches what is documented
-- in the thesis. No new attributes are introduced here.
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- D_DATE  (Table 10)
-- Calendar dimension, pre-populated 2015-2029.
-- date_key is a deterministic surrogate in YYYYMMDD format, not an
-- autoincrement key, exactly as specified.
-- ---------------------------------------------------------------------
CREATE TABLE D_DATE (
    date_key      INTEGER PRIMARY KEY,                 -- PK, e.g. 20240215
    full_date     DATE NOT NULL,
    day_of_month  TINYINT NOT NULL CHECK (day_of_month BETWEEN 1 AND 31),
    day_name      VARCHAR(10) NOT NULL,
    month         TINYINT NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_name    VARCHAR(10) NOT NULL,
    quarter       TINYINT NOT NULL CHECK (quarter BETWEEN 1 AND 4),
    year          SMALLINT NOT NULL,
    season        VARCHAR(10) NOT NULL
                  CHECK (season IN ('Winter','Spring','Summer','Autumn'))
);
CREATE INDEX IDX_D_DATE_YEAR ON D_DATE (year);
CREATE INDEX IDX_D_DATE_YEAR_MONTH ON D_DATE (year, month);

-- ---------------------------------------------------------------------
-- D_LOCATION  (Table 11)
-- Static outrigger, Portuguese geographic hierarchy.
-- SCD Type 1: updates overwrite, no historical versioning.
-- ---------------------------------------------------------------------
CREATE TABLE D_LOCATION (
    location_key      INTEGER PRIMARY KEY,
    municipality_code  VARCHAR(10) NOT NULL,            -- NK
    region            VARCHAR(40) NOT NULL
                      CHECK (region IN (
                          'Norte','Centro','Lisboa','Alentejo','Algarve',
                          'Região Autónoma dos Açores','Região Autónoma da Madeira'
                      )),
    district          VARCHAR(40) NOT NULL,
    municipality      VARCHAR(80) NOT NULL
);
CREATE UNIQUE INDEX UQ_D_LOCATION_NK ON D_LOCATION (municipality_code);
CREATE INDEX IDX_D_LOCATION_REGION ON D_LOCATION (region);
CREATE INDEX IDX_D_LOCATION_DISTRICT ON D_LOCATION (district);

-- ---------------------------------------------------------------------
-- D_SERVICE  (Table 12)
-- SCD Type 2. valid_to uses a far-future sentinel for the current row,
-- which is what makes the (platform_service_id, valid_to) key work as
-- a uniqueness guard across both active and historical versions.
-- ---------------------------------------------------------------------
CREATE TABLE D_SERVICE (
    service_key           INTEGER PRIMARY KEY,
    platform_service_id   VARCHAR(50) NOT NULL,         -- NK
    location_key          INTEGER NOT NULL,             -- FK -> D_LOCATION
    service_name          VARCHAR(150) NOT NULL,
    service_category      VARCHAR(30) NOT NULL
                          CHECK (service_category IN
                              ('Accommodation','Restaurant/Bar','Tourist Site')),
    service_subcategory   VARCHAR(50),
    star_rating           TINYINT
                          CHECK (star_rating IS NULL OR star_rating BETWEEN 1 AND 5),
    price_tier            VARCHAR(10)
                          CHECK (price_tier IN ('Low','Medium','High','Luxury')),
    is_current            BOOLEAN NOT NULL CHECK (is_current IN (0,1)),
    valid_from            DATE NOT NULL,
    valid_to              DATE NOT NULL,
    FOREIGN KEY (location_key) REFERENCES D_LOCATION (location_key)
);
CREATE UNIQUE INDEX UQ_D_SERVICE_NK ON D_SERVICE (platform_service_id, valid_to);
CREATE INDEX IDX_D_SERVICE_CATEGORY ON D_SERVICE (service_category);

-- ---------------------------------------------------------------------
-- D_ASPECT  (Table 13)
-- SCD Type 1. Controlled analytical taxonomy, not a record of events.
-- ---------------------------------------------------------------------
CREATE TABLE D_ASPECT (
    aspect_key          INTEGER PRIMARY KEY,
    aspect_code         VARCHAR(30) NOT NULL,           -- NK
    aspect_name         VARCHAR(100) NOT NULL,
    aspect_category     VARCHAR(50) NOT NULL
                        CHECK (aspect_category IN (
                            'Location','Physical Environment','Staff and Service',
                            'Core Offering','Value and Pricing','Experience and Atmosphere'
                        )),
    aspect_description  VARCHAR(255)
);
CREATE UNIQUE INDEX UQ_D_ASPECT_NK ON D_ASPECT (aspect_code);
CREATE INDEX IDX_D_ASPECT_CATEGORY ON D_ASPECT (aspect_category);

-- ---------------------------------------------------------------------
-- D_TRAVEL_SEGMENT  (Table 14)
-- Static outrigger connected through D_REVIEW. Individual attributes
-- may be NULL when source data is incomplete, but every review still
-- points at a segment row (an "unknown" row rather than a null FK),
-- consistent with Kimball practice elsewhere in the model.
-- ---------------------------------------------------------------------
CREATE TABLE D_TRAVEL_SEGMENT (
    travel_segment_key   INTEGER PRIMARY KEY,
    travel_segment_code  VARCHAR(80) NOT NULL,          -- NK
    nationality          VARCHAR(60),
    age_group            VARCHAR(20)
                         CHECK (age_group IS NULL OR age_group IN (
                             '<18','18-24','25-34','35-44','45-54','55-64','65+'
                         )),
    gender               VARCHAR(20)
                         CHECK (gender IS NULL OR gender IN ('Female','Male','Other/Unknown')),
    travel_party_type    VARCHAR(30)
                         CHECK (travel_party_type IS NULL OR travel_party_type IN (
                             'Solo','Couple','Family','Friends'
                         )),
    trip_purpose         VARCHAR(30)
                         CHECK (trip_purpose IS NULL OR trip_purpose IN ('Leisure','Business'))
);
CREATE UNIQUE INDEX UQ_D_TRAVEL_SEGMENT_NK ON D_TRAVEL_SEGMENT (travel_segment_code);

-- ---------------------------------------------------------------------
-- D_REVIEW  (Table 15)
-- Versioned dimension. Each version of an edited review is its own
-- row with its own platform_review_id; review_group_id ties versions
-- together and is_edit marks which row is the revision.
-- ---------------------------------------------------------------------
CREATE TABLE D_REVIEW (
    review_key           INTEGER PRIMARY KEY,
    platform_review_id   VARCHAR(50) NOT NULL,          -- NK
    travel_segment_key   INTEGER NOT NULL,              -- FK -> D_TRAVEL_SEGMENT
    review_group_id      VARCHAR(50) NOT NULL,
    is_edit              BOOLEAN NOT NULL CHECK (is_edit IN (0,1)),
    review_text          TEXT NOT NULL,
    star_rating          DECIMAL(2,1)
                         CHECK (star_rating IS NULL OR star_rating BETWEEN 1 AND 5),
    review_language      VARCHAR(10),
    FOREIGN KEY (travel_segment_key) REFERENCES D_TRAVEL_SEGMENT (travel_segment_key)
);
CREATE UNIQUE INDEX UQ_D_REVIEW_NK ON D_REVIEW (platform_review_id);
CREATE INDEX IDX_D_REVIEW_GROUP ON D_REVIEW (review_group_id);

-- ---------------------------------------------------------------------
-- D_PLATFORM  (Table 16)
-- SCD Type 1. Flat enumeration of sources, no hierarchy.
-- ---------------------------------------------------------------------
CREATE TABLE D_PLATFORM (
    platform_key       INTEGER PRIMARY KEY,
    platform_code      VARCHAR(30) NOT NULL,            -- NK
    platform_name      VARCHAR(100) NOT NULL,
    platform_type      VARCHAR(50) NOT NULL
                       CHECK (platform_type IN
                           ('Review Website','Social Media','Booking Platform','Other')),
    platform_website   VARCHAR(150)
);
CREATE UNIQUE INDEX UQ_D_PLATFORM_NK ON D_PLATFORM (platform_code);

-- ---------------------------------------------------------------------
-- F_ASPECT_SENTIMENT_OBSERVATION  (Table 17)
-- Grain: one record per aspect per review.
-- The five-column UNIQUE constraint below is the database-level
-- enforcement of the deduplication rule described in the Loading
-- Phase (5.8): no two fact rows may share the same
-- (date_key, service_key, review_key, aspect_key, platform_key).
-- ---------------------------------------------------------------------
CREATE TABLE F_ASPECT_SENTIMENT_OBSERVATION (
    sentiment_fact_key   INTEGER PRIMARY KEY,
    date_key             INTEGER NOT NULL,               -- FK -> D_DATE
    service_key          INTEGER NOT NULL,               -- FK -> D_SERVICE
    review_key           INTEGER NOT NULL,               -- FK -> D_REVIEW
    aspect_key           INTEGER NOT NULL,               -- FK -> D_ASPECT
    platform_key         INTEGER NOT NULL,               -- FK -> D_PLATFORM

    polarity_score       DECIMAL(4,3) NOT NULL CHECK (polarity_score BETWEEN -1 AND 1),
    subjectivity_score   DECIMAL(4,3) NOT NULL CHECK (subjectivity_score BETWEEN 0 AND 1),
    joy_score            DECIMAL(4,3) NOT NULL CHECK (joy_score BETWEEN 0 AND 1),
    trust_score          DECIMAL(4,3) NOT NULL CHECK (trust_score BETWEEN 0 AND 1),
    fear_score           DECIMAL(4,3) NOT NULL CHECK (fear_score BETWEEN 0 AND 1),
    surprise_score       DECIMAL(4,3) NOT NULL CHECK (surprise_score BETWEEN 0 AND 1),
    sadness_score        DECIMAL(4,3) NOT NULL CHECK (sadness_score BETWEEN 0 AND 1),
    disgust_score        DECIMAL(4,3) NOT NULL CHECK (disgust_score BETWEEN 0 AND 1),
    anger_score          DECIMAL(4,3) NOT NULL CHECK (anger_score BETWEEN 0 AND 1),
    anticipation_score   DECIMAL(4,3) NOT NULL CHECK (anticipation_score BETWEEN 0 AND 1),
    sentiment_strength   DECIMAL(4,3) NOT NULL CHECK (sentiment_strength BETWEEN 0 AND 1),
    model_confidence     DECIMAL(4,3) CHECK (model_confidence IS NULL OR model_confidence BETWEEN 0 AND 1),

    FOREIGN KEY (date_key)     REFERENCES D_DATE (date_key),
    FOREIGN KEY (service_key)  REFERENCES D_SERVICE (service_key),
    FOREIGN KEY (review_key)   REFERENCES D_REVIEW (review_key),
    FOREIGN KEY (aspect_key)   REFERENCES D_ASPECT (aspect_key),
    FOREIGN KEY (platform_key) REFERENCES D_PLATFORM (platform_key)
);
CREATE UNIQUE INDEX UQ_FACT_GRAIN
    ON F_ASPECT_SENTIMENT_OBSERVATION (date_key, service_key, review_key, aspect_key, platform_key);
