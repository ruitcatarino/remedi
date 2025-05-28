from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyttings import settings


class MedicationScheduler:
    def __init__(
        self, reminder_interval: int | None = None, missed_interval: int | None = None
    ):
        self.scheduler = AsyncIOScheduler(
            jobstore={
                "default": RedisJobStore(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                )
            }
        )
        self.reminder_interval = reminder_interval or settings.REMINDER_INTERVAL
        self.missed_interval = missed_interval or settings.MISSED_INTERVAL

    def start(self) -> None:
        self.scheduler.add_job(
            self.check_medication_reminders,
            "interval",
            minutes=self.reminder_interval,
            id="medication_reminders",
            replace_existing=True,
        )
        self.scheduler.add_job(
            self.check_missed_medications,
            "interval",
            minutes=self.missed_interval,
            id="missed_medications",
            replace_existing=True,
        )
        self.scheduler.start()

    async def check_medication_reminders(self) -> None:
        """Check for medications that need reminders"""
        ...  # TODO

    async def check_missed_medications(self) -> None:
        """Check for missed medications"""
        ...  # TODO

    def shutdown(self) -> None:
        self.scheduler.shutdown()
