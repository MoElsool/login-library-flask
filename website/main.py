import os
import re
import glob
import pymysql
import bcrypt
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    abort,
    send_from_directory,
)

load_dotenv()

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.secret_key = os.getenv("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing. Copy .env.example to .env")


def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "registration"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor,
    )


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_PASSWORD_BYTES = 72  # bcrypt rejects anything longer


def validate_title(title):
    if not title.strip():
        return "Title is required"
    if len(title) > 200:
        return "Title is too long (200 characters at most)"
    return None


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("library"))
    return redirect(url_for("login"))


# ----------------- REGISTER -----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not name:
            errors.append("Name is required")
        elif len(name) > 100:
            errors.append("Name is too long (100 characters at most)")
        if not email:
            errors.append("Email is required")
        elif len(email) > 255:
            errors.append("Email is too long (255 characters at most)")
        elif not EMAIL_RE.match(email):
            errors.append("Email format is invalid")
        if not password:
            errors.append("Password is required")
        elif len(password.encode("utf-8")) > MAX_PASSWORD_BYTES:
            errors.append("Password is too long (72 bytes at most)")
        if not confirm_password:
            errors.append("Confirm password is required")
        if password and confirm_password and password != confirm_password:
            errors.append("Passwords do not match")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("register.html", name=name, email=email)

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        conn = get_db()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s);"
                cursor.execute(sql, (email, name, password_hash))
                new_id = cursor.lastrowid
            conn.commit()

            session["user_id"] = new_id
            session["name"] = name
            return redirect(url_for("library"))
        except pymysql.err.IntegrityError as e:
            if e.args[0] == 1062:
                flash("Email Already Exists", "error")
            else:
                flash("Database error occurred", "error")
            return render_template("register.html", name=name, email=email)
        finally:
            conn.close()

    return render_template("register.html")


# ----------------- LOGIN -----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        errors = []
        if not email:
            errors.append("Email is required")
        if not password:
            errors.append("Password is required")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("login.html", email=email)

        conn = get_db()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT user_id, name, password_hash FROM users WHERE email = %s;"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

            if (
                user
                and len(password.encode("utf-8")) <= MAX_PASSWORD_BYTES
                and bcrypt.checkpw(
                    password.encode("utf-8"), user["password_hash"].encode("utf-8")
                )
            ):
                session["user_id"] = user["user_id"]
                session["name"] = user["name"]
                return redirect(url_for("library"))
            else:
                flash("Invalid email or password", "error")
                return render_template("login.html", email=email)
        finally:
            conn.close()

    return render_template("login.html")


# ----------------- LOGOUT -----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


LIBRARY_IMAGE_TYPES = {"png", "jpg", "jpeg", "webp", "gif"}
upload_dir = os.path.join(app.static_folder, "uploads")
book_dir = os.path.join(os.path.dirname(app.static_folder), "book_files")


def get_library_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_LIBRARY_NAME", "library"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor,
    )


def run_library(sql, args=(), fetch="all"):
    conn = get_library_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, args)
            if fetch == "all":
                result = cursor.fetchall()
            elif fetch == "one":
                result = cursor.fetchone()
            else:
                result = cursor.lastrowid
        conn.commit()
        return result
    finally:
        conn.close()


def image_for(kind, item_id):
    for path in glob.glob(os.path.join(upload_dir, kind, str(item_id) + ".*")):
        name = os.path.basename(path)
        return url_for(
            "static",
            filename="uploads/" + kind + "/" + name,
            v=int(os.path.getmtime(path)),
        )
    return None


def remove_image(kind, item_id):
    for path in glob.glob(os.path.join(upload_dir, kind, str(item_id) + ".*")):
        os.remove(path)


def save_image(kind, item_id, file):
    if file is None or file.filename == "":
        return
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in LIBRARY_IMAGE_TYPES:
        flash("Image was not saved. Use a png, jpg, jpeg, webp or gif file.", "error")
        return
    folder = os.path.join(upload_dir, kind)
    os.makedirs(folder, exist_ok=True)
    remove_image(kind, item_id)
    file.save(os.path.join(folder, str(item_id) + "." + ext))


def has_book_file(book_id):
    return os.path.exists(os.path.join(book_dir, str(book_id) + ".pdf"))


def remove_book_file(book_id):
    path = os.path.join(book_dir, str(book_id) + ".pdf")
    if os.path.exists(path):
        os.remove(path)


def save_book_file(book_id, file):
    if file is None or file.filename == "":
        return
    if not file.filename.lower().endswith(".pdf") or file.stream.read(5) != b"%PDF-":
        flash("Book file was not saved. Use a PDF file.", "error")
        return
    file.stream.seek(0)
    os.makedirs(book_dir, exist_ok=True)
    file.save(os.path.join(book_dir, str(book_id) + ".pdf"))


def valid_price(text):
    try:
        value = float(text)
    except ValueError:
        return False
    return 0 <= value < 100000000


def check_book(title, price, author_id, pages):
    errors = []
    if not title:
        errors.append("Title is required")
    elif len(title) > 100:
        errors.append("Title is too long (100 characters at most)")
    if not price:
        errors.append("Price is required")
    elif not valid_price(price):
        errors.append("Price must be a number, 0 or more")
    if pages and not (pages.isdigit() and 1 <= int(pages) <= 100000):
        errors.append("Pages must be a whole number between 1 and 100000")
    if not author_id:
        errors.append("Author is required")
    elif not run_library(
        "SELECT author_id FROM author WHERE author_id = %s;", (author_id,), fetch="one"
    ):
        errors.append("This author does not exist")
    return errors


def check_author(name, country):
    errors = []
    if not name:
        errors.append("Name is required")
    elif len(name) > 50:
        errors.append("Name is too long (50 characters at most)")
    if len(country) > 50:
        errors.append("Country is too long (50 characters at most)")
    return errors


@app.route("/library")
def library():
    if "user_id" not in session:
        return redirect(url_for("login"))

    books = run_library("SELECT * FROM book ORDER BY book_id;")
    authors = run_library("SELECT * FROM author ORDER BY author_id;")
    for b in books:
        b["cover"] = image_for("books", b["book_id"])
    for a in authors:
        a["photo"] = image_for("authors", a["author_id"])
    return render_template(
        "library.html", books=books, authors=authors, name=session.get("name")
    )


@app.route("/library/books/<int:book_id>")
def book_detail(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    book = run_library(
        "SELECT * FROM book WHERE book_id = %s;", (book_id,), fetch="one"
    )
    if book is None:
        abort(404)
    author = run_library(
        "SELECT * FROM author WHERE author_id = %s;", (book["author_id"],), fetch="one"
    )
    book["cover"] = image_for("books", book_id)
    return render_template(
        "book_detail.html", book=book, author=author, has_file=has_book_file(book_id)
    )


@app.route("/library/books/read/<int:book_id>")
def read_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if not has_book_file(book_id):
        abort(404)
    return send_from_directory(
        book_dir, str(book_id) + ".pdf", mimetype="application/pdf"
    )


@app.route("/library/books/add", methods=["GET", "POST"])
def add_book():
    if "user_id" not in session:
        return redirect(url_for("login"))

    authors = run_library("SELECT author_id, name FROM author ORDER BY name;")
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        price = request.form.get("price", "").strip()
        author_id = request.form.get("author_id", "")
        pages = request.form.get("pages", "").strip()
        errors = check_book(title, price, author_id, pages)
        if errors:
            for err in errors:
                flash(err, "error")
            form = {
                "title": title,
                "price": price,
                "author_id": author_id,
                "pages": pages,
            }
            return render_template(
                "book_form.html", book=form, authors=authors, editing=False
            )

        new_id = run_library(
            "INSERT INTO book (title, price, author_id, pages) VALUES (%s, %s, %s, %s);",
            (title, price, author_id, pages or None),
            fetch=None,
        )
        save_image("books", new_id, request.files.get("cover"))
        save_book_file(new_id, request.files.get("book_file"))
        flash("Book added", "success")
        return redirect(url_for("library"))

    return render_template("book_form.html", book={}, authors=authors, editing=False)


@app.route("/library/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    book = run_library(
        "SELECT * FROM book WHERE book_id = %s;", (book_id,), fetch="one"
    )
    if book is None:
        abort(404)
    authors = run_library("SELECT author_id, name FROM author ORDER BY name;")

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        price = request.form.get("price", "").strip()
        author_id = request.form.get("author_id", "")
        pages = request.form.get("pages", "").strip()
        errors = check_book(title, price, author_id, pages)
        if errors:
            for err in errors:
                flash(err, "error")
            form = {
                "book_id": book_id,
                "title": title,
                "price": price,
                "author_id": author_id,
                "pages": pages,
                "cover": image_for("books", book_id),
            }
            return render_template(
                "book_form.html",
                book=form,
                authors=authors,
                editing=True,
                has_file=has_book_file(book_id),
            )

        run_library(
            "UPDATE book SET title = %s, price = %s, author_id = %s, pages = %s WHERE book_id = %s;",
            (title, price, author_id, pages or None, book_id),
            fetch=None,
        )
        save_image("books", book_id, request.files.get("cover"))
        save_book_file(book_id, request.files.get("book_file"))
        flash("Book updated", "success")
        return redirect(url_for("library"))

    book["cover"] = image_for("books", book_id)
    return render_template(
        "book_form.html",
        book=book,
        authors=authors,
        editing=True,
        has_file=has_book_file(book_id),
    )


@app.route("/library/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    run_library("DELETE FROM book WHERE book_id = %s;", (book_id,), fetch=None)
    remove_image("books", book_id)
    remove_book_file(book_id)
    flash("Book removed", "success")
    return redirect(url_for("library"))


@app.route("/library/authors/<int:author_id>")
def author_detail(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    author = run_library(
        "SELECT * FROM author WHERE author_id = %s;", (author_id,), fetch="one"
    )
    if author is None:
        abort(404)
    books = run_library(
        "SELECT * FROM book WHERE author_id = %s ORDER BY book_id;", (author_id,)
    )
    for b in books:
        b["cover"] = image_for("books", b["book_id"])
    author["photo"] = image_for("authors", author_id)
    return render_template("author_detail.html", author=author, books=books)


@app.route("/library/authors/add", methods=["GET", "POST"])
def add_author():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        errors = check_author(name, country)
        if errors:
            for err in errors:
                flash(err, "error")
            form = {"name": name, "country": country}
            return render_template("author_form.html", author=form, editing=False)

        new_id = run_library(
            "INSERT INTO author (name, country) VALUES (%s, %s);",
            (name, country or None),
            fetch=None,
        )
        save_image("authors", new_id, request.files.get("photo"))
        flash("Author added", "success")
        return redirect(url_for("library"))

    return render_template("author_form.html", author={}, editing=False)


@app.route("/library/authors/edit/<int:author_id>", methods=["GET", "POST"])
def edit_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    author = run_library(
        "SELECT * FROM author WHERE author_id = %s;", (author_id,), fetch="one"
    )
    if author is None:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        errors = check_author(name, country)
        if errors:
            for err in errors:
                flash(err, "error")
            form = {
                "author_id": author_id,
                "name": name,
                "country": country,
                "photo": image_for("authors", author_id),
            }
            return render_template("author_form.html", author=form, editing=True)

        run_library(
            "UPDATE author SET name = %s, country = %s WHERE author_id = %s;",
            (name, country or None, author_id),
            fetch=None,
        )
        save_image("authors", author_id, request.files.get("photo"))
        flash("Author updated", "success")
        return redirect(url_for("library"))

    author["photo"] = image_for("authors", author_id)
    return render_template("author_form.html", author=author, editing=True)


@app.route("/library/authors/delete/<int:author_id>", methods=["POST"])
def delete_author(author_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    books = run_library("SELECT book_id FROM book WHERE author_id = %s;", (author_id,))
    run_library("DELETE FROM author WHERE author_id = %s;", (author_id,), fetch=None)
    for b in books:
        remove_image("books", b["book_id"])
        remove_book_file(b["book_id"])
    remove_image("authors", author_id)
    flash("Author removed together with their books", "success")
    return redirect(url_for("library"))


# ----------------- ERRORS -----------------
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(e):
    return render_template("error.html"), getattr(e, "code", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
