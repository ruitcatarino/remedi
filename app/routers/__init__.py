from app.routers import auth, medication, person

ROUTERS = [auth.router, person.router, medication.router]
