import os
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, get_session
from models import Video

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

STORAGE_PATH = Path(os.getenv("STORAGE_PATH", BASE_DIR.parent / "storage" / "videos")).resolve()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

app = FastAPI(title="Telepipe Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoOut(BaseModel):
    id: int
    title: str
    original_name: str
    mime_type: str
    size: int
    created_at: str
    file_url: str

    class Config:
        from_attributes = True


@app.on_event("startup")
def on_startup() -> None:
    STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)


def _video_to_dict(video: Video) -> dict:
    return {
        "id": video.id,
        "title": video.title,
        "original_name": video.original_name,
        "mime_type": video.mime_type,
        "size": video.size,
        "created_at": video.created_at.isoformat(),
        "file_url": f"{BASE_URL}/video/{video.id}",
    }


@app.post("/upload", status_code=201)
async def upload_video(
    file: UploadFile = File(...),
    title: str | None = Form(None),
    db: Session = Depends(get_session),
):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    extension = Path(file.filename or "").suffix or ".bin"
    stored_name = f"{uuid4().hex}{extension}"
    file_path = STORAGE_PATH / stored_name
    with open(file_path, "wb") as buffer:
        buffer.write(data)

    video = Video(
        title=title or (file.filename or stored_name),
        original_name=file.filename or stored_name,
        stored_name=stored_name,
        mime_type=file.content_type or "application/octet-stream",
        size=len(data),
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return _video_to_dict(video)


@app.get("/videos", response_model=list[VideoOut])
def list_videos(db: Session = Depends(get_session)):
    videos = db.query(Video).order_by(Video.created_at.desc()).all()
    return [_video_to_dict(video) for video in videos]


@app.get("/video/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_session)):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    file_path = STORAGE_PATH / video.stored_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(path=file_path, filename=video.original_name, media_type=video.mime_type)
