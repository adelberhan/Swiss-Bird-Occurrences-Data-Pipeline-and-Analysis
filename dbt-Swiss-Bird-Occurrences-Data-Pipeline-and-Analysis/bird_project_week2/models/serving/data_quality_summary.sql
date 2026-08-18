WITH issue_flags AS (

    SELECT
        occurrence_key,
        TRIM(issue.value::VARCHAR) AS issue

    FROM {{ ref('fct_occurrences') }},
    LATERAL SPLIT_TO_TABLE(issues, ',') AS issue

    WHERE issues IS NOT NULL
      AND TRIM(issues) != ''
),

issue_counts AS (

    SELECT
        issue,
        COUNT(DISTINCT occurrence_key) AS record_count

    FROM issue_flags

    GROUP BY issue
),

total_records AS (

    SELECT COUNT(*) AS total_count
    FROM {{ ref('fct_occurrences') }}
)

SELECT
    issue,
    record_count,
    ROUND(
        100.0 * record_count / total_count,
        2
    ) AS pct_of_total

FROM issue_counts
CROSS JOIN total_records
ORDER BY record_count DESC