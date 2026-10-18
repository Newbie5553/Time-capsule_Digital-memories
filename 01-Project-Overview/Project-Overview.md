
# ⏳ TIME CAPSULE
### 🌌 Digital Memories for the Future

**Preserve Today • Unlock Tomorrow • Relive Forever**

![Project](https://img.shields.io/badge/Project-Time%20Capsule-7555D9)
![Methodology](https://img.shields.io/badge/Methodology-Agile%20Scrum-1678C2)
![Status](https://img.shields.io/badge/Status-Planning-F5A623)
![Team](https://img.shields.io/badge/Team-4%20Members-18A999)

---

## 🌟 01 | PROJECT VISION

> What if you could send a memory to your future self?

**Time Capsule** is a web application that allows people to preserve precious memories and rediscover them in the future.

Users can create digital capsules containing messages, photos, and videos, select a future unlocking date, and securely store their memories until that day arrives.

### 🎯 Our Objectives

- Preserve meaningful digital memories.
- Create and manage personal time capsules.
- Schedule future unlocking dates.
- Protect locked capsules from early access.
- Enable sharing with authorized users.
- Provide countdowns and notifications.
- Build the system using Agile Scrum principles.

---

## 🔮 02 | HOW TIME CAPSULE WORKS

```mermaid
flowchart LR
    A["👤 Register"] --> B["📦 Create Capsule"]
    B --> C["💌 Add Memories"]
    C --> D["📅 Schedule"]
    D --> E["🔒 Lock"]
    E --> F["🎁 Unlock"]

    style A fill:#DBEAFE,stroke:#2563EB,color:#111827
    style B fill:#EDE9FE,stroke:#7C3AED,color:#111827
    style C fill:#FCE7F3,stroke:#DB2777,color:#111827
    style D fill:#FEF3C7,stroke:#D97706,color:#111827
    style E fill:#FEE2E2,stroke:#DC2626,color:#111827
    style F fill:#D1FAE5,stroke:#059669,color:#111827
```

### 🔐 Unlocking Logic

```mermaid
flowchart TD
    A["User Opens Dashboard"] --> B["Select Capsule"]
    B --> C{"Unlock Date Reached?"}
    C -->|No| D["🔒 Keep Locked"]
    D --> E["Show Countdown"]
    C -->|Yes| F{"Authorized User?"}
    F -->|No| G["Access Denied"]
    F -->|Yes| H["🔓 Open Memories"]

    style C fill:#FEF3C7,stroke:#D97706,color:#111827
    style F fill:#FEF3C7,stroke:#D97706,color:#111827
    style D fill:#FEE2E2,stroke:#DC2626,color:#111827
    style H fill:#D1FAE5,stroke:#059669,color:#111827
```

---

## 📊 03 | FEATURE ANALYSIS

### Proposed Feature Priorities

```mermaid
pie showData
    title Initial Feature Priority Distribution
    "High Priority" : 5
    "Medium Priority" : 3
```

| Feature | Description | Priority |
|:---|:---|:---:|
| 👤 Authentication | Registration and login | 🔴 High |
| 📦 Capsule Creation | Store digital memories | 🔴 High |
| 🔒 Capsule Locking | Prevent early access | 🔴 High |
| 📅 Unlock Scheduling | Choose a future date | 🔴 High |
| 🖥️ Dashboard | Manage capsules | 🔴 High |
| 👥 Sharing | Share with authorized users | 🟡 Medium |
| 🔔 Notifications | Unlock alerts | 🟡 Medium |
| ⏳ Countdown | Display remaining time | 🟡 Medium |

**Analysis:** Five of the eight proposed features are high priority because they form the core functionality of the application.

*These are proposed priorities, not completed development results.*

---

## 👥 04 | OUR SCRUM TEAM

```mermaid
flowchart TD
    A["🚀 TIME CAPSULE SCRUM TEAM"]
    A --> B["👑 Product Owner"]
    A --> C["📋 Scrum Master"]
    A --> D["💻 Development Team"]

    B --> E["Lima Wahedi"]
    C --> F["Parasto Noorzaei"]
    D --> G["Mohammad Ibrahim Fathi"]
    D --> H["Hamid Mirkhil Wardak"]

    style A fill:#312E81,stroke:#312E81,color:#FFFFFF
    style B fill:#DDD6FE,stroke:#7C3AED,color:#111827
    style C fill:#BFDBFE,stroke:#2563EB,color:#111827
    style D fill:#A7F3D0,stroke:#059669,color:#111827
```

### Team Responsibilities

| Member | Scrum Role | Responsibilities |
|---|---|---|
| Lima Wahedi | Product Owner | Vision, backlog, prioritization, stakeholder coordination |
| Parasto Noorzaei | Scrum Master | Scrum facilitation, meetings, impediments |
| Mohammad Ibrahim Fathi | Developer | Design, implementation, testing |
| Hamid Mirkhil Wardak | Developer | Design, implementation, testing |

---

## 🗓️ 05 | PROPOSED DEVELOPMENT ROADMAP

```mermaid
flowchart LR
    A["Sprint 1<br/>Requirements & Design"]
    B["Sprint 2<br/>Core Development"]
    C["Sprint 3<br/>Integration & Testing"]
    D["Final Review<br/>& Demonstration"]

    A --> B --> C --> D

    style A fill:#DBEAFE,stroke:#2563EB,color:#111827
    style B fill:#EDE9FE,stroke:#7C3AED,color:#111827
    style C fill:#FEF3C7,stroke:#D97706,color:#111827
    style D fill:#D1FAE5,stroke:#059669,color:#111827
```

*The sprint count and roadmap are preliminary proposals pending team confirmation.*

---

## 📚 06 | SOFTWARE ENGINEERING DELIVERABLES

| Deliverable | Planned Documentation |
|---|---|
| Requirements Engineering | Functional and non-functional requirements |
| User Stories | 20 prioritized user stories |
| UML Modeling | Use case and sequence diagrams |
| Product Backlog | Standard Scrum backlog template |
| Sprint Backlogs | Sprint tasks and assignments |
| Burndown Charts | Actual sprint progress |
| Scrum Meetings | Agendas, minutes, and recordings |
| Development | Source code and testing evidence |
| Review | Sprint reviews and retrospectives |

---

## 💜 OUR PROJECT GOAL

**Build a secure, meaningful platform that transforms today's memories into tomorrow's discoveries.**

**Project:** Time Capsule – Digital Memories for the Future

**Methodology:** Agile Scrum

**Current Phase:** Initial Planning
