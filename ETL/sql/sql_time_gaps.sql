-- Find shortest and longest time interval between streams for each user in Australia who signed up in March 2024 or later,
-- using only songs published by "Global Artists Songs United Company"
SELECT
    u.user_id,
    MIN(gap) AS shortest_gap_seconds,
    MAX(gap) AS longest_gap_seconds
FROM (
    SELECT
        e.user_id,
        EXTRACT(EPOCH FROM (event_time - LAG(event_time) OVER (PARTITION BY e.user_id ORDER BY event_time))) AS gap
    FROM events e
    JOIN users u ON e.user_id = u.user_id
    JOIN songs s ON e.song_id = s.id
    JOIN publishers p ON s.publisher_id = p.id
    WHERE
        u.country = 'Australia'
        AND u.signup_time >= '2024-03-01'
        AND p.name = 'Global Artists Songs United Company'
) g
WHERE gap IS NOT NULL
GROUP BY user_id;