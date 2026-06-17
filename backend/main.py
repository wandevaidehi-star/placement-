from jose import jwt
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import engine, Base, SessionLocal, User


app = FastAPI()
SECRET_KEY = "educationportal123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)



# ---------- Pydantic Models ----------
class RegisterUser(BaseModel):
    name: str
    email: str
    password: str


class LoginUser(BaseModel):
    email: str
    password: str


# ---------- Database ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Home ----------
@app.get("/")
def home():
    return {"message": "FastAPI + SQLite working"}


# ---------- Register ----------
@app.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")



    new_user = User(
    name=user.name,
    email=user.email,
    password=user.password
)
    

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email
    }


# ---------- Login ----------
@app.post("/login")
def login(user: LoginUser, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if user.password != db_user.password:
        raise HTTPException(status_code=400, detail="Wrong password")

        token = create_access_token({"sub": db_user.email})

        return {
        "access_token": token,
        "token_type": "bearer"
    }