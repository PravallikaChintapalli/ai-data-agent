from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import shutil, os
from pathlib import Path
from .database import SessionLocal, engine, Base
from . import models, schemas, agent, utils
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Data Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", Path(__file__).parent.parent / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/upload")
async def upload_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = UPLOAD_DIR / file.filename
    # basic safety
    if not file.filename.lower().endswith(('.xls', '.xlsx')):
        raise HTTPException(status_code=400, detail="Only Excel files allowed")
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # parse and ingest
    parsed = utils.parse_and_ingest_excel(filename, db)
    return {"status": "ok", "file": file.filename, "sheets": parsed}


@app.post("/query")
async def nl_query(payload: schemas.QueryRequest, db: Session = Depends(get_db)):
    # payload includes: question, optional sheet/table name
    result = agent.handle_nl_query(payload.question, payload.table_name, db)
    return result


@app.get("/chart/{chart_path}")
async def get_chart(chart_path: str):
    file = Path("./charts") / chart_path
    if not file.exists():
        raise HTTPException(404, "Chart not found")
    return FileResponse(path=file, media_type="image/png")
