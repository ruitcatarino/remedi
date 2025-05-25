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
    "frequency" BIGINT NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE,
    "total_doses" INT,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "person_id" INT NOT NULL REFERENCES "person" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_medication_end_dat_9e3376" ON "medication" ("end_date");
CREATE INDEX IF NOT EXISTS "idx_medication_person__c6b4db" ON "medication" ("person_id");
CREATE INDEX IF NOT EXISTS "idx_medication_start_d_f95688" ON "medication" ("start_date", "end_date");
CREATE TABLE IF NOT EXISTS "medicationlog" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "schedule" BIGINT NOT NULL,
    "taken_at" TIMESTAMPTZ NOT NULL,
    "skipped" BOOL NOT NULL DEFAULT False,
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "medication_id" INT NOT NULL REFERENCES "medication" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_medicationl_taken_a_bf0a58" ON "medicationlog" ("taken_at");
CREATE INDEX IF NOT EXISTS "idx_medicationl_medicat_0bdc55" ON "medicationlog" ("medication_id");
CREATE INDEX IF NOT EXISTS "idx_medicationl_medicat_001164" ON "medicationlog" ("medication_id", "skipped");
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
