# Database
DB_USER: str = "user"
DB_PASSWORD: str = "password"
DB_HOST: str = "database"
DB_PORT: int = 5432
DB_NAME: str = "database"

# Redis
REDIS_PROTOCOL: str = "redis"
REDIS_HOST: str = "redis"
REDIS_PORT: int = 6379
REDIS_DB: int = 0

# JWT
JWT_SECRET_KEY: str = "secret"
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRATION: int = 3600

# Logging
LOG_LEVEL: str = "INFO"

# Configs
ALLOW_REGISTRATION: bool = True
MAINTENANCE_MODE: bool = False
REMINDER_GENERATION_INTERVAL: int = 12  # in hours
REMINDER_CHECK_INTERVAL: int = 1  # in minutes
MISSED_INTERVAL: int = 5  # in minutes
MEDICATION_GRACE_PERIOD: int = 60  # in minutes
