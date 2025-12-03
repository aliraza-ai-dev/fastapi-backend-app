from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, auth

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="FastAPI Backend Example")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(400, "User already exists")
    return crud.create_user(db, user)

@app.post("/auth/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    stored = crud.get_user_by_username(db, user.username)
    if not stored or not crud.verify_password(user.password, stored.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    token = auth.create_access_token({"sub": stored.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/", response_model=list[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()
