# 🧩 System Modeling – Time Capsule Project

## 📊 Sequence Diagrams

Sequence diagrams show how different parts of our
application communicate to complete a task.

### 01 | Save Time Capsule Draft

![Save Time Capsule Draft](Sequence%20Diagram%201.png)

**Status:** 🟡 Design Prepared – Implementation Pending

### 🎯 Purpose

This diagram explains how a user can save a time
capsule draft in the KeepSafe application.

### 👥 Components

- User
- Website
- Python Flask Backend
- SQLite Database
- Private File Storage

### 🔄 Main Workflow

1. User enters the capsule title, message, and date.
2. User optionally selects photos or videos.
3. User clicks the Save Draft button.
4. The Flask backend validates the information.
5. If valid, the application saves the capsule draft.
6. Selected attachments are processed and stored.
7. The user is redirected to the draft preview.
8. If the input is invalid, an error message appears.

### 📌 Development Status

The sequence diagram has been uploaded to GitHub.

The capsule creation and draft-saving functionality
is still pending implementation.

### 🔜 Next Steps

- Review the diagram with the development team.
- Prepare additional sequence diagrams.
- Compare the diagram with the Product Backlog.
- Update implementation status after testing.

