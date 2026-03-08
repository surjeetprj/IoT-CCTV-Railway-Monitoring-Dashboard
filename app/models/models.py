from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.session import Base
import datetime

class Train(Base):
    __tablename__ = "trains"
    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String, unique=True, index=True, nullable=False) #
    
    # Relationships
    cameras = relationship("Camera", back_populates="train")

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String, unique=True, index=True, nullable=False) #
    train_id = Column(Integer, ForeignKey("trains.id"))
    
    # Relationships
    train = relationship("Train", back_populates="cameras")
    videos = relationship("Video", back_populates="camera")

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id")) # Normalized link to camera
    video_url = Column(String, nullable=False) #
    stored_timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    status = Column(String, default="available")
    
    # Relationships
    camera = relationship("Camera", back_populates="videos")
    detections = relationship("AIDetection", back_populates="video")
    alerts = relationship("Alert", back_populates="video")

class AIDetection(Base):
    __tablename__ = "ai_detections"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    detection_results = Column(JSONB, nullable=True) # Results from AI analysis
    
    # Relationship back to video
    video = relationship("Video", back_populates="detections")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    alert_type = Column(String) #
    is_resolved = Column(Boolean, default=False)
    
    # Relationship back to video
    video = relationship("Video", back_populates="alerts")