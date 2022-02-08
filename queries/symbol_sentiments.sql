SELECT * FROM (
	SELECT sym.symbol, COUNT(sym.symbol) AS count, AVG(mnt.sentiment) AS sentiment
	FROM public.symbols sym
	INNER JOIN public.mentions AS mnt
	ON sym.symbol = mnt.symbol
	INNER JOIN public.comments AS cmt
	ON cmt.id = mnt.comment_id
	WHERE cmt.created > (
		SELECT EXTRACT(epoch FROM (current_timestamp - (60 || ' seconds')::interval))
	)
	GROUP BY sym.symbol
) AS sent
ORDER BY sent.count DESC, sent.sentiment DESC;