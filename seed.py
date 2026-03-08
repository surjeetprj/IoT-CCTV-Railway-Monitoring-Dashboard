# seed.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models import models
from datetime import datetime, timedelta

def seed_data():
    db = SessionLocal()
    try:
        # 1. Clear existing data in reverse order of relationships to avoid FK errors
        db.query(models.Alert).delete()
        db.query(models.AIDetection).delete()
        db.query(models.Video).delete()
        db.query(models.Camera).delete()
        db.query(models.Train).delete()
        db.commit()

        # 2. Create Train Records
        train_1 = models.Train(train_number="12401")
        train_2 = models.Train(train_number="12951")
        db.add_all([train_1, train_2])
        db.flush() # Flush to get IDs for the next step

        # 3. Create Camera Records linked to Trains
        cam_1 = models.Camera(camera_id="CAM_A1", train_id=train_1.id)
        cam_2 = models.Camera(camera_id="CAM_B2", train_id=train_2.id)
        db.add_all([cam_1, cam_2])
        db.flush()

        # 4. Create Video Records linked to Cameras
        v1 = models.Video(
            camera_id=cam_1.id,
            video_url="https://s3.ap-south-1.amazonaws.com/rail-bucket/v1.mp4",
            stored_timestamp=datetime.utcnow(),
            status="available"
        )
        v2 = models.Video(
            camera_id=cam_2.id,
            video_url="https://s3.ap-south-1.amazonaws.com/rail-bucket/v2.mp4",
            stored_timestamp=datetime.utcnow() - timedelta(hours=2),
            status="processing"
        )
        db.add_all([v1, v2])
        db.flush()

        # 5. Create AI Detection Records
        d1 = models.AIDetection(
            video_id=v1.id,
            detection_results={"person_count": 5, "alert": False}
        )
        d2 = models.AIDetection(
            video_id=v2.id,
            detection_results={"person_count": 2, "alert": True,"alert_type":"unattended_baggage"}
        )
        db.add_all([d1, d2])

        # 6. Create Alert Records for flagged videos
        alert_v2 = models.Alert(
            video_id=v2.id,
            alert_type="unattended_baggage",
            is_resolved=False
        )
        db.add(alert_v2)

        db.commit()
        print("Successfully seeded Relational Railway DB with initial data!")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()