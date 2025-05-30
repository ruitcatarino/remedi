# Architecture Documentation

## Table of Contents
- [Database Schema (ER Diagram)](#database-schema-er-diagram)
- [Model Relationships](#model-relationships)

## Database Schema (ER Diagram)

```mermaid
erDiagram
    users ||--o{ persons : "registers"
    users ||--o{ blacklisted_tokens : "has"
    persons ||--o{ medications : "is_prescribed"
    medications ||--o{ medication_schedules : "generates"
    medications ||--o{ medication_logs : "tracks"
    medication_schedules ||--o| medication_logs : "creates"

    users {
        int id PK
        string email UK
        string password
        string name
        string phone_number
        date birth_date
        string timezone
        boolean disabled
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
        boolean is_prn
        datetime start_date
        datetime end_date
        timedelta frequency
        int total_doses
        int doses_taken
        boolean is_active
        text notes
        timestamp created_at
        timestamp updated_at
    }
   
    medication_schedules {
        int id PK
        int medication_id FK
        datetime scheduled_datetime
        string status
        timestamp created_at
        timestamp updated_at
    }

    medication_logs {
        int id PK
        int medication_id FK
        int schedule_id FK
        datetime taken_at
        text notes
        timestamp created_at
        timestamp updated_at
    }

    blacklisted_tokens {
        int id PK
        int user_id FK
        string token_hash UK
        datetime expires_at
        timestamp created_at
        string reason
    }
```

## Model Relationships

### Core Entities

**Users**
- Primary entity representing system users
- Has one-to-many relationship with persons (can manage multiple people)
- Has one-to-many relationship with blacklisted tokens for security

**Persons** 
- Represents individuals whose medications are being tracked
- Each person belongs to a user (caregiver relationship)
- Has one-to-many relationship with medications

**Medications**
- Represents prescribed medications for a person
- Can be scheduled (regular intervals) or PRN (as needed)
- Tracks dosage information, frequency, and active status
- Has one-to-many relationships with both schedules and logs

### Scheduling & Tracking

**Medication Schedules**
- Represents individual scheduled doses
- Links to a specific medication with a scheduled datetime
- Tracks status: `scheduled`, `notified`, `taken`, `late_taken`, `skipped`, `missed`
- Has optional one-to-one relationship with medication logs when completed

**Medication Logs**
- Records when medications are actually taken
- Can be linked to a schedule (for scheduled doses) or standalone (for PRN doses)
- Tracks actual taken time and optional notes

### Security

**Blacklisted Tokens**
- Manages JWT token invalidation for security
- Stores hashed tokens to prevent reuse after logout
