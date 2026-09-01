SELECT
    "KEY" AS occurrence_key,
    TO_VARCHAR(DATASET_KEY) AS dataset_key,
    LAST_INTERPRETED AS last_interpreted,

    TO_VARCHAR(ACCEPTED_SCIENTIFIC_NAME) AS accepted_scientific_name,
    SPECIES_KEY AS species_key,
    TO_VARCHAR(SPECIES) AS species_name,

    TO_VARCHAR(KINGDOM) AS kingdom,
    TO_VARCHAR(CLASS) AS taxon_class,
    TO_VARCHAR("ORDER") AS taxon_order,
    TO_VARCHAR(FAMILY) AS family,
    TO_VARCHAR(GENUS) AS genus,

    TO_VARCHAR(TAXON_RANK) AS taxon_rank,
    TO_VARCHAR(TAXONOMIC_STATUS) AS taxonomic_status,

    TO_DATE(EVENT_DATE) AS event_date,
    YEAR AS year,
    MONTH AS month,
    DAY AS day,

    DECIMAL_LATITUDE AS decimal_latitude,
    DECIMAL_LONGITUDE AS decimal_longitude,
    COORDINATE_UNCERTAINTY_IN_METERS AS coordinate_uncertainty_m,

    TO_VARCHAR(COUNTRY_CODE) AS country_code,
    TO_VARCHAR(BASIS_OF_RECORD) AS basis_of_record,
    TO_VARCHAR(OCCURRENCE_STATUS) AS occurrence_status,

    TO_VARCHAR(MEDIA_URL) AS media_url,

    TO_VARCHAR(_DLT_ID) AS dlt_id

FROM {{ source('raw_data', 'OCCURRENCES_RAW') }}