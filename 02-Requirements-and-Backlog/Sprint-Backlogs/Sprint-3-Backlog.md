
# 🚀 Sprint 3 | Sprint Backlog

## ⏳ Time Capsule – Digital Memories for the Future

**Application:** KeepSafe  
**Course:** ITC 315 – Software Engineering  
**Methodology:** Agile Scrum  
**Sprint:** Sprint 3  
**Sprint Status:** 🟡 Development Delivered – Final Acceptance Pending

**Product Owner:** Lima Wahedi  
**Scrum Master:** Parasto Noorzaei  
**Developers:** Mohammad Ibrahim Fathi and Hamid Mirkhil Wardak

---

## 🎯 01 | Sprint Goal

The goal of Sprint 3 is to introduce time-based capsule management, allowing users to select a future opening date, seal their capsules, monitor countdowns, and unlock their memories when the scheduled time arrives.

**Goal Status:** 🟡 Implemented According to Development README – Verification Required

---

## 📋 02 | Sprint 3 Selected Tasks

| ID | Task | Priority | Status |
|---|---|---|---|
| S3-01 | Select a future capsule opening date and time | High | ✅ Implemented |
| S3-02 | Seal a capsule after confirmation | High | ✅ Implemented |
| S3-03 | Prevent opening a sealed capsule before its scheduled time | High | ✅ Implemented |
| S3-04 | Display a live countdown | Medium | ✅ Implemented |
| S3-05 | Unlock a capsule when its opening time arrives | High | ✅ Implemented |
| S3-06 | Preserve existing user accounts and drafts during upgrade | High | ✅ Supported |
| S3-07 | Test the complete sealing and unlocking workflow | High | 🟡 Acceptance Pending |

*These are Sprint task IDs. Corresponding Product Backlog user-story IDs should be linked after checking the Product Backlog.*

## 🔗 Sprint 3 – User Story Traceability

The following table connects Sprint 3 development tasks with the corresponding user stories in the Product Backlog.

| Sprint Tasks | Related Feature | Product Backlog Reference |
|---|---|---|
| S3-01 | Set future capsule opening date and time | US-06 |
| S3-02 | Seal a capsule after confirmation | US-07 |
| S3-03 | Prevent early opening of sealed capsules | US-07 |
| S3-04 | Display a live countdown | US-13 |
| S3-05 | Unlock capsules when the scheduled time arrives | US-16 |
| S3-06 | Preserve existing user accounts and drafts | US-01, US-02, US-11 (supporting compatibility task) |
| S3-07 | Test sealing and unlocking functionality | Verification of US-06, US-07, US-13, US-16 |

**Traceability Note:** Sprint task IDs (S3-01 to S3-07) identify development activities. User Story IDs refer to the requirements defined in the Product Backlog.

---

## 💻 03 | Development Deliverables

The development team provided a cumulative Python Flask and SQLite application containing:

- Sprint 1: Registration, login, logout, and dashboard
- Sprint 2: Private drafts, attachments, editing, and deletion
- Sprint 3: Opening dates, capsule sealing, countdowns, and time-based unlocking

### Technical Components

- `app.py` – Application backend
- `templates/` – HTML interface
- `static/` – Static assets
- `tests/` – Testing files
- `requirements.txt` – Python dependencies
- `README.md` – Installation and feature documentation

---

## 🧩 04 | System Modeling

The development team has uploaded additional Sprint 3 sequence diagrams in the `03-System-Modeling` folder.

These diagrams support documentation of the application's interactions and workflows.

**Status:** ✅ Diagrams Uploaded

---

## 👩‍💼 05 | Product Owner Responsibilities

**Product Owner: Lima Wahedi**

- Reviewed the Sprint 3 development documentation.
- Identified the new capsule scheduling and unlocking features.
- Prepared and organized the Sprint 3 Backlog.
- Monitored alignment between development and project requirements.
- Coordinated sprint progress with the Scrum Team.

### Final Acceptance Checklist

- [ ] Demonstrate setting a future opening date
- [ ] Verify capsule sealing
- [ ] Confirm early access is blocked
- [ ] Verify countdown functionality
- [ ] Confirm unlocking at the scheduled time
- [ ] Record acceptance results

---

## 🔍 06 | Sprint Review

### Development Summary

Sprint 3 extends KeepSafe from private capsule storage to time-controlled memory preservation.

The development README documents the implementation of scheduling, sealing, countdowns, and unlocking.

**Product Owner Acceptance:** 🟡 Pending Final Demonstration

---

## 🔄 07 | Sprint Retrospective

### What Went Well

- The development team delivered an updated cumulative application.
- Sprint 3 builds on the previous sprint functionality.
- Additional sequence diagrams were uploaded.

### Improvements for Future Sprints

- Record acceptance testing for every major feature.
- Keep sprint documentation aligned with development changes.
- Verify database migration and existing data preservation.

---

## 🎯 08 | Next Steps

1. Complete Sprint 3 acceptance testing.
2. Record results in the Testing Report.
3. Update the Sprint 3 status after verification.
4. Review Sprint 4 deliverables.
5. Prepare the next Sprint Backlog.

---

**Prepared By:** Lima Wahedi  
**Role:** Product Owner  
**Project:** KeepSafe – Digital Time Capsule

