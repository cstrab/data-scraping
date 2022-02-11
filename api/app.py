from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

import config as cfg


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

connection = psycopg2.connect(
    database=cfg.DATABASE_NAME,
    user=cfg.DATABASE_USER,
    password=cfg.DATABASE_PASSWORD,
    host=cfg.DATABASE_HOST,
    port=cfg.DATABASE_PORT
)
# cursor = connection.cursor()
print(f"Connected to {cfg.DATABASE_NAME} as {cfg.DATABASE_USER}.")


@app.route('/api/mentions')
def get_mentions():
    minutes = int(request.args.get('minutes')) if request.args.get('minutes') is not None else 60
    limit = int(request.args.get('limit')) if request.args.get('limit') is not None else 20
    data = query_mentions(minutes, limit)
    if data is None:
        return "Failed to get mentions.", 500
    return jsonify(data)


def query_mentions(minutes: int, limit: int):
    if cfg.DEBUG:
        print("Getting mentions...")
    
    try:
        sql = """SELECT * FROM (
            SELECT sym.symbol, COUNT(sym.symbol) AS count, AVG(mnt.sentiment) AS sentiment
            FROM public.symbols sym
            INNER JOIN public.mentions AS mnt
            ON sym.symbol = mnt.symbol
            INNER JOIN public.comments AS cmt
            ON cmt.id = mnt.comment_id
            WHERE cmt.created > (
                SELECT EXTRACT(epoch FROM (current_timestamp - (%s || ' minutes')::interval))
            )
            GROUP BY sym.symbol
        ) AS sent
        ORDER BY sent.count DESC, sent.sentiment DESC
        LIMIT %s;"""
        cursor = connection.cursor()
        cursor.execute(sql, (minutes, limit,))
        results = cursor.fetchall()
        mentions = [
            {
                "symbol": result[0],
                "count": result[1],
                "sentiment": float(result[2])
            }
            for result in results
        ]
        return mentions
    except Exception as exp:
        print(f"Error getting mentions: {exp}")


@app.route('/api/symbols/<symbol>/comments')
def get_comments(symbol):
    minutes = int(request.args.get('minutes')) if request.args.get('minutes') is not None else 60
    data = query_comments(symbol, minutes)
    if data is None:
        return "Failed to get comments.", 500
    return jsonify(data)


def query_comments(symbol: str, minutes: int):
    if cfg.DEBUG:
        print(f"Getting comments for {symbol} since {minutes} minutes...")
    
    try:
        sql = """SELECT cmt.*, COUNT(sym.symbol) AS count, AVG(mnt.sentiment) AS sentiment 
        FROM public.comments cmt
        INNER JOIN public.mentions AS mnt
        ON cmt.id = mnt.comment_id
        INNER JOIN public.symbols AS sym
        ON sym.symbol = mnt.symbol
        WHERE sym.symbol = %s
        AND cmt.created > (
            SELECT EXTRACT(epoch FROM (current_timestamp - (%s || ' minutes')::interval))
        )
        GROUP BY cmt.id
        ORDER BY cmt.created DESC;"""
        cursor = connection.cursor()
        cursor.execute(sql, (symbol, minutes,))
        results = cursor.fetchall()
        mentions = [
            {
                "id": result[0],
                "submission_id": result[1],
                "body": result[2],
                "author": result[3],
                "created": int(result[4]),
                "count": int(result[5]),
                "sentiment": float(result[6]),
            }
            for result in results
        ]
        return mentions
    except Exception as exp:
        print(f"Error getting comments: {exp}")


if __name__ == "__main__":
    app.run(host="0.0.0.0")