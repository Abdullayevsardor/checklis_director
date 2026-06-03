import os

from fastapi import FastAPI
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.modules.auth.router import router as auth_router
from app.modules.workly.router import router as workly_router
from app.modules.users.router import router as users_router
from app.modules.branches.router import router as branches_router
from app.modules.checklist.router import router as checklist_router
from app.modules.shift_checks.router import router as shift_checks_router
from app.modules.uploads.router import router as uploads_router
from app.modules.reports.router import router as reports_router
from app.modules.admin.router import router as admin_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/"
)

if os.path.exists("media"):
    app.mount("/media", StaticFiles(directory="media"), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Har bir router faqat BIR MARTA qo'shiladi
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(workly_router, prefix="/api/workly", tags=["Workly"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(branches_router, prefix="/api/branches", tags=["Branches"])
app.include_router(checklist_router, prefix="/api/checklist", tags=["Checklist"])
app.include_router(shift_checks_router, prefix="/api/shift-checks", tags=["Shift Checks"])
app.include_router(uploads_router, prefix="/api/uploads", tags=["Uploads"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])

@app.get("/")
async def root():
    return {"status": "ok", "app": settings.APP_NAME}

@app.get("/users")
def get_users():
    return {"message": "Users ro'yxati"}