# Keepsake — Sprint 1

A separate teaching and demonstration version of the Keepsake web application. It contains the welcome page, registration, login, logout, and a basic personal dashboard.

This is an extract/adaptation of the existing working project. It is not evidence that development originally took place over historical sprints. Record your team's actual reviews, changes and testing.

## Run on Windows
1. Install Python 3.11 or newer.
2. Extract the ZIP into its own folder, separate from the full Keepsake project.
3. Double-click `start_windows.bat`.
4. Keep the terminal open and visit http://127.0.0.1:5000.
5. Register with your own account details.

Or open a terminal in this folder and run:
```
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```
For macOS/Linux use `python3 -m venv .venv`, then `.venv/bin/python` for the other commands.

Internet is required to install Flask. Stop any other app using port 5000 before starting this one. The Flask development server is intended for this local demonstration.

## Separate files and placement
| File | Purpose |
|---|---|
| app.py | Python application, SQLite accounts, validation, sessions and routes |
| templates/base.html | Shared page structure, navigation and footer |
| templates/icons.html | Reusable SVG icon macro imported by base.html |
| templates/welcome.html | Welcome page |
| templates/auth.html | Registration and login forms |
| templates/dashboard.html | Personal dashboard |
| templates/error.html | Error messages |
| static/style.css | Formatted CSS with indented blocks; shared full-project style foundation |
| requirements.txt | Flask dependency |
| start_windows.bat | Local Windows launcher |
| tests/test_accounts.py | Automated account checks |
| docs/sprint-1-guide.md | Scope, acceptance criteria, demo and code walkthrough |
| .gitignore | Excludes runtime data and environment files |

Preserve these folders exactly. Flask reads HTML from templates and CSS from static. No custom JavaScript is needed for this sprint's account forms and page navigation. The later full project has JavaScript for capsule features.

## GitHub
Upload the extracted files and folders, including .gitignore, to your repository. Do not upload only the ZIP if you want reviewers to inspect code. Do not upload `instance/`, `.venv/`, or `__pycache__/`, even when using browser drag-and-drop uploads.

Suggested honest commit message: `Add Sprint 1 account and frontend demonstration version`.
Keep your full project separately. The Sprint 1 package has its own database generated on first run.

## Tests
From this folder:
```
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Boundaries
Capsule creation, uploads, scheduling, countdowns, sharing and notifications belong to future sprints and are not active here. The dashboard states that these are coming later. Email ownership verification, password recovery, and login rate limiting are not implemented. Account data and session key are stored in the local instance folder; keep that folder private.
