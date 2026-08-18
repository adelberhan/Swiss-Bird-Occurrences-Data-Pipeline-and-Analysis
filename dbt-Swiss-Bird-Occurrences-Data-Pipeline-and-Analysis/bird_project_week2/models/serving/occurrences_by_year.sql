SELECT 
    species_key,
    year,
    COUNT(*) as occurrence_count
FROM {{ ref('stg_occurrences') }}
WHERE
    species_key IS NOT NULL
GROUP BY
    species_key,
    year