# Mermaid Diagram Test

This page tests Mermaid diagram functionality.

## Simple Flowchart

```mermaid
graph TD
    A[User Request] --> B{Authentication}
    B -->|Valid| C[Process Request]
    B -->|Invalid| D[Return Error]
    C --> E[Generate Response]
    E --> F[Return to User]
    D --> F
```

## Sequence Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant V as View
    participant M as Model
    participant D as Database
    
    U->>V: Submit Form
    V->>M: Validate Data
    M->>D: Save Data
    D-->>M: Confirmation
    M-->>V: Success Response
    V-->>U: Display Success
```

## Simple Class Diagram

```mermaid
classDiagram
    class Story {
        +String title
        +String content
        +User author
        +save()
        +delete()
    }
    
    class User {
        +String username
        +String email
        +create_story()
    }
    
    User ||--o{ Story : creates
```
