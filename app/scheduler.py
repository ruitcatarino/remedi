from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyttings import settings

from app.models.token_blacklist import BlacklistedToken


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstore={
                "default": RedisJobStore(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                )
            }
        )

    def start(self) -> None:
        self.scheduler.add_job(
            self.generate_medication_reminders,
            "interval",
            hours=settings.REMINDER_GENERATION_INTERVAL,
            id="generate_medication_reminders",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.check_medication_schedules,
            "interval",
            minutes=settings.REMINDER_CHECK_INTERVAL,
            id="check_medication_schedules",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.handles_missed_medications,
            "interval",
            minutes=settings.MISSED_INTERVAL,
            id="handles_missed_medications",
            replace_existing=True,
        )
        self.scheduler.add_job(
            BlacklistedToken.cleanup_expired_tokens,
            "cron",
            hour=0,
            minute=0,
            id="clean_blacklist_tokens",
            replace_existing=True,
        )
        self.scheduler.start()

    async def generate_medication_reminders(self) -> None:
        """
        Create medication schedules for the upcoming day.
        Skip if already created.
        """
        ...  # TODO

    async def check_medication_schedules(self) -> None:
        """
        Check for medications schedules that where missed.
        Not yet taken nor notified but in grace period.
        """
        ...  # TODO

    async def handles_missed_medications(self) -> None:
        """Handles missed medications, bigger than grace period."""
        ...  # TODO

    async def clean_blacklist_tokens(self) -> None:
        """Clean expired tokens from blacklist."""
        await BlacklistedToken.cleanup_expired_tokens()

    def shutdown(self) -> None:
        self.scheduler.shutdown()
