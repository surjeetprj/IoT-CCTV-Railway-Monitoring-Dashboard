from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.models.models import Train, Camera, Video, AIDetection, Alert
from app.schemas.video import IngestRequest
from app.core.logging_config import logger

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, tags=["Ingest"])
def ingest_video_data(payload: IngestRequest, db: Session = Depends(get_db)):
    """
    Relational Ingest: Coordinates data across Trains, Cameras, 
    Videos, AI Detections, and Alerts tables.
    """
    try:
        # 1. Handle Train: Get or Create
        train = db.query(Train).filter(Train.train_number == payload.train_number).first()
        if not train:
            train = Train(train_number=payload.train_number)
            db.add(train)
            db.flush() # Flush to get train.id for the camera link

        # 2. Handle Camera: Get or Create linked to the Train
        camera = db.query(Camera).filter(Camera.camera_id == payload.camera_id).first()
        if not camera:
            camera = Camera(camera_id=payload.camera_id, train_id=train.id)
            db.add(camera)
            db.flush() # Flush to get camera.id for the video link

        # 3. Create Video Entry
        new_video = Video(
            camera_id=camera.id,
            video_url=payload.video_url,
            stored_timestamp=datetime.utcnow(),
            status= payload.status
        )
        db.add(new_video)
        db.flush() # Flush to get new_video.id for detection and alert links

        
        # 4. Create AI Detection Record (Save the FULL context here)
        detection = AIDetection(
            video_id=new_video.id,
            # Use .dict() to save person_count, alert, and alert_type
            detection_results=payload.ai_results.dict() 
        )
        db.add(detection)
        
        # 5. Create Alert Record (if the flag is true)
        if payload.ai_results.alert:
            alert = Alert(
                video_id=new_video.id,
                alert_type=payload.ai_results.alert_type or "General Security"
            )
            db.add(alert)

        db.commit()
        logger.info(f"Relational Ingest Complete: Train {payload.train_number} | Video {new_video.id}")
        
        return {
            "message": "Data ingested successfully",
            "video_id": new_video.id,
            "train_id": train.id
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Ingest Failed: {str(e)}")
        raise e