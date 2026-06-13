from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(
    __name__,
    template_folder="templates2",
    static_folder="static2"
)

app.secret_key = "social_secret"

UPLOAD_FOLDER = "static2/slike"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


def get_db():
    conn = sqlite3.connect("db/social.db")
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
    CREATE TABLE IF NOT EXISTS posts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        image TEXT,
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

    posts = conn.execute("""
        SELECT posts.*,
               users.username
        FROM posts
        JOIN users
        ON posts.user_id = users.id
        ORDER BY posts.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "index.html",
        posts=posts
    )


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


@app.route("/create_post", methods=["GET", "POST"])
def create_post():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        text = request.form["text"]

        image = request.files["image"]

        filename = ""

        if image and image.filename != "":

            filename = image.filename

            image.save(
                os.path.join(
                    UPLOAD_FOLDER,
                    filename
                )
            )

        conn = get_db()

        conn.execute(
            """
            INSERT INTO posts(text,image,user_id)
            VALUES(?,?,?)
            """,
            (text, filename, session["user_id"])
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("create_post.html")


@app.route("/delete_post/<int:id>")
def delete_post(id):

    conn = get_db()

    conn.execute(
        """
        DELETE FROM posts
        WHERE id=?
        AND user_id=?
        """,
        (id, session["user_id"])
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    posts = conn.execute(
        """
        SELECT *
        FROM posts
        WHERE user_id=?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    conn.close()

    return render_template(
        "profile.html",
        posts=posts
    )

@app.route("/edit_post/<int:id>", methods=["GET", "POST"])
def edit_post(id):

    conn = get_db()

    if request.method == "POST":

        text = request.form["text"]

        conn.execute(
            """
            UPDATE posts
            SET text=?
            WHERE id=?
            AND user_id=?
            """,
            (text, id, session["user_id"])
        )

        conn.commit()
        conn.close()

        return redirect("/profile")

    post = conn.execute(
        """
        SELECT *
        FROM posts
        WHERE id=?
        """,
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit_post.html",
        post=post
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)