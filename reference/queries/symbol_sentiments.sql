SELECT * FROM (
	SELECT sym.symbol, COUNT(sym.symbol) AS count, AVG(mnt.sentiment) AS sentiment
	FROM public.symbols sym
	INNER JOIN public.mentions AS mnt
	ON sym.symbol = mnt.symbol
	INNER JOIN (
		SELECT * FROM getCommentsSinceSeconds(300)
    ) AS cmt
	ON cmt.id = mnt.comment_id
	WHERE sym.active
	GROUP BY sym.symbol
) AS sent
ORDER BY sent.count DESC, sent.sentiment DESC;

-- CREATE FUNCTION getCommentsSinceSeconds(s INTEGER) RETURNS SETOF comments
--    LANGUAGE plpgsql AS
-- $$DECLARE
--    unix_now INTEGER := (SELECT EXTRACT(epoch FROM (current_timestamp - (s || ' seconds')::interval))::integer);
-- BEGIN
--     RETURN QUERY
--        SELECT * FROM public.comments 
-- 		WHERE created > unix_now;
-- END;$$;