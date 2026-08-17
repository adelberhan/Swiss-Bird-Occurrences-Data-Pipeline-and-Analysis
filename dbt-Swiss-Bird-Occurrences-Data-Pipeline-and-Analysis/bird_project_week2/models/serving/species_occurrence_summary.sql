SELECT
    species_key,
    count(*) as occurrence_count,
    MIN(event_date) as first_observed,
    MAX(event_date) as last_observed,
    COUNT(DISTINCT dataset_key) as dataset_count,
    ROUND(
        100.0 * COUNT_IF(
            DECIMAL_LATITUDE IS NOT NULL
            AND DECIMAL_LONGITUDE IS NOT NULL
        ) / COUNT(*),
        2
    ) as percentage_observed
FROM
    {{ ref('stg_occurrences') }}
WHERE
    species_key IS NOT NULL
GROUP BY
    species_key