from app.routers import auth, medication, medication_schedule, person

ROUTERS = [auth.router, person.router, medication.router, medication_schedule.router]
