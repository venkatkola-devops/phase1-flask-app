from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os

app = Flask(__name__)

# -------------------------------------------------------------------
# DATABASE CONNECTION
# These values come from environment variables (set in docker-compose)
# This is the SAFE way - never hardcode passwords in code!
# -------------------------------------------------------------------
def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "db"),
        user=os.environ.get("DB_USER", "flaskuser"),
        password=os.environ.get("DB_PASSWORD", "flaskpass"),
        database=os.environ.get("DB_NAME", "flaskdb")
    )

# -------------------------------------------------------------------
# ROUTES
# A "route" is just a URL path that triggers a function
# -------------------------------------------------------------------

@app.route("/")
def index():
    """Home page - shows all tasks from the database"""
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")
    tasks = cursor.fetchall()
    conn.close()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    """Receives the form submission and saves a new task"""
    task_name = request.form.get("task")
    if task_name:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tasks (name, done) VALUES (%s, %s)", (task_name, False))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/done/<int:task_id>")
def mark_done(task_id):
    """Marks a task as completed"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET done = TRUE WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    """Deletes a task from the database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/health")
def health():
    """Health check endpoint - Jenkins uses this to verify the app is running"""
    return {"status": "healthy"}, 200

# -------------------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------------------
if __name__ == "__main__":
    # debug=False in production! Only True during local development.
    app.run(host="0.0.0.0", port=5000, debug=False)
