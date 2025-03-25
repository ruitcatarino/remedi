
# Table of Contents
- [Database Schema (ER Diagram)](#database-schema-er-diagram)

# Database Schema (ER Diagram)

```mermaid
erDiagram
    users ||--o{ persons : "registers"
    persons ||--o{ medications : "is prescribed"
    medications ||--o{ medication_logs : "generates"

    users {
        int id PK
        string email
        string password_hash
        string name
        string phone_number
        date birth_date
        timestamp created_at
        timestamp updated_at
    }
    
    persons {
        int id PK
        int user_id FK
        string name
        date birth_date
        text notes
        timestamp created_at
        timestamp updated_at
    }
    
    medications {
        int id PK
        int person_id FK
        string name
        string dosage
        timedelta frequency
        date start_date
        date end_date
        int total_doses
        text notes
        timestamp created_at
        timestamp updated_at
    }
    
    medication_logs {
        int id PK
        int medication_id FK
        timestamp scheduled_time
        timestamp taken_time
        boolean skipped
        text notes
        timestamp created_at
        timestamp updated_at
    }
```