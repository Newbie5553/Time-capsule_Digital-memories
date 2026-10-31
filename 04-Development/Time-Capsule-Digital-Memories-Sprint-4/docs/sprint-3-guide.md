# Sprint 3 — Time locking and rediscovering memories

## Sprint goal
Users can choose a future opening time, seal a capsule, see its countdown, and access its message and files only after that time.

## What is new
| Feature | Behavior |
|---|---|
| Opening date/time | Select a date in browser-local time on the sealing page. It is converted to UTC for storage. |
| Seal confirmation | An explicit checkbox and submit action seal a reviewed draft. |
| Lock enforcement | Flask denies early content and file access, even through direct URLs. |
| Countdown | Days, hours, minutes and seconds are synchronized with server time. |
| Automatic availability | At or after the opening timestamp, authorized reads/downloads become available. No background job is needed. |
| Capsule states | Dashboard shows Draft, Sealed, and Ready to open. |
| Immutable memories | A sealed capsule cannot be edited, deleted or rescheduled, even after it opens. |
| Migration | Adds three columns to the Sprint 2 database while retaining accounts, drafts and uploads. |
| Launcher | Windows launcher supports either py or python and keeps errors visible. |

## Demo (about three minutes)
1. Log in and open or create a draft with a short message and photo.
2. Click Choose opening date & seal.
3. Click In 2 minutes, review the local time, tick confirmation, and seal.
4. Show the countdown. Explain that the message and files are not in the locked HTML response.
5. Show that editing/deleting is unavailable. Demonstrate a previously copied attachment URL returning an access error if useful.
6. Let the countdown finish. The page checks server status and reloads to display the message and downloads.
7. Show the dashboard's Ready to open state.

## Developer explanation
- `capsule_state()` calculates state from locked flag, opening timestamp, and server clock.
- `seal_capsule()` validates future, timezone-aware input, confirmation, ownership and CSRF.
- `view_capsule()` supplies only metadata when sealed; it never renders the message early.
- `download_attachment()` checks the same time rule independently of the web page.
- `edit_capsule()` and `delete_capsule()` reject any already sealed capsule.
- Mutating capsule requests use a SQLite write transaction before checking state, preventing an old editor tab from changing a capsule after sealing.
- `/status` returns only state and timestamps; JavaScript uses it to synchronize the countdown. Changing browser HTML or its countdown does not grant access.
- Database migration adds `locked`, `unlock_at`, and `sealed_at` only if missing.

## Scope and limits
This release includes Sprints 1, 2 and 3. Sharing, search/filter improvements and unlock notifications are for Sprint 4. Ready to open is a dashboard state, not an email notification.

On a local installation, the server clock is your computer clock. Direct database/file access or changing the server clock can bypass this educational app's time lock. Content is not encrypted at rest. Keep instance private and backed up. The application does not guarantee multi-year data preservation.

## Acceptance checklist
- Reject missing, invalid, timezone-less and past opening timestamps.
- Require confirmation and ownership before sealing.
- Prevent early reads, attachment downloads, edits, deletes and rescheduling.
- Permit reads/downloads exactly when server time reaches the opening time.
- Continue to deny access to other accounts even after opening.
- Retain Sprint 2 account and attachment data during repeated application starts.

Manual checks still needed: run the Windows launcher on your computer; verify layout and date/time choices in your browser; confirm two-minute demonstration and real media downloads. Automated Flask tests do not execute the browser's JavaScript.

## Scrum records
Add actual estimates, remaining effort, meeting dates/recordings, review results and retrospective actions. This package contains implementation and test evidence, not invented meetings or sprint progress.

## Validation results
32 automated tests passed under Python 3.12 and Flask 3.1.2: earlier account/draft checks plus 9 timed capsule tests. Python compilation and JavaScript syntax checks passed. Windows execution and visual/browser JavaScript behavior have not been verified in this environment.
