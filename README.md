# Lab 3: Foreign Keys and Simple SQL
## 1. Team

| Name | ID 
|------|----
| Mohamed Osama | 2304071
| Seif El-din Tarek | 2304080 

Introduction to Database Systems, Alexandria National University, Fall 2026.

This repository has the two problems of Lab 3 and the website. The website is the Lab 2 Login & To-Do application, continued with the new library pages (Problem 2).

## 1. What is in this folder

| File | What it is |
|---|---|
| problem1_DDL.sql | creates the `company` database and its tables |
| problem1_DML.sql | inserts the rows (5 employees, 3 departments, 4 projects) |
| problem1_Answers.txt | the SQL and the output for Q1.1 to Q1.3 |
| problem2_DDL.sql | creates the `library` database (AUTHOR and BOOK) |
| problem2_DML.sql | seed data (9 authors, 18 books) |
| website/ | the Lab 2 website with the new library pages |

## 2. Technology

- **Back end:** Python 3, Flask, PyMySQL (plain SQL with `%s` parameters, no ORM), bcrypt, python-dotenv
- **Front end:** HTML, CSS (own stylesheet), JavaScript
- **Database:** MySQL. Three databases are used: `company` (Problem 1), `library` (Problem 2) and `registration` (the Lab 2 users and to-dos).

## 3. How to run it (from an empty machine)

1. Install **Python 3**, **MySQL Server** and **Git**.
2. Clone the repository and open the folder:
   ```
   git clone <repository-url>
   cd <repository-folder>
   ```
3. Build the databases. Each DDL file drops and recreates its database, so these commands can be run again at any time. Run the DDL before the DML:
   ```
   mysql -u root -p < problem1_DDL.sql
   mysql -u root -p < problem1_DML.sql
   mysql -u root -p < problem2_DDL.sql
   mysql -u root -p < problem2_DML.sql
   mysql -u root -p < website/database/schema.sql
   ```
   The last line builds the `registration` database used by the login of the website.
4. Go to the website folder, create and activate a virtual environment:
   ```
   cd website
   python -m venv venv
   venv\Scripts\activate          (Windows)
   source venv/bin/activate        (Linux / macOS)
   ```
5. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Copy `.env.example` to `.env` and fill in your values (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`, `SECRET_KEY`). `DB_LIBRARY_NAME` is the name of the library database and is already set to `library`.
7. Start the server:
   ```
   python main.py
   ```
8. Open http://127.0.0.1:5000 in the browser, register a new account (or log in) and click **Library** at the top of the to-do page. The library page is also at http://127.0.0.1:5000/library.

To try the Problem 1 queries by hand: `mysql -u root -p company`.

## 4. Lab 3 features (library, Problem 2)

The library pages need a logged-in user, like the to-do list. A visitor who is not logged in is sent to the login page.

- **F2.1 Show:** `/library` shows the table of books (with the `author_id` of each book) and the table of authors.
- **Book page:** clicking a book title opens its page (cover, price, author, with Edit and Delete buttons).
- **Author page:** clicking an author name opens the page of the author (photo, country and the list of their books, each one a link to its book page).
- **Read a book:** the add and edit forms have an optional PDF upload. A book with a file shows a **Read book** button on its page, which opens the PDF in the browser (only for logged-in users). The files are saved in `website/app/book_files/` named with the id of the book, and they are deleted together with the book.
- **Pages:** each book has an optional number of pages (`pages` column in BOOK, a whole number from 1 to 100000). It is shown in the table and on the book page, and can be set when adding or editing a book.
- **F2.2 Add:** the **Add book** and **Add author** buttons. The author of a book is chosen from a list of the existing authors.
- **F2.3 Edit:** the **Edit** button on each row of both tables.
- **F2.4 Remove a book:** the **Delete** button on each book (a browser confirmation comes first).
- **F2.5 Remove an author:** the **Delete** button on each author. The books of that author are deleted too (`ON DELETE CASCADE` in the database), and the confirmation says so.
- **Checks on the server:** an empty title or name, a price that is not a number, a text that is too long and an author that does not exist are refused with a message, and the database is not touched.
- **Bonus, images:** the add and edit forms have an optional cover (books) and photo (authors). Allowed types: png, jpg, jpeg, webp, gif. The files are saved in `website/app/static/uploads/books/` and `website/app/static/uploads/authors/`, named with the id of the book or author, and they are deleted together with the row. A row without an image shows its first letter. The dark mode of Lab 2 works on the new pages too.

## 5. Lab 2 features (login and to-do)

The Lab 2 application as described in the Lab 2 report. It is unchanged, except for a **Library** link on the to-do page.

- **Register and login:** name, e-mail and password with bcrypt hashes. A duplicate e-mail shows `Email Already Exists`, a wrong login shows `Invalid email or password`.
- **Private to-do list:** add, edit, mark as done and delete, only for the logged-in user. `UPDATE` and `DELETE` always contain `AND user_id = %s`.
- **Checks in the browser and on the server**, with the exact messages of the lab.
- **Bonus:** dark mode (the button on every page) and the count of open to-dos.
