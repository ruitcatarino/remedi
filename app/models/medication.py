from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from tortoise import fields
from tortoise.models import Model

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
        """
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
            await MedicationSchedule.bulk_create(schedules_to_create)
