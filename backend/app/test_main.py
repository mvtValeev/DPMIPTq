
import pytest
from httpx import AsyncClient
from main import app
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, User

@pytest.fixture(scope="module", autouse=True)
def setup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/register", json={
            "email": "test@example.com",
            "password": "testpass"
        })
        assert res.status_code == 200
        token = res.json()["access_token"]
        assert token

        res2 = await ac.post("/token", data={
            "username": "test@example.com",
            "password": "testpass"
        })
        assert res2.status_code == 200
        assert res2.json()["access_token"] != ""

@pytest.mark.asyncio
async def test_upload_dataset():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/token", data={
            "username": "test@example.com",
            "password": "testpass"
        })
        token = res.json()["access_token"]

        with open("/mnt/data/test_data.csv", "w") as f:
            f.write("country,year,GDP,Inflation\nUSA,2020,21000,2.3\nUSA,2021,22000,2.5\n")

        with open("/mnt/data/test_data.csv", "rb") as file:
            upload = await ac.post("/upload-dataset/", headers={"Authorization": f"Bearer {token}"}, files={"file": file})
            assert upload.status_code == 200
            assert "dataset_id" in upload.json()

@pytest.mark.asyncio
async def test_run_preview_analysis():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/token", data={
            "username": "test@example.com",
            "password": "testpass"
        })
        token = res.json()["access_token"]

        ds_list = await ac.get("/my-datasets/", headers={"Authorization": f"Bearer {token}"})
        dataset_id = ds_list.json()[0]["dataset_id"]

        res = await ac.post("/run-analysis/", headers={"Authorization": f"Bearer {token}"}, json={
            "countries": ["USA"],
            "method": "OLS",
            "dependent_metric": "GDP",
            "base_metric": "Inflation",
            "control_metrics": [],
            "start_year": 2020,
            "end_year": 2021,
            "uploaded_dataset_id": dataset_id,
            "preview": True
        })
        assert res.status_code == 200
        assert "preview" in res.json()

@pytest.mark.asyncio
async def test_history_and_popular():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        res = await ac.post("/token", data={
            "username": "test@example.com",
            "password": "testpass"
        })
        token = res.json()["access_token"]

        history = await ac.get("/my-studies/", headers={"Authorization": f"Bearer {token}"})
        assert history.status_code == 200

        pop = await ac.get("/popular-studies/")
        assert pop.status_code == 200
        assert isinstance(pop.json(), list)
