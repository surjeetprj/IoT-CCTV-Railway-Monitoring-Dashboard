from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any, Dict
from datetime import datetime

class AIResults(BaseModel):
    person_count: int
    alert: bool
    alert_type: Optional[str] = None

class VideoResponse(BaseModel):
    video_id: int = Field(validation_alias="id")
    train_number: str
    camera_id: str
    video_url: str
    stored_timestamp: datetime
    status: str
    # Pulling from the new ai_detections table
    ai_results: Optional[Dict[str, Any]] = None 

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def flatten_data(cls, data: Any) -> Any:
        """
        Senior Developer Trick: Flattening relationships for the frontend.
        Maps: Video -> Camera -> Train -> train_number
        """
        # If 'data' is a SQLAlchemy model instance
        if hasattr(data, "camera") and data.camera:
            # Flatten Camera ID
            setattr(data, "camera_id", data.camera.camera_id)
            
            # Flatten Train Number
            if data.camera.train:
                setattr(data, "train_number", data.camera.train.train_number)
        
        # Flatten AI Detections (Take the first/latest result)
        if hasattr(data, "detections") and data.detections:
            setattr(data, "ai_results", data.detections[0].detection_results)
            
        return data

class DashboardSummary(BaseModel):
    total_videos_today: int
    total_trains_monitored: int
    alerts_generated: int
    storage_usage_gb: float

class IngestRequest(BaseModel):
    camera_id: str
    train_number: str
    video_url: str
    status: Optional[str] = "available"
    ai_results: AIResults
    