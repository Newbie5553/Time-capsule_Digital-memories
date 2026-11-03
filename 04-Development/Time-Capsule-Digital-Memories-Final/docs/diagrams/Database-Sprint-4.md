# Sprint 4 database model

```mermaid
erDiagram
    USERS ||--o{ CAPSULES : owns
    CAPSULES ||--o{ ATTACHMENTS : contains
    CAPSULES ||--o{ CAPSULE_SHARES : grants
    USERS ||--o{ CAPSULE_SHARES : receives
    USERS {
        integer id PK
        text name
        text email UK
        text password
    }
    CAPSULES {
        integer id PK
        integer user_id FK
        text title
        text message
        text theme
        real created_at
        real updated_at
        integer locked
        real unlock_at
        real sealed_at
    }
    ATTACHMENTS {
        integer id PK
        integer capsule_id FK
        text filename
        text stored UK
        text kind
    }
    CAPSULE_SHARES {
        integer id PK
        integer capsule_id FK
        integer recipient_id FK
        real created_at
    }
```

UNIQUE(capsule_id, recipient_id) prevents duplicate shares. Foreign keys protect references. Recipient index supports lookup. The capsule owner does not change when a share is added. The new table is added with CREATE TABLE IF NOT EXISTS; no existing data is reset.
