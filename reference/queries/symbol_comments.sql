SELECT cmt.*, COUNT(sym.symbol) AS count, AVG(mnt.sentiment) AS sentiment 
FROM public.comments cmt
INNER JOIN public.mentions AS mnt
ON cmt.id = mnt.comment_id
INNER JOIN public.symbols AS sym
ON sym.symbol = mnt.symbol
WHERE sym.symbol = 'FB'
AND cmt.created > (
	SELECT EXTRACT(epoch FROM (current_timestamp - (30 || ' minutes')::interval))
)
GROUP BY cmt.id
ORDER BY cmt.created DESC;
