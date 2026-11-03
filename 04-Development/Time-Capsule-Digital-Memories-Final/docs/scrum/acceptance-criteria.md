# Sprint 4 acceptance criteria

## US-19
- Owner can share only a sealed capsule whose opening time has arrived.
- Registered recipient email is required; invalid, unknown, own and duplicate emails are rejected.
- Recipient sees the capsule in Shared with me and can read/download it.
- Recipient cannot edit, delete, reseal or reshare the capsule.
- An unrelated account cannot read content, files, status or the recipient list.
- Owner can remove access with confirmation; future requests then fail.
- Existing users, capsules and attachments survive upgrade and restart.

## US-20
- Search own capsule titles without regard to case; leading/trailing query spaces are ignored.
- Empty query restores all owned capsules; no match produces a clear empty state.
- Search never discloses another account's private capsules.
- Percent and underscore are matched literally; query length is limited to 100 characters.
- Shared search separately restricts results to explicit, currently available shares.

Automated evidence: docs/test-results.txt. Actual Windows/browser results, verifier, review date and final status: pending team entry.
