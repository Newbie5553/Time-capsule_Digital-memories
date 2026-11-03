
# Sprint 2 – Testing Report
## Time Capsule – Digital Memories for the Future

**Course:** ITC 315 – Software Engineering  
**Methodology:** Agile Scrum  
**Sprint:** 2  
**Status:** Completed – Tests Passed  
**Product Owner:** Lima Wahedi

---

## 1. Testing Objective

The objective of Sprint 2 testing was to verify the successful implementation of time capsule creation, draft management, multimedia attachments, security controls, and database integration.

All planned Sprint 2 development tasks were completed, and the implemented functionality was tested successfully.

## 2. Testing Team

| Team Member | Role |
|---|---|
| Lima Wahedi | Product Owner – Acceptance Review |
| Parasto Noorzaei | Scrum Master – Testing Coordination |
| Mohammad Ibrahim Fathi | Developer – Backend and Database |
| Hamid Mirkhil Wardak | Developer – Frontend and Interface |

## 3. Test Cases and Results

| Test ID | Sprint Task | Test Scenario | Expected Result | Status |
|---|---|---|---|---|
| TC2-01 | S2-01 to S2-03 | Create a private capsule with title, message, and cover color | Capsule is saved with correct information | Passed |
| TC2-02 | S2-04 to S2-05 | Upload images and videos | Attachments upload successfully | Passed |
| TC2-03 | S2-06 to S2-09 | View saved drafts and attachments | Saved information displays correctly | Passed |
| TC2-04 | S2-06 to S2-09 | Edit an existing draft | Updated information is saved | Passed |
| TC2-05 | S2-06 to S2-09 | Download attachments | Authorized user can download files | Passed |
| TC2-06 | S2-06 to S2-09 | Delete a draft or attachment | Selected content is removed | Passed |
| TC2-07 | S2-10 to S2-13 | Verify private capsule access | Unauthorized access is prevented | Passed |
| TC2-08 | S2-10 to S2-13 | Verify password hashing | Passwords are securely stored as hashes | Passed |
| TC2-09 | S2-10 to S2-13 | Verify CSRF protection | Invalid or missing CSRF tokens are rejected | Passed |
| TC2-10 | S2-10 to S2-13 | Verify database integration | Capsule information is stored and retrieved correctly | Passed |
| TC2-11 | S2-14 | Perform functional testing | Implemented features work correctly | Passed |
| TC2-12 | S2-15 | Product Owner acceptance review | Sprint deliverables satisfy acceptance criteria | Accepted |

## 4. User Story Traceability

| User Story | Feature | Result |
|---|---|---|
| US-04, US-05 | Capsule creation and messages | Completed |
| US-09, US-10 | Multimedia attachments | Completed |
| US-08, US-11, US-12 | Draft management | Completed |
| US-17, US-18 | Capsule title and appearance | Completed |
| US-04, US-07 | Supporting security requirements | Completed |

## 5. Testing Summary

| Category | Result |
|---|---|
| Sprint Backlog Tasks | 15/15 Completed |
| Documented Test Cases | 12 |
| Passed Functional and Security Tests | 11 |
| Product Owner Acceptance Check | Accepted |
| Failed Tests | 0 reported |
| Overall Result | Completed |

## 6. Testing Evidence

Supporting evidence is maintained through the project source code, GitHub development records, and sprint demonstration recordings.

Relevant evidence includes capsule creation, attachment management, database interaction, security testing, and draft operations.

## 7. Product Owner Acceptance

The Sprint 2 functionality was reviewed and demonstrated successfully.

The completed work satisfied the Sprint 2 requirements and supported progression to Sprint 3.

**Product Owner:** Lima Wahedi  
**Final Status:** Accepted – Sprint 2 Completed

