-- =====================================================================
-- Chapter 7 Evaluation Queries
-- Ten queries, each mapped to one analytical use case from Section 3.4.
-- Grouped by the same three stakeholder categories used there:
--   Strategic and Comparative Analysis    (UC1-UC4)
--   Aspect-level and Operational Analysis (UC5-UC7)
--   Affective and Segmentation Analysis   (UC8-UC10)
--
-- Each query is annotated with the OLAP operation it demonstrates
-- (slice/dice, drill-down, roll-up), consistent with the mapping
-- already established in the closing paragraph of Section 3.4.
-- =====================================================================


-- ---------------------------------------------------------------------
-- UC1: How does overall user sentiment differ between accommodation
-- services, restaurants and bars and tourist sites?
-- OLAP operation: slice and dice across service_category.
-- ---------------------------------------------------------------------
SELECT
    s.service_category,
    ROUND(AVG(f.polarity_score), 4)     AS avg_polarity,
    ROUND(AVG(f.subjectivity_score), 4) AS avg_subjectivity,
    ROUND(AVG(f.sentiment_strength), 4) AS avg_strength,
    COUNT(*)                            AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_SERVICE s ON f.service_key = s.service_key
GROUP BY s.service_category
ORDER BY avg_polarity DESC;


-- ---------------------------------------------------------------------
-- UC2: How do emotional responses expressed in user reviews vary
-- across regions and cities?
-- OLAP operation: slice and dice across the D_Location hierarchy,
-- accessed indirectly through D_Service.
-- ---------------------------------------------------------------------
SELECT
    l.region,
    l.municipality,
    ROUND(AVG(f.joy_score), 3)     AS avg_joy,
    ROUND(AVG(f.sadness_score), 3) AS avg_sadness,
    ROUND(AVG(f.anger_score), 3)   AS avg_anger,
    COUNT(*)                       AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_SERVICE s ON f.service_key = s.service_key
JOIN D_LOCATION l ON s.location_key = l.location_key
GROUP BY l.region, l.municipality
ORDER BY avg_joy DESC;


-- ---------------------------------------------------------------------
-- UC3: Which regions or cities consistently exhibit stronger positive
-- or negative emotional responses across multiple service categories?
-- OLAP operation: slice and dice, cross-tabulating region against
-- service_category to identify consistency across categories.
-- ---------------------------------------------------------------------
SELECT
    l.region,
    s.service_category,
    ROUND(AVG(f.polarity_score), 3) AS avg_polarity,
    COUNT(*) AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_SERVICE s ON f.service_key = s.service_key
JOIN D_LOCATION l ON s.location_key = l.location_key
GROUP BY l.region, s.service_category
HAVING COUNT(*) >= 10
ORDER BY l.region, s.service_category;


-- ---------------------------------------------------------------------
-- UC4: How does user sentiment evolve over time for specific service
-- categories or locations, particularly across different tourism
-- seasons?
-- OLAP operation: roll-up and drill-down along the D_Date hierarchy
-- (year, season).
-- ---------------------------------------------------------------------
SELECT
    d.year,
    d.season,
    s.service_category,
    ROUND(AVG(f.polarity_score), 3) AS avg_polarity,
    COUNT(*) AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_DATE d ON f.date_key = d.date_key
JOIN D_SERVICE s ON f.service_key = s.service_key
WHERE s.service_category = 'Accommodation'
GROUP BY d.year, d.season
ORDER BY d.year,
    CASE d.season
        WHEN 'Winter' THEN 1 WHEN 'Spring' THEN 2
        WHEN 'Summer' THEN 3 WHEN 'Autumn' THEN 4
    END;


-- ---------------------------------------------------------------------
-- UC5: Which service aspects are most frequently associated with
-- negative sentiment or negative emotions in accommodation services?
-- OLAP operation: drill-down from service-level aggregates to
-- individual aspect characteristics.
-- ---------------------------------------------------------------------
SELECT
    a.aspect_name,
    ROUND(AVG(f.polarity_score), 3)  AS avg_polarity,
    ROUND(AVG(f.anger_score), 3)     AS avg_anger,
    ROUND(AVG(f.disgust_score), 3)   AS avg_disgust,
    COUNT(*)                         AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_SERVICE s ON f.service_key = s.service_key
JOIN D_ASPECT a ON f.aspect_key = a.aspect_key
WHERE s.service_category = 'Accommodation'
GROUP BY a.aspect_name
HAVING COUNT(*) >= 5
ORDER BY avg_polarity ASC;


-- ---------------------------------------------------------------------
-- UC6: Are certain emotions more prevalent in specific types of
-- services or tourist sites?
-- OLAP operation: slice and dice across service_category, comparing
-- all eight Plutchik-aligned emotion measures simultaneously.
-- ---------------------------------------------------------------------
SELECT
    s.service_category,
    ROUND(AVG(f.joy_score), 3)          AS avg_joy,
    ROUND(AVG(f.trust_score), 3)        AS avg_trust,
    ROUND(AVG(f.fear_score), 3)         AS avg_fear,
    ROUND(AVG(f.surprise_score), 3)     AS avg_surprise,
    ROUND(AVG(f.sadness_score), 3)      AS avg_sadness,
    ROUND(AVG(f.disgust_score), 3)      AS avg_disgust,
    ROUND(AVG(f.anger_score), 3)        AS avg_anger,
    ROUND(AVG(f.anticipation_score), 3) AS avg_anticipation
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_SERVICE s ON f.service_key = s.service_key
GROUP BY s.service_category;


-- ---------------------------------------------------------------------
-- UC7: How does sentiment change following service improvements or
-- operational decisions?
--
-- NOTE: this query is architecturally supported but not empirically
-- demonstrable with the present dataset. No service in the synthetic
-- dataset has more than one SCD Type 2 version (verified: zero
-- services with multiple valid_from/valid_to windows), meaning no
-- genuine attribute change was detected during transformation. The
-- query below shows how the comparison would be expressed once
-- version history exists; it is included for architectural
-- completeness and should be discussed in Chapter 7 as a documented
-- limitation of the evaluation dataset rather than run for a result.
-- OLAP operation: drill-down across SCD Type 2 service versions.
-- ---------------------------------------------------------------------
SELECT
    s.platform_service_id,
    s.valid_from,
    s.valid_to,
    s.service_category,
    s.star_rating,
    ROUND(AVG(f.polarity_score), 3) AS avg_polarity_this_version,
    COUNT(*) AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_SERVICE s ON f.service_key = s.service_key
WHERE s.platform_service_id = 'SVC_001'   -- example: any service with >1 version
GROUP BY s.platform_service_id, s.valid_from, s.valid_to
ORDER BY s.valid_from;


-- ---------------------------------------------------------------------
-- UC8: How does the degree of subjectivity influence the
-- interpretation of aggregated sentiment trends?
-- OLAP operation: slice and dice, banding subjectivity_score into
-- ranges and comparing aggregated polarity and strength per band.
-- ---------------------------------------------------------------------
SELECT
    CASE
        WHEN f.subjectivity_score < 0.3 THEN 'Low (<0.3)'
        WHEN f.subjectivity_score < 0.6 THEN 'Medium (0.3-0.6)'
        ELSE 'High (>=0.6)'
    END AS subjectivity_band,
    ROUND(AVG(f.polarity_score), 3)     AS avg_polarity,
    ROUND(AVG(f.sentiment_strength), 3) AS avg_strength,
    COUNT(*)                            AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
GROUP BY subjectivity_band
ORDER BY MIN(f.subjectivity_score);


-- ---------------------------------------------------------------------
-- UC9: How do polarity, subjectivity and emotion interact when
-- analysing sentiment patterns across service aspects and visitor
-- segments?
-- OLAP operation: drill-down across two dimensions simultaneously
-- (D_Aspect and D_Travel_Segment, the latter accessed through
-- D_Review), demonstrating multidimensional affective analysis.
-- ---------------------------------------------------------------------
SELECT
    a.aspect_category,
    t.travel_party_type,
    ROUND(AVG(f.polarity_score), 3)     AS avg_polarity,
    ROUND(AVG(f.subjectivity_score), 3) AS avg_subjectivity,
    ROUND(AVG(f.joy_score), 3)          AS avg_joy,
    COUNT(*)                            AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_ASPECT a ON f.aspect_key = a.aspect_key
JOIN D_REVIEW r ON f.review_key = r.review_key
JOIN D_TRAVEL_SEGMENT t ON r.travel_segment_key = t.travel_segment_key
WHERE t.travel_party_type IS NOT NULL
GROUP BY a.aspect_category, t.travel_party_type
HAVING COUNT(*) >= 8
ORDER BY a.aspect_category, t.travel_party_type;


-- ---------------------------------------------------------------------
-- UC10: How does sentiment differ between solo travellers, families
-- and business travellers for the same service category?
-- OLAP operation: slice and dice across service_category, cross-
-- tabulated with travel_party_type and trip_purpose from the
-- D_Travel_Segment outrigger, accessed through D_Review.
-- ---------------------------------------------------------------------
SELECT
    s.service_category,
    t.travel_party_type,
    t.trip_purpose,
    ROUND(AVG(f.polarity_score), 3) AS avg_polarity,
    COUNT(*) AS n_observations
FROM F_ASPECT_SENTIMENT_OBSERVATION f
JOIN D_SERVICE s ON f.service_key = s.service_key
JOIN D_REVIEW r ON f.review_key = r.review_key
JOIN D_TRAVEL_SEGMENT t ON r.travel_segment_key = t.travel_segment_key
WHERE t.travel_party_type IN ('Solo', 'Family') OR t.trip_purpose = 'Business'
GROUP BY s.service_category, t.travel_party_type, t.trip_purpose
HAVING COUNT(*) >= 5
ORDER BY s.service_category;
