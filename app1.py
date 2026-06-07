from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(
    __name__,
    template_folder="templates1",
    static_folder="static1"
)

app.secret_key = "skrivni_kljuc"


def get_db():
    conn = sqlite3.connect("db/notes.db")
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
    CREATE TABLE IF NOT EXISTS notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
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

    notes = conn.execute(
        "SELECT * FROM notes WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template("index.html", notes=notes)


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
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
            "SELECT * FROM users WHERE username=? AND password=?",
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


@app.route("/add", methods=["POST"])
def add():

    title = request.form["title"]
    content = request.form["content"]

    conn = get_db()

    conn.execute(
        "INSERT INTO notes(title,content,user_id) VALUES(?,?,?)",
        (title, content, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM notes WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_db()

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"]

        conn.execute(
            "UPDATE notes SET title=?, content=? WHERE id=?",
            (title, content, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    note = conn.execute(
        "SELECT * FROM notes WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_note.html",
        note=note
    )


@app.route("/search")
def search():

    q = request.args.get("q")

    conn = get_db()

    notes = conn.execute(
        """
        SELECT * FROM notes
        WHERE user_id=?
        AND title LIKE ?
        """,
        (session["user_id"], f"%{q}%")
    ).fetchall()

    conn.close()

    result = []

    for note in notes:
        result.append({
            "id": note["id"],
            "title": note["title"]
        })

    return jsonify(result)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)