# Lab 2: Login & To-Do Application

Introduction to Database Systems, Alexandria National University, Fall 2026

## 1. Team

| Name | ID | Role |
|------|----|------|
| Mohamed Osama | 2304071 | Frontend & UI |
| Seif El-din Tarek | 2304080 | Backend & Database |

**Who did what**

- **Seif (Backend & Database):** set up the database connection and the `.env` file, wrote the register/login logic and the to-do routes, server-side validation, and all the database queries.
- **Mohamed (Frontend & UI):** designed the register, login and to-do pages, connected the forms to the server, wrote the client-side validation, the responsive design, and the dark mode bonus. Also did testing and bug fixing.

## 2. Technology

- **Back end:** Python 3 with Flask (Jinja templates, Flask sessions), PyMySQL (plain SQL with `%s` parameters, no ORM), bcrypt, python-dotenv
- **Front end:** HTML, CSS (own stylesheet, no framework), JavaScript
- **Database:** MySQL, database `registration` (tables `users` and `todos`)

## 3. How to run it (from an empty machine)

1. Install **Python 3**, **MySQL Server** and **Git**.
2. Clone the repository and open the project folder:
   ```
   git clone <repository-url>
   cd <project-folder>
   ```
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate          (Windows)
   source venv/bin/activate        (Linux / macOS)
   ```
4. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Build the database (note: this drops and recreates the `registration` database):
   ```
   mysql -u root -p < database/schema.sql
   ```
   (or open `database/schema.sql` in MySQL Workbench and run it)
6. Copy `.env.example` to `.env` and fill in your values (`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`, `SECRET_KEY`).
7. Start the server:
   ```
   python main.py
   ```
8. Open http://127.0.0.1:5000 in the browser.

## 4. Features

- **R1 Register:** name, e-mail, password and confirm password. A duplicate e-mail shows `Email Already Exists`. After a successful registration the user is logged in and sees the list.
- **R2 Login:** e-mail and password. A wrong e-mail and a wrong password both show `Invalid email or password`. Logout ends the session.
- **R3 Private list:** a visitor who is not logged in is redirected to the login page. A logged-in user sees only their own to-dos, newest first.
- **R4 Add** a to-do (title).
- **R5 Edit** its title.
- **R6 Mark** it done or not done (checkbox; done items are crossed out and greyed).
- **R7 Delete** it (a browser "Are you sure?" confirmation comes first).
- **R8 Checks in the browser and on the server** with the exact messages of the lab. When the server finds an error, it shows the same page again with the messages and does not touch the database.
- **R9 Security:** passwords are stored as bcrypt hashes; only the queries of the lab are used, always with parameters; the `user_id` comes from the session, never from a form.
- **R10 User interface:** one consistent style on all pages, works on a phone-sized screen (about 360 px), error messages next to the form, a visible state for done to-dos, a friendly text when the list is empty, and the user name with a logout button when logged in. Errors are shown on a styled error page (no stack traces).

**Bonus**

- **Dark mode:** a toggle button on every page; the choice is saved in the browser and the first visit follows the system theme.
- **Counting open to-dos:** the list page shows how many to-dos are still open.

## 5. Screenshots

**Register page with error messages**

**Login page**

**The list with some to-dos (one done)**

**Phone-sized window**

**Extra: validation of a too-long to-do title**

**Extra: SQL injection test (`' OR '1'='1` as the login e-mail)**


## 6. Answers

**(a) Why do `UPDATE` and `DELETE` contain `AND user_id = ?`, and what changes if you remove it?**

The id of a to-do comes from the browser, so anybody can send somebody else's number. Adding `AND user_id = ?` (the id of the logged-in user, taken from the session) makes the statement change zero rows when the to-do is not theirs. If we remove it, any logged-in user could edit, mark or delete the to-dos of other users just by changing the number in the request.

**(b) What happens if you insert a to-do for a `user_id` that does not exist, and which constraint of the lecture is that?**

MySQL refuses the insert with error 1452 (a foreign key constraint fails), and no row is added. This is the **foreign key constraint** (referential integrity): every to-do must belong to exactly one existing user.

**(c) Why do you store a hash and not the password?**

If the database is leaked or read by someone, the real passwords must not be exposed. A bcrypt hash cannot be turned back into the password, it is salted (two equal passwords give different hashes), and it is slow on purpose, which makes guessing attacks expensive. To log in, the library compares the typed password with the stored hash.

**(d) The `name` column is `NOT NULL`: why did you still need your own check for an empty name?**

`NOT NULL` only means the column must have a value. An empty text `''` (or a name of only spaces) is a value, so MySQL accepts it. Only our own checks, in the browser and on the server, can refuse an empty name and show `Name is required`.
