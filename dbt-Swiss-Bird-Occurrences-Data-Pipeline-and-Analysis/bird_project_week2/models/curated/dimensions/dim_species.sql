WITH ranked_species AS (
    SELECT
        species_key,
        accepted_scientific_name,
        species_name,
        kingdom,
        taxon_class,
        taxon_order,
        family,
        genus,
        taxon_rank,
        taxonomic_status,
        ROW_NUMBER() OVER(
            PARTITION BY species_key
            ORDER BY
                CASE
                    WHEN taxonomic_status = 'ACCEPTED' THEN 1
                    ELSE 2
                END,
                accepted_scientific_name,
                species_name
        ) as row_num
    from  {{ ref('stg_occurrences') }}
    WHERE
        species_key IS NOT NULL
)
SELECT
    species_key,
    accepted_scientific_name,
    species_name,
    kingdom,
    taxon_class,
    taxon_order,
    family,
    genus,
    taxon_rank,
    taxonomic_status
FROM ranked_species
WHERE
    row_num = 1