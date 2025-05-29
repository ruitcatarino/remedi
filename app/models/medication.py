from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pyttings import settings
from tortoise import fields
from tortoise.models import Model

from app.logs import logger
from app.models.medication_log import MedicationLog
from app.models.medication_schedule import MedicationSchedule, MedicationStatus


class Medication(Model):
    id = fields.IntField(primary_key=True)
    person = fields.ForeignKeyField(
        "models.Person", related_name="medications", db_index=True
    )
    name = fields.CharField(max_length=50)
    dosage = fields.CharField(max_length=50)
    is_prn = fields.BooleanField(
        default=False, db_index=True
    )  # not scheduled, as needed
    start_date = fields.DatetimeField()
    end_date = fields.DatetimeField(null=True)
    frequency = fields.TimeDeltaField(null=True)
    total_doses = fields.IntField(null=True)
    doses_taken = fields.IntField(default=0)
    is_active = fields.BooleanField(default=True, db_index=True)
    notes = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        indexes = [("start_date", "end_date", "is_active", "is_prn")]

    @property
    async def next_scheduled(self) -> MedicationSchedule | None:
        if self.is_prn or self.is_active is False:
            return None

        return await self.schedules.filter(
            status__in=[MedicationStatus.SCHEDULED, MedicationStatus.NOTIFIED]
        ).earliest("scheduled_datetime")

    async def generate_schedules(
        self: "Medication", delta: timedelta | None = None
    ) -> None:
        """
        Create medication schedules for a medication for a defined period.
        Skip if already created.
        """
        logger.info(f"Generating medication schedules for: {self}")
        if self.is_prn:
            return

        if delta is None:
            delta = timedelta(days=1)

        now = datetime.now(ZoneInfo("UTC"))
        schedule_end = now + delta
        next_scheduled: MedicationSchedule | None = await self.next_scheduled
        current_datetime = (
            now if next_scheduled is None else next_scheduled.scheduled_datetime
        )

        if self.end_date is not None and schedule_end > self.end_date:
            schedule_end = self.end_date

        if self.start_date > schedule_end or current_datetime > schedule_end:
            return

        schedules_to_create = []

        while current_datetime <= schedule_end:
            if (
                self.total_doses is not None
                and len(schedules_to_create) >= self.total_doses - self.doses_taken
            ):
                break

            schedules_to_create.append(
                MedicationSchedule(
                    medication=self,
                    scheduled_datetime=current_datetime,
                    status=MedicationStatus.SCHEDULED,
                )
            )

            current_datetime += self.frequency

        if schedules_to_create:
            await MedicationSchedule.bulk_create(
                schedules_to_create, ignore_conflicts=True
            )

    async def _handle_unscheduled_medication_consuption(self) -> None:
        """Handles unscheduled medication consumption."""
        logger.info(f"Taking unscheduled medication: {self}")
        await MedicationLog.create(
            medication=self,
            taken_at=datetime.now(ZoneInfo("UTC")),
        )
        self.doses_taken += 1
        await self.save()
        return

    async def _handle_scheduled_medication_consuption(
        self, next_scheduled: MedicationSchedule
    ) -> bool:
        """Handles scheduled medication consumption."""
        logger.info(f"Taking scheduled medication: {self} - {next_scheduled}")
        if next_scheduled.status == MedicationStatus.MISSED:
            await next_scheduled.handle_late_taken()
            return True

        if next_scheduled.status in [
            MedicationStatus.SCHEDULED,
            MedicationStatus.NOTIFIED,
        ]:
            await next_scheduled.handle_take_medication()
            return True

        return False

    async def handle_medication_consuption(self) -> None:
        """Handles medication consumption."""
        logger.info(f"Handling medication consumption: {self}")
        if self.is_prn:
            return await self._handle_unscheduled_medication_consuption()

        grace_period = timedelta(minutes=settings.MEDICATION_GRACE_PERIOD)
        now = datetime.now(ZoneInfo("UTC"))

        next_scheduled: MedicationSchedule | None = await self.next_scheduled
        if next_scheduled is None or not (
            now - grace_period
            <= next_scheduled.scheduled_datetime
            <= now + grace_period
        ):
            return await self._handle_unscheduled_medication_consuption()

        if await self._handle_scheduled_medication_consuption(next_scheduled):
            self.doses_taken += 1
            await self.save()

        return None

    def __str__(self) -> str:
        return (
            f"Medication(start_date={self.start_date}, end_date={self.end_date}, "
            f"frequency={self.frequency}, total_doses={self.total_doses}, "
            f"doses_taken={self.doses_taken}, is_active={self.is_active})"
        )
