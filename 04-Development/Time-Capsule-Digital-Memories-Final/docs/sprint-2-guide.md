# Sprint 2 developer guide

## Goal
Users can create private capsule drafts, add memories, and edit or delete drafts.

## Changed and new files
| File | Change |
|---|---|
| app.py | Adds capsule/attachment tables; draft list, create/edit, preview, download and delete routes; upload validation and ownership checks. |
| templates/base.html | Loads JavaScript and adds Create a capsule navigation. |
| templates/welcome.html | Describes draft functionality now available. |
| templates/dashboard.html | Lists the current user's saved drafts, cover colors and attachment counts. |
| templates/editor.html | New title/message form, attachments and cover choices. |
| templates/capsule.html | New draft preview, download links and edit/delete actions. |
| templates/delete_capsule.html | New confirmation page; GET never deletes data. |
| static/style.css | Adds Sprint 2 form and confirmation styles in readable blocks. |
| static/app.js | New upload filename feedback and selection-size/count checks. |
| tests/test_accounts.py | Keeps account checks and updates future-feature expectation. |
| tests/test_capsules.py | Adds draft, upload, permission, failure and upgrade checks. |
| README.md | Describes startup, upgrade and current features. |

Unchanged files such as auth.html, icons.html, requirements.txt and the launcher are included so the ZIP runs on its own.

## What to explain
- `owned_capsule()` checks the signed-in user owns a capsule before any access.
- `edit_capsule()` handles both new drafts and edits. It validates title/message/cover, checks uploads, and saves changes to SQLite.
- `identify_upload()` checks both extension and basic file header.
- Random filenames prevent one upload overwriting another. Original names are kept only for downloads.
- `dashboard()` retrieves only the user's drafts, including attachment counts.
- `download_attachment()` checks ownership before sending a file from the private upload directory.
- `delete_capsule()` first shows a confirmation page, then deletes only on a confirmed POST with a valid CSRF token.
- Database changes are additive so Sprint 1 accounts remain intact.

## Demonstration
1. Sign in with an existing account.
2. Create a capsule with title/message, one image and a short video.
3. Pick a cover and save.
4. Open the draft from the dashboard and download an attachment.
5. Edit its message and cover. Show that previous attachments remain.
6. Choose Delete draft; cancel once to show nothing is deleted.
7. Choose Delete again and confirm; show it is removed from the dashboard.
8. Explain the owner-only access tests and show the test results.

## Acceptance criteria
| Feature | Expected result |
|---|---|
| Create | Valid title/message saves and appears on the dashboard. |
| Upload | Supported headers/extensions accepted; invalid files, excess attachments and oversized requests rejected. |
| Edit | Only the owner can edit; existing files remain attached. |
| Cover | Chosen cover persists on preview and dashboard. |
| Delete | Confirmation needed; database records and files removed. |
| Ownership | Another account cannot list, read, edit, delete or download the draft. |
| Upgrade | Existing Sprint 1 account can sign in and create drafts after table creation. |

## Remaining manual checks
Windows launcher and browser visual QA must be verified on your computer. Check narrow/mobile layout, keyboard focus, upload feedback, real photo/video downloads, and persistence after restarting. Upload header fixtures in automated tests check routing/validation, not video playback.

## Scrum evidence
Record actual dates, meeting attendance, recordings, backlog changes, remaining effort, review feedback and retrospective actions. The package is an implementation aid, not a record of meetings your team has held.

## Automated result
23 tests passed on Python 3.12 / Flask 3.1.2 in Linux: 10 account/regression checks and 13 draft/upload/upgrade checks. The disk-full case deliberately logs an error while verifying database rollback and file cleanup.
