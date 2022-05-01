from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

import config as cfg


def checkDbConnection(db_conn):
    try:
        with psycopg2.connect(**db_conn) as connection:
            with connection.cursor("test_connection") as cursor:
                cursor.execute("SELECT 1")
                print(f"Connected to {db_conn['database']} as {db_conn['user']}.")
    except Exception as exp:
        print(f"Failed to connect to {db_conn['database']}: {exp}")


db_conn = {
    "database": cfg.DATABASE_NAME,
    "user": cfg.DATABASE_USER,
    "password": cfg.DATABASE_PASSWORD,
    "host": cfg.DATABASE_HOST,
    "port": cfg.DATABASE_PORT
}

checkDbConnection(db_conn)


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})


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
            INNER JOIN (
                SELECT * FROM getCommentsSinceSeconds(%s)
            ) AS cmt
            ON cmt.id = mnt.comment_id
	        WHERE sym.active
            GROUP BY sym.symbol
        ) AS sent
        ORDER BY sent.count DESC, sent.sentiment DESC
        LIMIT %s;"""
        # Would it be best practice to also do this with the connection?
        with psycopg2.connect(**db_conn) as connection:
            with connection.cursor("query_mentions") as cursor:
                cursor.execute(sql, (minutes * 60, limit,))
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
        FROM getCommentsSinceSeconds(%s) cmt
        INNER JOIN public.mentions AS mnt
        ON cmt.id = mnt.comment_id
        INNER JOIN public.symbols AS sym
        ON sym.symbol = mnt.symbol
        WHERE sym.symbol =  %s
        GROUP BY cmt.id, cmt.body, cmt.created, cmt.author, cmt.submission_id
        ORDER BY cmt.created DESC;"""
        with psycopg2.connect(**db_conn) as connection:
            with connection.cursor("query_comments") as cursor:
                cursor.execute(sql, (minutes * 60, symbol,))
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