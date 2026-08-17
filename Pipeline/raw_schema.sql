-- =====================================================================
-- Raw Source Schema

-- This is deliberately NOT the warehouse model. It is denormalized
-- (service and platform attributes repeated on every review row),
-- carries fields that 5.7 explicitly says get dropped, and leaves
-- several values in their raw, unstandardized form. The transformation
-- step (built next) is what turns this into the eight D_/F_ tables.
--
-- Threading: source platforms do not hand over a clean "this review
-- was edited" flag. raw_thread_id ties every capture of the same
-- review together; raw_capture_id is unique per capture; captured_at
-- lets the transformation step derive which capture is the original
-- and which are edits, by earliest timestamp per thread.
-- =====================================================================

CREATE TABLE RAW_REVIEW (
    raw_capture_id      VARCHAR(50) PRIMARY KEY,   -- unique per capture
    raw_thread_id        VARCHAR(50) NOT NULL,       -- shared across edits of the same review
    captured_at           DATETIME NOT NULL,          -- when this capture was scraped

    -- ---- platform block ----

    platform_id          VARCHAR(30) NOT NULL,
    platform_name        VARCHAR(100) NOT NULL,
    platform_url          VARCHAR(150),
    country_scope         VARCHAR(50),                

    -- ---- service block ----

    service_source_id    VARCHAR(50) NOT NULL,
    service_name          VARCHAR(150) NOT NULL,
    service_type           VARCHAR(50),
    municipality_name     VARCHAR(80),
    star_rating_official  TINYINT,                   
    price_tier_raw        VARCHAR(20),
    overall_ranking        INTEGER,                    
    photo_count             INTEGER,                    

    -- ---- review block ----

    review_title           VARCHAR(150),               
    review_text             TEXT NOT NULL,
    star_rating_reviewer  DECIMAL(2,1),
    language_raw            VARCHAR(10),

    -- ---- reviewer / trip block ----

    reviewer_nationality  VARCHAR(60),
    reviewer_age_group     VARCHAR(20),
    reviewer_gender         VARCHAR(20),
    trip_type_raw            VARCHAR(50),
    trip_purpose_raw       VARCHAR(30)
);

CREATE INDEX IDX_RAW_REVIEW_THREAD ON RAW_REVIEW (raw_thread_id);
CREATE INDEX IDX_RAW_REVIEW_SERVICE ON RAW_REVIEW (service_source_id);
CREATE INDEX IDX_RAW_REVIEW_PLATFORM ON RAW_REVIEW (platform_id);

-- =====================================================================
-- Aspect detection dictionary (5.7.4, third rule)
-- Not part of D_ASPECT and not loaded into the warehouse. Used only
-- during the transformation phase to identify which aspect a fragment
-- of review text belongs to, via keyword matching against this table.
-- =====================================================================

CREATE TABLE RAW_ASPECT_KEYWORD (
    keyword          VARCHAR(50) NOT NULL,
    aspect_code     VARCHAR(30) NOT NULL,   
    PRIMARY KEY (keyword, aspect_code)
);
