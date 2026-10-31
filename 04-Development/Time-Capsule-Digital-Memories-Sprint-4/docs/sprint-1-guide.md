# Sprint 1 developer guide

## Goal
Users can register, log in, log out, and reach a clear personal dashboard.

## Proposed tasks and acceptance criteria
| Task | Acceptance criteria |
|---|---|
| Review welcome-page design | Introduction and working sign-in/register links are visible. |
| Review registration form | Name, email and password fields are labelled; invalid data gives a message. |
| Verify account storage | Valid registration saves a password hash; duplicate email is rejected. |
| Verify login | Correct credentials open dashboard; wrong credentials show an error. |
| Verify dashboard protection | Signed-out visitors are redirected to login. |
| Verify logout | Session cleared; dashboard no longer accessible. |
| Review responsive layout | Check 360px, tablet and desktop widths on team devices. |
| Update documentation | Record actual test output, feedback, changes and commit references. |

## Code to explain in the meeting
Start with app.py. Explain these parts in order:
1. `create_app()`: prepares Flask and its configuration.
2. `get_db()` and the users table: connect Python to SQLite and store accounts.
3. `register()`: reads form fields, validates input, hashes password and saves user.
4. `login()`: compares submitted password with stored hash and starts a session.
5. `login_required`: keeps dashboard access limited to signed-in users.
6. `logout()`: clears the session.

For frontend design, show `base.html` for shared structure, `auth.html` for forms, and `static/style.css` for colors, spacing and responsive rules. HTML templates use Jinja expressions to display the current user's name and validation messages.

## Demonstration sequence
1. Start on welcome page.
2. Register a test account.
3. Show the name and email on the dashboard.
4. Sign out and try opening /dashboard directly.
5. Try a wrong password, then the correct one.
6. Sign out and demonstrate that a duplicate registration is rejected.
7. Show test output and discuss remaining manual checks.

## Meeting and Scrum evidence
Use real dates, attendance, recordings, estimates and remaining work. This source package does not supply completed meeting records or a fabricated burndown chart. Record review findings and improvements your team makes to the supplied initial implementation.

## Validation
Automated tests cover page rendering, access protection, registration, duplicate emails, invalid inputs, password hashing and login, logout, CSRF, HTML escaping, and absence of future capsule routes.
Browser visual inspection and Windows launcher execution must be checked on the team's computer. Do not claim those checks are complete until you perform them.

Automated result for this package: 10 tests passed under Python 3.12 / Flask 3.1.2 in Linux.
