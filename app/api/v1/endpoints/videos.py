from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import func
from datetime import date, datetime

from app.db.session import get_db
from app.schemas.video import VideoResponse, DashboardSummary
# Import all required models for joining
from app.models.models import Video, Alert, Camera, Train 
from app.core.logging_config import logger
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

router = APIRouter()

@router.get("/videos", response_model=List[VideoResponse], tags=["API"])
def get_all_videos(
    train_number: Optional[str] = Query(None, examples=["12401"]),
    camera_id: Optional[str] = Query(None, examples=["CAM_01"]),
    from_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    to_date: Optional[datetime] = Query(None, description="Format: YYYY-MM-DDTHH:MM:SS"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=100),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Fetch videos using relational joins to filter by Train and Camera attributes.
    """
    logger.info(f"Request started: GET /videos | Filters: train={train_number}, cam={camera_id}")
    
    # Start the query on Video
    query = db.query(Video)
    
    # Join with Camera and Train to access their attributes for filtering
    if train_number:
        # Video -> Camera -> Train
        query = query.join(Camera).join(Train).filter(Train.train_number == train_number)
    
    if camera_id:
        # Video -> Camera
        query = query.join(Camera).filter(Camera.camera_id == camera_id)

    if from_date:
        query = query.filter(Video.stored_timestamp >= from_date)
    if to_date:
        query = query.filter(Video.stored_timestamp <= to_date)
    
    results = query.offset(skip).limit(limit).all()
    
    logger.info(f"Request completed: GET /videos | Found {len(results)} records")
    return results

@router.get("/dashboard/summary", response_model=DashboardSummary, tags=["API"])
def get_dashboard_summary(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Aggregate metrics using the normalized Relational structure.
    """
    today = date.today()
    
    # 1. Total videos stored today
    videos_today = db.query(Video).filter(func.date(Video.stored_timestamp) == today).count()

    # 2. Total unique trains (Now directly from the Trains table)
    total_trains = db.query(Train).count()

    # 3. Alert count (Now from the dedicated Alerts table)
    alerts = db.query(Alert).count()

    # 4. Storage Usage Mock
    storage_usage = round((videos_today * 0.5), 2)

    return {
        "total_videos_today": videos_today,
        "total_trains_monitored": total_trains,
        "alerts_generated": alerts,
        "storage_usage_gb": storage_usage
    }

@router.get("/videos/{video_id}", response_model=VideoResponse, tags=["API"])
def get_video_details(video_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Retrieve full metadata for a specific video ID.
    """
    video = db.query(Video).filter(Video.id == video_id).first()
    
    if not video:
        logger.warning(f"Video ID {video_id} not found")
        raise HTTPException(status_code=404, detail="Video record not found")
    
    return video