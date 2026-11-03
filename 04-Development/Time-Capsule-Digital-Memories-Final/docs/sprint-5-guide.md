# Sprint 5 — Final Implementation and Acceptance

## Scope
- Preserve the existing Sprints 1–4 SQLite records and media.
- Add administrator / normal-user roles and immediate account disable / restore.
- Allow sharing sealed capsules before the opening date, revealing **metadata only** until the server determines access is due.
- Queue invitation emails and due-date notification emails to registered recipients.
- Complete testing and UML sequence diagrams.

## Acceptance criteria
1. Normal users cannot enter `/admin` or change account status.
2. Admin access is assigned only by the local operator CLI, not by public signup.
3. Disabling an account prevents new logins and invalidates its existing sessions on the next request.
4. Disabling a user **preserves** all data and files; the administrator can restore the account.
5. A sealed capsule can be shared with a registered user who sees its title / unlock date but not its message or files.
6. Invitation messages are queued once per recipient; actual delivery requires SMTP configuration.
7. Unlock email is delivered at or after the unlock time only when the scheduled notification command runs.
8. Removing sharing access prevents future capsule / file reads and causes pending notifications to be skipped.
9. Earlier sprint data remains available following the additive migration.

## Limitations
- Email links work outside the host computer only when `TC_PUBLIC_BASE_URL` points to a reachable deployed website. A local `127.0.0.1` link cannot be opened remotely.
- Email requires a real SMTP server and scheduler. This ZIP does not include SMTP credentials or provide an online deployment.
- Recipients must have an account before the invitation is created. No unregistered-email invitation feature is included.
- Account deactivation is reversible rather than destructive deletion to protect personal memories and linked sharing data.
- The project is educational and is not represented as production security-hardened.

## Test command
```
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

An additional `tests/test_sprint5.py` covers account permissions, deactivation, locked sharing and notification queue records. The execution environment used to prepare this archive could not install Flask, so these tests are **included but not reported as passed**.
