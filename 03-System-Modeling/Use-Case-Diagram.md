# Use Case Diagram - Digital Time Capsule System

```mermaid
graph TD
    User["User / Member"] --> Sign["Sign Up / Login"]
    User --> Profile["Manage User Profile"]
    User --> Create["Create New Time Capsule"]
    User --> Edit["Edit or Delete Capsule"]
    User --> Upload["Upload Photos & Videos"]
    User --> Write["Write Letters & Messages"]
    User --> Open["Open Time Capsule"]

    Create -. "<<include>>" .-> Unlock["Set Unlock Date & Time"]
    Open -. "<<extend>>" .-> Notify["Receive Reminder Notification"]
    Open -. "<<include>>" .-> View["View Past Memories"]

    Timer["Notification & Timer System"] --> Notify
    Recipient["Future Recipient"] --> View
