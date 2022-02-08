from flask import Flask, jsonify
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
cursor = connection.cursor()
print(f"Connected to {cfg.DATABASE_NAME} as {cfg.DATABASE_USER}.")


@app.route('/api/mentions')
def hello_world():
    data = get_mentions(60, 20)
    if data is None:
        return "Failed to get mentions.", 500
    return jsonify(data)


def get_mentions(minutes: int, limit: int):
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


if __name__ == "__main__":
    app.run()