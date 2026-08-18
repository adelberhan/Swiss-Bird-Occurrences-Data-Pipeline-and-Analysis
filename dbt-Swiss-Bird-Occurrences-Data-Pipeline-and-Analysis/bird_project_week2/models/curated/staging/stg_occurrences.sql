SELECT
    TRY_TO_NUMBER(KEY) AS occurrence_key,
    TO_VARCHAR(DATASETKEY) AS dataset_key,
    LASTINTERPRETED AS last_interpreted,

    TO_VARCHAR(ACCEPTEDSCIENTIFICNAME) AS accepted_scientific_name,
    TRY_TO_NUMBER(SPECIESKEY) AS species_key,
    TO_VARCHAR(SPECIES) AS species_name,

    TO_VARCHAR(KINGDOM) AS kingdom,
    TO_VARCHAR(CLASS) AS taxon_class,
    TO_VARCHAR("ORDER") AS taxon_order,
    TO_VARCHAR(FAMILY) AS family,
    TO_VARCHAR(GENUS) AS genus,

    TO_VARCHAR(TAXONRANK) AS taxon_rank,
    TO_VARCHAR(TAXONOMICSTATUS) AS taxonomic_status,

    TRY_TO_DATE(EVENTDATE) AS event_date,
    TRY_TO_NUMBER(YEAR) AS year,
    TRY_TO_NUMBER(MONTH) AS month,
    TRY_TO_NUMBER(DAY) AS day,

    TRY_TO_DOUBLE(DECIMALLATITUDE) AS decimal_latitude,
    TRY_TO_DOUBLE(DECIMALLONGITUDE) AS decimal_longitude,
    TRY_TO_DOUBLE(COORDINATEUNCERTAINTYINMETERS) AS coordinate_uncertainty_m,

    TO_VARCHAR(COUNTRYCODE) AS country_code,
    TO_VARCHAR(BASISOFRECORD) AS basis_of_record,
    TO_VARCHAR(OCCURRENCESTATUS) AS occurrence_status,

    TO_VARCHAR(ISSUES) AS issues,
    TO_VARCHAR(MEDIA_URL) AS media_url

FROM {{ source('raw_data', 'OCCURRENCES_RAW') }}