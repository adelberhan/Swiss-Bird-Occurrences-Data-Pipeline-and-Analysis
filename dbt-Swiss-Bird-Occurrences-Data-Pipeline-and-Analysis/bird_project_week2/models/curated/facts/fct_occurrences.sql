SELECT
    occurrence_key,

    species_key,

    dataset_key,

    event_date,
    year,
    month,
    day,

    decimal_latitude,
    decimal_longitude,
    coordinate_uncertainty_m,

    country_code,

    basis_of_record,

    occurrence_status,

    media_url,

    CASE
        WHEN media_url IS NOT NULL
             AND TRIM(media_url) != ''
        THEN TRUE
        ELSE FALSE
    END AS has_media,

    issues

FROM {{ ref('stg_occurrences') }}