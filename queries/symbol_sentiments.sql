SELECT * FROM (
	SELECT sym.symbol, COUNT(sym.symbol) AS count, AVG(mnt.sentiment) AS sentiment
	FROM public.symbols sym
	INNER JOIN public.mentions AS mnt 
	ON sym.symbol = mnt.symbol
	GROUP BY sym.symbol
) AS sent
ORDER BY sent.count DESC, sent.sentiment DESC;