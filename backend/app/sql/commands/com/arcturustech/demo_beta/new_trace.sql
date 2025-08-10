SELECT
    client_id,
    total_time,
    server,
    browser
FROM
    eum_entry
WHERE 
    recorded >= NOW() - INTERVAL 5 MINUTE
ORDER BY 
    total_time DESC,  -- Sorting by highest duration first
    recorded DESC    -- If durations are equal, sort by most recent start time
LIMIT 1;



SELECT *
FROM txn
JOIN eum_entry ON txn.id = eum_entry.trace_id;