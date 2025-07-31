from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "supersecretkey")  # Needed for sessions

# Login credentials from environment
VALID_USERNAME = os.environ.get("LOGIN_USERNAME", "admin")
VALID_PASSWORD = os.environ.get("LOGIN_PASSWORD", "password")

def get_db_connection():
    return psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        database=os.environ['POSTGRES_DB'],
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD']
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return render_template('index.html', tables=tables)

@app.route('/view')
def view_table():
    if 'user' not in session:
        return redirect(url_for('login'))

    table = request.args.get('table')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table};")
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    # Preprocess for Jinja (zip)
    zipped_rows = [[(val, colnames[i]) for i, val in enumerate(row)] for row in rows]

    return render_template('view.html', table=table, colnames=colnames, zipped_rows=zipped_rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
