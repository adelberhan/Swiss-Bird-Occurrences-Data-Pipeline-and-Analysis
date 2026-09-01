WITH issue_aggregation AS (

    SELECT
        _DLT_PARENT_ID AS dlt_parent_id,
        ARRAY_AGG(VALUE) AS issues

    FROM {{ source('raw_data', 'OCCURRENCES_RAW__ISSUES') }}

    GROUP BY _DLT_PARENT_ID
)

SELECT
    s.occurrence_key,

    s.species_key,
    s.dataset_key,

    s.event_date,
    s.year,
    s.month,
    s.day,

    s.decimal_latitude,
    s.decimal_longitude,
    s.coordinate_uncertainty_m,

    s.country_code,

    s.basis_of_record,

    s.occurrence_status,

    s.media_url,

    CASE
        WHEN s.media_url IS NOT NULL
             AND TRIM(s.media_url) != ''
        THEN TRUE
        ELSE FALSE
    END AS has_media,

    i.issues

FROM {{ ref('stg_occurrences') }} AS s

LEFT JOIN issue_aggregation AS i
    ON s.dlt_id = i.dlt_parent_id