# Sprint 3 sequence diagrams

## Choose a time and seal a draft
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Browser
    participant App as Flask
    participant DB as SQLite
    User->>UI: Select opening date and confirm
    UI->>UI: Convert local time to UTC
    UI->>App: POST seal with CSRF token
    App->>App: Validate session and token
    App->>DB: Begin write transaction and check owner/state
    alt Draft and future opening time
        App->>DB: Save locked flag and timestamps
        App->>DB: Commit
        App-->>UI: Redirect to sealed capsule
        UI-->>User: Show countdown
    else Invalid input or already sealed
        App-->>UI: Error response
        UI-->>User: Show correction or access message
    end
```

## Open a capsule
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Browser
    participant App as Flask
    participant DB as SQLite
    User->>UI: Select capsule
    UI->>App: GET capsule
    App->>DB: Find capsule owned by current user
    DB-->>App: Return capsule or no match
    alt Not owner
        App-->>UI: Not found
    else Sealed and opening time not reached
        App-->>UI: Metadata only
        UI->>App: Request state and server timestamps
        App-->>UI: Sealed state and timing metadata
        UI-->>User: Display countdown
    else Opening time reached
        App-->>UI: Message and authorized download links
        UI-->>User: Show memory
    end
```

Every attachment download independently checks ownership and time. A countdown reaching zero requests confirmation from the server before reloading the memory.
