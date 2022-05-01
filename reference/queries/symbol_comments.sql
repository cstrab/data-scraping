SELECT cmt.*, COUNT(sym.symbol) AS count, AVG(mnt.sentiment) AS sentiment 
FROM getCommentsSinceSeconds(1200) cmt
INNER JOIN public.mentions AS mnt
ON cmt.id = mnt.comment_id
INNER JOIN public.symbols AS sym
ON sym.symbol = mnt.symbol
WHERE sym.symbol = 'FB'
GROUP BY cmt.id, cmt.body, cmt.created, cmt.author, cmt.submission_id
ORDER BY cmt.created DESC;