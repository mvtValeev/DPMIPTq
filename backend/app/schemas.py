from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DatasetResponse(BaseModel):
    dataset_id: str
    status: str

class StudyCreate(BaseModel):
    country_list: List[str]
    dependent_variable: str
    base_variable: str
    control_variables: List[str]
    time_period_start: int
    time_period_end: int
    econometric_method: str
    data_sources: List[str]
    uploaded_dataset_id: Optional[str] = None

from enum import Enum

class MethodEnum(str, Enum):
    OLS  = "OLS"
    TSLS = "2SLS"
    FE   = "FE"
    RE   = "RE"

# Тело запроса на анализ
class RunAnalysisRequest(BaseModel):
    countries: List[str]
    method: MethodEnum
    dependent_metric: str

    # Для OLS/2SLS
    base_metric: Optional[str] = None
    control_metrics: Optional[List[str]] = None

    # Для 2SLS
    instrument_metrics: Optional[List[str]] = None

    # Для FE/RE
    exog_metrics: Optional[List[str]] = None
    entity: Optional[str] = None
    time: Optional[str] = None

    start_year: int
    end_year: int

# Ответ от анализа
class RunAnalysisResponse(BaseModel):
    method: MethodEnum
    params: dict
    pvalues: dict
    r_squared: Optional[float]
    summary: str
