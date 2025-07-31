from flask import Flask, render_template, request
import psycopg2
import os

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('index.html', tables=tables)

@app.route('/view')
def view_table():
    table = request.args.get('table')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table};")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return render_template('view.html', table=table, colnames=colnames, rows=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
