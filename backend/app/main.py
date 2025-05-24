import time
import math
import pandas as pd
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from .database import engine, SessionLocal
from . import models, auth
from .schemas import (
    UserCreate, Token,
    DatasetResponse,
    RunAnalysisRequest, RunAnalysisResponse, MethodEnum
)
from .world_bank import fetch_world_bank_data
from .econometrics import perform_analysis

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    # Ждём, пока БД поднимется, и создаём таблицы
    for i in range(10):
        try:
            models.Base.metadata.create_all(bind=engine)
            print("✅ Database tables created")
            return
        except OperationalError:
            print(f"⏳ Database not ready, retrying ({i+1}/10)...")
            time.sleep(1)
    raise RuntimeError("❌ Could not connect to the database after retries")

@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=dict)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"email": user.email, "id": str(user.id), "created_at": user.created_at}

@app.post("/upload-dataset/", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    # Проверяем токен
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Читаем файл
    if file.filename.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(file.file)
    else:
        df = pd.read_csv(file.file)

    # Заменяем все NaN (числовые и строковые) на None
    records = df.to_dict(orient="records")
    cleaned = []
    for rec in records:
        new = {}
        for k, v in rec.items():
            if isinstance(v, float) and math.isnan(v):
                new[k] = None
            elif isinstance(v, str) and v.strip().lower() == "nan":
                new[k] = None
            else:
                new[k] = v
        cleaned.append(new)

    dataset = models.UploadedDataset(
        user_id=user.id,
        file_name=file.filename,
        data=cleaned
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return {"dataset_id": str(dataset.id), "status": "uploaded successfully"}

@app.get("/my-datasets/", response_model=list[dict])
def list_my_datasets(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    records = db.query(models.UploadedDataset).filter_by(user_id=user.id).all()
    return [
        {"dataset_id": str(r.id), "file_name": r.file_name, "created_at": r.created_at}
        for r in records
    ]

@app.post("/run-analysis/", response_model=RunAnalysisResponse)
def run_analysis(req: RunAnalysisRequest):
    # Собираем индикаторы
    names = {req.dependent_metric}
    if req.base_metric:
        names.add(req.base_metric)
    names.update(req.control_metrics)
    names.update(req.instrument_metrics)
    names.update(req.exog_metrics)

    from .indicator_map import METRIC_MAP
    unknown = names - METRIC_MAP.keys()
    if unknown:
        raise HTTPException(400, f"Unknown metrics: {unknown}")

    indicators = {METRIC_MAP[n]: n for n in names}

    df = fetch_world_bank_data(
        indicators=indicators,
        countries=req.countries,
        start_year=req.start_year,
        end_year=req.end_year
    )

    result = perform_analysis(
        df=df,
        method=req.method.value,
        dependent_var=req.dependent_metric,
        base_var=req.base_metric,
        control_vars=req.control_metrics,
        instrument_vars=req.instrument_metrics,
        exog_vars=req.exog_metrics,
        entity=req.entity,
        time=req.time
    )
    return result



@app.get("/my-studies/", response_model=list[dict])
def my_studies(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    records = db.query(models.StudyResult).filter_by(user_id=user.id).order_by(models.StudyResult.created_at.desc()).all()
    return [{
        "method": r.method,
        "start_year": r.start_year,
        "end_year": r.end_year,
        "countries": r.countries,
        "metrics": r.metrics,
        "r_squared": r.r_squared,
        "summary": r.summary
    } for r in records]


from collections import Counter
import json

@app.get("/popular-studies/", response_model=list[dict])
def popular_studies(db: Session = Depends(get_db), top_n: int = 10):
    records = db.query(models.StudyResult).all()
    counter = Counter()

    for r in records:
        key = json.dumps({
            "method": r.method,
            "dependent_metric": r.dependent_metric,
            "base_metric": r.base_metric,
            "control_metrics": sorted(r.metrics or [])
        }, sort_keys=True)
        counter[key] += 1

    top = counter.most_common(top_n)
    return [
        {
            **json.loads(key),
            "count": count
        } for key, count in top
    ]
