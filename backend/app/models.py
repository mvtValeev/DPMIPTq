from .database import Base
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UploadedDataset(Base):
    __tablename__ = "uploaded_datasets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Study(Base):
    __tablename__ = "studies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    country_list = Column(JSON, nullable=False)
    dependent_variable = Column(String, nullable=False)
    base_variable = Column(String, nullable=False)
    control_variables = Column(JSON, nullable=False)
    time_period_start = Column(Integer, nullable=False)
    time_period_end = Column(Integer, nullable=False)
    econometric_method = Column(String, nullable=False)
    analysis_result = Column(JSON, nullable=False)
    data_sources = Column(JSON, nullable=False)
    uploaded_dataset_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_datasets.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
