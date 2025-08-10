SELECT
    txn.trace,
    txn.client_id,
    txn.server_name,
    txn.name,
    txn.started,
    txn.duration
FROM
    txn
JOIN 
	eum_entry ON txn.id = eum_entry.trace_id
WHERE 
    recorded >= NOW() - INTERVAL {interval}
ORDER BY 
    total_time DESC,  
    recorded DESC 
LIMIT 1;
