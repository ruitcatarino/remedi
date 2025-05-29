from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyttings import settings
from tortoise.expressions import Q

from app.models.medication import Medication
from app.models.medication_schedule import MedicationSchedule, MedicationStatus
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
        Create medication schedules for the defined period.
        Skip if already created.
        """
        now = datetime.now(ZoneInfo("UTC"))

        future_meds: list[Medication] = await Medication.filter(
            Q(start_date__gt=now, end_date__isnull=True, is_active=True, is_prn=False)
            | Q(start_date__gt=now, end_date__gt=now, is_active=True, is_prn=False)
        ).all()

        for med in future_meds:
            await med.generate_schedules()

    async def check_medication_schedules(self) -> None:
        """
        Check for medications schedules that where missed.
        Not yet taken nor notified.
        """
        now = datetime.now(ZoneInfo("UTC"))

        schedules: list[MedicationSchedule] = await MedicationSchedule.filter(
            status=MedicationStatus.SCHEDULED, scheduled_datetime__lt=now
        ).all()

        for schedule in schedules:
            await schedule.handle_medication_notification()

    async def handles_missed_medications(self) -> None:
        """Handles missed medications, bigger than grace period."""
        now = datetime.now(ZoneInfo("UTC"))
        grace_period = timedelta(minutes=settings.MEDICATION_GRACE_PERIOD)

        missed_schedules: list[MedicationSchedule] = await MedicationSchedule.filter(
            status=MedicationStatus.NOTIFIED,
            scheduled_datetime__lt=now - grace_period,
        ).all()

        for schedule in missed_schedules:
            await schedule.handle_missed_medication()

    def shutdown(self) -> None:
        self.scheduler.shutdown()
