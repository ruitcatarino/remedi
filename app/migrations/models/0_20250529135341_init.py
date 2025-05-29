from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(50) NOT NULL UNIQUE,
    "password" VARCHAR(130) NOT NULL,
    "name" VARCHAR(50) NOT NULL,
    "phone_number" VARCHAR(50) NOT NULL,
    "birth_date" DATE NOT NULL,
    "timezone" VARCHAR(50) NOT NULL DEFAULT 'UTC',
    "disabled" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "blacklisted_tokens" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "token_hash" VARCHAR(64) NOT NULL UNIQUE,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "reason" VARCHAR(50) NOT NULL DEFAULT 'logout',
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_blacklisted_token_h_d91912" ON "blacklisted_tokens" ("token_hash");
CREATE INDEX IF NOT EXISTS "idx_blacklisted_expires_3b1480" ON "blacklisted_tokens" ("expires_at");
CREATE INDEX IF NOT EXISTS "idx_blacklisted_token_h_db5543" ON "blacklisted_tokens" ("token_hash", "expires_at");
CREATE INDEX IF NOT EXISTS "idx_blacklisted_user_id_3954ff" ON "blacklisted_tokens" ("user_id", "created_at");
CREATE TABLE IF NOT EXISTS "person" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "birth_date" DATE NOT NULL,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_person_user_id_de8894" UNIQUE ("user_id", "name")
);
CREATE INDEX IF NOT EXISTS "idx_person_user_id_b150dd" ON "person" ("user_id");
CREATE TABLE IF NOT EXISTS "medication" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "dosage" VARCHAR(50) NOT NULL,
    "is_prn" BOOL NOT NULL DEFAULT False,
    "start_date" TIMESTAMPTZ NOT NULL,
    "end_date" TIMESTAMPTZ,
    "frequency" BIGINT,
    "total_doses" INT,
    "doses_taken" INT NOT NULL DEFAULT 0,
    "is_active" BOOL NOT NULL DEFAULT True,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "person_id" INT NOT NULL REFERENCES "person" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_medication_person__aed88b" UNIQUE ("person_id", "name", "dosage", "start_date")
);
CREATE INDEX IF NOT EXISTS "idx_medication_is_prn_e12ab5" ON "medication" ("is_prn");
CREATE INDEX IF NOT EXISTS "idx_medication_is_acti_11ec62" ON "medication" ("is_active");
CREATE INDEX IF NOT EXISTS "idx_medication_person__c6b4db" ON "medication" ("person_id");
CREATE INDEX IF NOT EXISTS "idx_medication_start_d_77927a" ON "medication" ("start_date", "end_date", "is_active", "is_prn");
CREATE TABLE IF NOT EXISTS "medicationschedule" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "scheduled_datetime" TIMESTAMPTZ NOT NULL,
    "status" VARCHAR(10) NOT NULL DEFAULT 'scheduled',
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "medication_id" INT NOT NULL REFERENCES "medication" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_medications_medicat_6f302b" UNIQUE ("medication_id", "scheduled_datetime")
);
CREATE INDEX IF NOT EXISTS "idx_medications_medicat_054012" ON "medicationschedule" ("medication_id");
CREATE INDEX IF NOT EXISTS "idx_medications_medicat_5a6f1d" ON "medicationschedule" ("medication_id", "status");
CREATE INDEX IF NOT EXISTS "idx_medications_schedul_e9f4dd" ON "medicationschedule" ("scheduled_datetime", "status");
COMMENT ON COLUMN "medicationschedule"."status" IS 'SCHEDULED: scheduled\nNOTIFIED: notified\nTAKEN: taken\nLATE_TAKEN: late_taken\nSKIPPED: skipped\nMISSED: missed';
CREATE TABLE IF NOT EXISTS "medicationlog" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "taken_at" TIMESTAMPTZ NOT NULL,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "medication_id" INT NOT NULL REFERENCES "medication" ("id") ON DELETE CASCADE,
    "schedule_id" INT REFERENCES "medicationschedule" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_medicationl_taken_a_bf0a58" ON "medicationlog" ("taken_at");
CREATE INDEX IF NOT EXISTS "idx_medicationl_medicat_0bdc55" ON "medicationlog" ("medication_id");
CREATE INDEX IF NOT EXISTS "idx_medicationl_medicat_e3b015" ON "medicationlog" ("medication_id", "taken_at");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
