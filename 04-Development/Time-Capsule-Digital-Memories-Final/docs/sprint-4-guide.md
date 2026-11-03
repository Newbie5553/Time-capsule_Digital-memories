# Sprint 4 developer guide

## Sprint goal and stories
Owners can share opened memories with registered recipients, while private and locked content remains protected. US-19 implements read-only sharing. US-20 implements title search; shared-collection search and confirmed removal of access are supporting improvements.

## Code to explain
1. `capsule_shares`: additive table with capsule_id, recipient_id, created_at and a UNIQUE pair. The index supports recipient lookup. Existing Sprint 3 records are retained.
2. `owned_capsule()`: remains the guard for edit, delete, seal, share and remove-access operations. Being a recipient never grants ownership.
3. `readable_capsule()`: retrieves an owned or explicitly shared capsule. Non-owners must also pass the ready-state check. No relationship returns 404. It is used for pages, files and status reads.
4. `share_capsule()`: checks owner and opening time, validates registered email, rejects self-sharing and duplicates, stores the relationship and displays authorized recipients only to the owner.
5. `revoke_share()`: requires owner, CSRF and confirmation; deletes only the relationship belonging to that capsule. Permission is checked again on the recipient's next request.
6. `shared_capsules()`: reads metadata for the signed-in recipient; shows only ready memories. It never puts messages in list views.
7. `dashboard()`: restricts to owned capsules before using casefold() for literal title matching. `%` and `_` are not wildcards. A search is limited to 100 characters.
8. `capsule.html`: uses the owner's name as author and hides owner-only controls in the recipient view. Backend checks still enforce all permissions.

## Request serialization
Sharing and revocation join existing state-changing routes in the BEGIN IMMEDIATE transaction guard. The UNIQUE constraint prevents duplicate relationships. Read permission is checked independently for each content or file request. A download already authorized or completed cannot be recalled by later revocation.

## Four minute review demonstration
Use three disposable test accounts on one installation. Prepare an already opened capsule before the meeting. Show ownership, share with the recipient, switch browser profile or sign in as recipient, open Shared with me, and download a file. Explain that edit/delete/reshare requests are denied at the server. Use an unrelated account to demonstrate a denied direct URL. Remove recipient access and retry. Finish by searching an owned title and showing a no-match result.

## Evidence and limits
Automated results are recorded separately. Browser and Windows checks need the results stated in the testing report. Do not claim historical meetings, team estimates or Product Owner acceptance based solely on these files. Notifications and recovery remain future work.
