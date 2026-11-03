# Sprint 4 testing report

Executed during package preparation on 29 October 2026.
Environment: Python 3.12.14, Flask 3.1.2, Werkzeug 3.1.9; Linux test environment.
Command: `python -m unittest discover -s tests -v`
Result: **53 tests passed**, including **20 new Sprint 4 tests** and 33 earlier regression checks.
Python compilation and JavaScript syntax validation passed.

Coverage: owner/recipient/unrelated/anonymous access, file permissions, locked and draft sharing rejection, input validation, self/duplicate sharing, CSRF, confirmed revocation, stale sessions after revocation, time rechecks, title search scope and escaping, HTML escaping, idempotent upgrade/restart, and immutable sealed content.

The earlier draft-save failure test deliberately logs “Simulated disk full”; its expected exception handling is tested and the test passes. See raw output in test-results.txt.

## Manual checks to complete on your Windows computer
- Launch with start_windows.bat and visit http://127.0.0.1:5000.
- Create three accounts, share, read and download in another browser profile.
- Check share confirmation/removal and title search at desktop and mobile widths.
- Confirm the countdown and local date/time selection work in your browser.
- Upgrade a backed-up instance, log in and compare old memories and files.
- Record browser versions, tester, date, observed result and screenshots as needed.

Windows launcher execution is not verified in this Linux environment. Automated Flask tests do not execute browser JavaScript. Browser smoke-test result is recorded below if available.

Browser smoke test: not executed. The browser runtime download failed in this environment. Browser layout and JavaScript behavior still require the manual checks above.
