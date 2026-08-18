SELECT
    dataset_key,

    COUNT(*) AS record_count,

    MIN(event_date) AS first_seen,

    MAX(event_date) AS last_seen

FROM {{ ref('stg_occurrences') }}

WHERE dataset_key IS NOT NULL

GROUP BY dataset_key