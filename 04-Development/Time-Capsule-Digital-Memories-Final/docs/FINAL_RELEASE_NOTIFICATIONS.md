# Final Sprint – Notification and UI acceptance criteria

## Dashboard
- Each saved capsule produces **one** capsule card in the collection grid. No standalone Share tiles.
- Owner sharing remains within the sealed or opened capsule page; drafts must be sealed first.
- Home points to the introduction at `/`; My capsules points to `/dashboard`.

## In-app events
- Sharing a capsule with a registered account creates an immediate invitation in that recipient’s **Notifications** inbox.
- At or after the unlock time, the owner and each currently shared recipient receive exactly one **ready to open** in-app notification.
- Opening-time notices are generated on app requests and by the scheduled notification command. They are retained in the database, deduplicated, and can be marked read.
- Revoked recipients cannot see or open the capsule; their associated notifications are removed upon revocation.

## Email delivery
- Sharing attempts an invitation email immediately. A failed or unconfigured SMTP server leaves it queued for retry.
- At unlock, the scheduled command processes all due capsules and sends opening email to owners and shared recipients.
- **A scheduled job is necessary** to send unlock emails at the due time when nobody is using the site. With no job, mail is only sent upon manual command or when the app explicitly attempts delivery.
- Configure `TC_SMTP_HOST`, `TC_SMTP_PORT`, `TC_SMTP_USER`, `TC_SMTP_PASSWORD`, `TC_SMTP_FROM`, and `TC_PUBLIC_BASE_URL` for a real deployment.
- A local-only website address is not reachable by email recipients outside that computer. For another device use a securely deployed HTTPS URL.
- Before demonstrating real email, use two registered test accounts, a real configured SMTP server, and verify Inbox/Spam on both addresses.

## Windows scheduler (run every minute)
From PowerShell in the extracted project directory, with environment variables configured for the scheduler account:

```powershell
.\.venv\Scripts\python.exe -m flask --app app:create_app send-notifications
```

For automatic scheduled delivery, set up a Windows Task Scheduler task with an **absolute path** to `.venv\Scripts\python.exe`, arguments `-m flask --app app:create_app send-notifications`, and **Start in** the project directory. Repeat every minute, under a user account with SMTP environment settings and write permissions to `instance`. Keep credentials out of task arguments and version control.

## Verification
Run `python -m unittest discover -s tests -v` in the app's installed virtual environment. In particular `tests/test_final_notifications.py` tests card count, owner/recipient unlock notices, mocked SMTP sends, duplicate suppression, and notification ownership. Check the other existing tests as well.
