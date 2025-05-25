-- Top 5 most popular artists streamed by folks in Germany
SELECT
    a.name,
    COUNT(*) AS stream_count
FROM events e
JOIN users u ON e.user_id = u.user_id
JOIN songs s ON e.song_id = s.id
JOIN artists a ON s.artist_id = a.id
WHERE u.country = 'Germany'
GROUP BY a.name
ORDER BY stream_count DESC
LIMIT 5;