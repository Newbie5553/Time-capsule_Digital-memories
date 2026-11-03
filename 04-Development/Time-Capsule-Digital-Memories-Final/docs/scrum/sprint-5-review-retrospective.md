# Sprint 5 Review and Retrospective — Draft for Team Validation

## Review
The Sprint 5 deliverable extends the existing product with administrator account controls, locked-capsule sharing, email notifications, and updated diagrams. The previous four sprints' code and docs were retained.

## Pending demonstration
Demonstrate a registered user's capsule creation and seal action; sharing before opening; recipient's metadata-only view; unlock time transition; admin disabling and restoring an account; SMTP invitation delivery; and scheduled unlock email delivery.

## Retrospective
**What went well:** The existing project could be upgraded with database migrations rather than rewritten.
**Challenges:** Email requires external SMTP credentials and a scheduler; opening-time security must be checked on the server.
**Action items:** Run the full suite in a Flask-equipped environment, configure SMTP and the scheduler, capture screenshots, then record measured test results before calling the release accepted.

This is a documentation draft, not fabricated minutes or an assertion that the team held a meeting or completed a demo.
