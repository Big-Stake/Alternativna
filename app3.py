from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(
    __name__,
    template_folder="templates3",
    static_folder="static3"
)

app.secret_key = "task_secret"


def get_db():
    conn = sqlite3.connect("db2/tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        priority TEXT,
        status TEXT,
        user_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    status = request.args.get("status")

    if status:

        tasks = conn.execute(
            """
            SELECT * FROM tasks
            WHERE user_id=?
            AND status=?
            ORDER BY id DESC
            """,
            (session["user_id"], status)
        ).fetchall()

    else:

        tasks = conn.execute(
            """
            SELECT * FROM tasks
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

    conn.close()

    return render_template(
        "index.html",
        tasks=tasks
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        try:

            conn.execute(
                """
                INSERT INTO users(username,password)
                VALUES(?,?)
                """,
                (username, password)
            )

            conn.commit()

        except:
            pass

        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username=?
            AND password=?
            """,
            (username, password)
        ).fetchone()

        conn.close()

        if user:

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


@app.route("/add_task", methods=["GET", "POST"])
def add_task():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        priority = request.form["priority"]

        conn = get_db()

        conn.execute(
            """
            INSERT INTO tasks(
                title,
                description,
                priority,
                status,
                user_id
            )
            VALUES(?,?,?,?,?)
            """,
            (
                title,
                description,
                priority,
                "V teku",
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("add_task.html")


@app.route("/delete_task/<int:id>")
def delete_task(id):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM tasks
        WHERE id=?
        """,
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    conn = get_db()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        priority = request.form["priority"]

        conn.execute(
            """
            UPDATE tasks
            SET title=?,
                description=?,
                priority=?
            WHERE id=?
            """,
            (title, description, priority, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    task = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE id=?
        """,
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_task.html",
        task=task
    )


@app.route("/change_status/<int:id>", methods=["POST"])
def change_status(id):

    conn = get_db()

    task = conn.execute(
        """
        SELECT *
        FROM tasks
        WHERE id=?
        """,
        (id,)
    ).fetchone()

    new_status = "Končano"

    if task["status"] == "Končano":
        new_status = "V teku"

    conn.execute(
        """
        UPDATE tasks
        SET status=?
        WHERE id=?
        """,
        (new_status, id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "status": new_status
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5002)