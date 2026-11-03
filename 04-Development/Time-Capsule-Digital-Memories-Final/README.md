# Final navigation and sealed-sharing correction

**Home** in the sidebar and the logo link to `/`, the informational main page, not the capsule creator. Capsule creation remains a separate option.

**Share a sealed capsule:** Sign in as its owner, open **My capsules**, use **Share locked capsule** below its card, or open the capsule and select **Share this locked capsule**. Enter the email of **another user who already registered on this same installation**. That account sees the sealed capsule in **Shared with me**, but cannot read its contents before the opening date. Drafts must be sealed first. A localhost app cannot be opened remotely without deployment; optional email sending needs SMTP configuration.

**Regression:** Run `python -m unittest discover -s tests -v` after installing requirements. In particular, `test_navigation_locked_share.py` catches the missing-owner-ID bug that hid the Share button in the previous build.

---

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


## Sprint 5 — Final build additions

This release retains the existing application and adds reversible administrator account controls, sharing before opening, and a queued email notification mechanism. See `docs/sprint-5-guide.md` for acceptance criteria and limitations.

**Create an admin:** Register an ordinary user through the website first. On the same computer, run:

```powershell
python -m flask --app app:create_app create-admin
```

Enter the registered account email when asked. Restart or refresh the app and sign back in. An Admin link will appear in the sidebar. Administrators can disable and restore normal accounts without destroying the original capsules.

**Configure email:** The app stores pending notifications in SQLite; it does not pretend to send messages when email is unconfigured. Set environment variables before launching:

```powershell
$env:TC_SMTP_HOST = "smtp.yourprovider.example"
$env:TC_SMTP_PORT = "587"
$env:TC_SMTP_USER = "your-smtp-account"
$env:TC_SMTP_PASSWORD = "your-app-password"
$env:TC_SMTP_FROM = "your-verified-sender@example.com"
$env:TC_PUBLIC_BASE_URL = "https://your-deployed-website.example"
```

These are placeholders, not a working server. Use your provider's actual host/credentials. Invitations are attempted immediately when a share is created. To deliver retry and **unlock-time** emails, run this command periodically (for example, every 5 minutes in Windows Task Scheduler, with the same working directory and environment):

```powershell
python -m flask --app app:create_app send-notifications
```

No continuous background worker is bundled. Access control is checked on the server even if mail runs late. Recipient accounts must already be registered. Local `127.0.0.1` URLs do not work on another device over the internet. Do not commit credentials or your instance folder to GitHub.

**Tests:** `python -m unittest discover -s tests -v`. The preparation environment lacked the installed Flask dependency and could not run the suite; test outcomes are not claimed.


## Sprint 5.1 fixes — navigation, locked sharing and account recovery

- **Home** is in the signed-in left sidebar next to **My capsules** and **Shared with me**.
- Open your own **sealed capsule**, click **Share this locked capsule**, enter the email of a user **already registered on the same installation**, then look in the recipient's **Shared with me** list. Contents remain hidden until unlock. Sharing a draft still requires sealing first.
- **Admin**: There is intentionally no universal default admin email/password. Register your chosen account, open a PowerShell terminal in the folder containing `app.py`, then run `.\.venv\Scripts\python.exe -m flask --app app:create_app create-admin` and enter that exact registered email. Sign out/in; **Admin dashboard** appears in the left navigation. Its URL is `/admin`; only admins have permission.
- **Forgot password?** appears under Sign in. For email reset links, configure the SMTP variables documented above and a reachable `TC_PUBLIC_BASE_URL`. Reset links expire after **30 minutes** and stop working after password changes. For local classroom demonstrations without email, use `.\.venv\Scripts\python.exe -m flask --app app:create_app reset-password` and follow the prompts; never share reset credentials.
- **Important**: Copy the entire `instance/` directory from your current installation into the upgraded extracted folder *before running*, to preserve accounts, capsules, uploads and signing key. Never upload `instance/` or SMTP secrets to GitHub.


## FINAL Sprint 5 release — dashboard & dual notifications

The dashboard no longer creates standalone Share cards: each capsule appears once, and the Share action is available inside its opened or sealed owner page. **Notifications** is in the left sidebar, with an unread badge. Sharing creates an in-app invitation and queues an email; opening creates one in-app and email notification for the capsule owner and each current shared recipient.

SMTP and a scheduled `send-notifications` command are required for automatic email delivery when the app is idle. Without working SMTP, mail remains queued; it cannot be guaranteed to arrive. See `docs/FINAL_RELEASE_NOTIFICATIONS.md` for the full setup, acceptance checklist, and testing instructions.

Before upgrading, **back up and copy the entire old `instance` folder** (database, uploads and `secret.key`) into the new extracted project directory. Never publish personal capsules or SMTP credentials.

The historical Sprint 4 sections above describe the previous release, not the capabilities added in Sprint 5.
