import sqlite3
#import jinja2
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
import os

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# List of note titles
list = []

# Append note titles from a a database into a list of these note titles
db = sqlite3.connect('books.db')
cur = db.cursor()
notes = cur.execute("SELECT title FROM notes")
db.commit()
output = cur.fetchall()
for note in output:
    list.append(note[0])
db.close()

@app.route("/", methods=["GET", "POST"])
def start():
    if not session.get("name"):
        return redirect("/login")
    name = session.get("name")
    return render_template("index.html", name=name)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["name"] = request.form.get("surname")
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if not session.get("name"):
        return redirect("/login")
    if request.method == "POST":
        session["bg"] = request.form.get("header_1")
    return render_template("settings.html")


@app.route("/books", methods=["GET", "POST"])
def books():
    if not session.get("name"):
        return redirect("/login")
    return render_template("books.html")


@app.route("/library", methods=["GET", "POST"])
def library():
    if not session.get("name"):
        return redirect("/login")
    # Get books from the database to display in a library
    db = sqlite3.connect('books.db')
    cur = db.cursor()
    books = cur.execute("SELECT rowid, * FROM books")
    db.commit()
    return render_template("library.html", books=books)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    if not session.get("name"):
        return redirect("/login")
    # Get data about a book from a form
    title = request.form.get("title")
    author = request.form.get("author")
    params = (title, author)
    # Add this book to the database
    db = sqlite3.connect('books.db')
    cur = db.cursor()
    cur.execute("INSERT INTO books(title, author) VALUES (?,?)", params)
    db.commit()
    db.close()
    return redirect("/library")


@app.route("/remove_book", methods=["GET", "POST"])
def remove_book():
    # Get id of a removing book
    id = request.form.get("id")
    if id:
        # Remove a book from the database
        db = sqlite3.connect('books.db')
        cur = db.cursor()
        cur.execute("DELETE FROM books WHERE rowid = (?)", id)
        db.commit()
    return redirect("/library")

@app.route("/save_note", methods=["GET", "POST"])
def save_note():
    # Get data about a note from the form
    text = request.form.get("text")
    title = request.form.get("note_title")
    title = title.strip()

    # Update datebase
    db = sqlite3.connect('books.db')
    cur = db.cursor()
    cur.execute("INSERT INTO notes(title) VALUES(?)", (title,))
    db.commit()
    db.close()

    # If a note with given title does not exist yet, add it to the list of notes
    if title not in session.get("list"):
        session.get("list").append(title)

    # Write given text into the file
    file = open("notes/" + title + ".odt", "w")
    file.write(text)
    file.close()
    return redirect("/notes")


@app.route("/notes", methods=["GET", "POST"])
def notes():
    # when I want to go to notes through a button in main menu (start.html)
    if request.method == "GET":
        # Always update a session of notes
        session["list"] = list
        return render_template("notes.html")


@app.route("/load_note", methods=["GET", "POST"])
def load_note():
    # which note to lead?
    if request.form.get("get_title"):
        title = request.form.get("get_title")
        file = open("notes/" + title + ".odt")
        content = file.read()
        file.close()
        return render_template("notes.html", title=title, content=content)
    return render_template("notes.html")

@app.route("/delete_note", methods=["GET", "POST"])
def delete_notes():
    # Which note to remove?
    delete_title = request.form.get("delete_title")

    # Remove a file of that note
    os.remove("notes/" + delete_title + ".odt")

    # Remove a note from a session
    list.remove(delete_title)
    session["list"] = list

    # Remove a note from database
    db = sqlite3.connect('books.db')
    cur = db.cursor()
    cur.execute("DELETE FROM notes WHERE title = ?", (delete_title,))
    db.commit()
    db.close()
    return redirect("/notes")

@app.route("/to_do_list", methods=["GET", "POST"])
def to_do_list():
    return render_template(to_do_list.html)