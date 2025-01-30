from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import books, users, customer, reservations, admin, auth
from app.middleware.error_handler import error_handler

app = FastAPI(
    title="BookStore API",
    description="BookStore API",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.middleware("http")(error_handler)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(customer.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(reservations.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")