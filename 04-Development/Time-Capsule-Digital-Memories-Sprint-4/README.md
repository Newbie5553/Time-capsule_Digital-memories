# Time Capsule Digital Memories — Sprint 4

Complete cumulative Python Flask + SQLite application for local use. Includes Sprints 1–3 plus **US-19 sharing opened capsules** and **US-20 title search**.

## What is new
- Share an opened capsule with another registered account by email address.
- Separate Shared with me dashboard and read-only recipient view.
- Permission checks on every capsule, attachment and status request.
- Owner-managed recipient list and confirmed removal of access.
- Case-insensitive literal title search for owned and shared collections.
- Original author shown on shared letters; responsive search and sharing interfaces.

Drafts cannot be shared. A sealed capsule must reach its opening time before sharing. Recipients cannot edit, delete, seal or reshare it. Owners still cannot change sealed content. Removing access blocks future requests, but cannot erase downloaded copies.

## Start on Windows
1. Install Python 3.11 or newer with **Add Python to PATH** enabled.
2. Extract the ZIP completely. Open the folder containing `app.py`.
3. Double-click `start_windows.bat`. Internet is needed to install dependencies.
4. Keep that terminal window open. Visit **http://127.0.0.1:5000** in your browser.
5. Register or sign in. The database is created automatically on first launch.

Manual alternative from Command Prompt in this folder:
```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```
If `py` is unavailable, use `python` for the first command. For macOS/Linux:
```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

## Upgrade from Sprint 3 without losing memories
1. Stop the old app with Ctrl+C. Keep a backup of the entire old project folder.
2. Extract Sprint 4 into a **new folder**.
3. Copy the entire old `instance/` folder beside Sprint 4's `app.py` BEFORE first launch.
4. Start Sprint 4. It adds `capsule_shares` without removing users, capsules or files.
5. Sign in and check your old memories and attachments. Keep the backup.

Do not run both versions against one instance folder. Copy the entire instance folder, including database, uploads and secret.key. Keep the same database filename `time_capsule_digital_memories.db`. Earlier supplied Sprint 1/2 schemas are also upgraded additively; the separate original prototype schema is not supported. Existing legacy single-database filename migration is retained. Do not merge two different instance folders or delete a database to troubleshoot.

## Try Sprint 4 with three accounts
1. Register owner, recipient and unrelated test accounts on this same installation.
2. As owner, create a draft with a title, letter and photo. Seal it using **In 2 minutes**, then wait until it opens.
3. Choose **Share this memory**. Enter the recipient's registered email.
4. Sign out and sign in as recipient, or use a second browser profile. Open **Shared with me** and read/download the memory.
5. Confirm the recipient has no edit, delete or reshare controls. An unrelated account cannot open the same link.
6. As owner, open sharing again, tick **Confirm removal**, then **Remove access**. The recipient's next page/file request is denied.
7. Use title search; try mixed case, no matching text, and Clear.

## Sharing on a local computer
Recipients must have accounts in this app's database. No invitation email is sent. The server binds to 127.0.0.1, so use sign-out/sign-in or separate browser profiles on the same computer to demonstrate. Sending a localhost URL to another computer does not give it access. Public hosting is not included.

## Tests
```bat
.venv\Scripts\python.exe -m unittest discover -s tests -v
```
See `docs/testing-report.md` and `docs/test-results.txt` for automated execution evidence. Run the manual Windows/browser checklist on your computer as well.

## Limits and next sprint
Notifications and password recovery are not implemented. There is no email verification, rate limiting or production hosting. Files are private at the app level, not encrypted at rest. Local file/database access or changing the server clock bypasses time-lock assumptions. Downloads are not malware-scanned; only basic supported format headers are checked. Search scans the current user's collection and is suitable for the small local demonstration, not a large hosted database.

## Documentation and GitHub
- `docs/sprint-4-guide.md`: developer explanation and demonstration.
- `docs/diagrams/`: Sprint 4 sequence diagrams and editable sources.
- `docs/scrum/`: goal, backlog, acceptance criteria, review and retrospective templates.
- `docs/github-upload.md`: team upload responsibilities and target paths.

Earlier sprint guides describe their historical release scope. This README and Sprint 4 guide describe the current release. Upload extracted source, tests, templates, static assets and docs. Keep .gitignore; never upload instance/, .venv/, credentials or __pycache__/.
