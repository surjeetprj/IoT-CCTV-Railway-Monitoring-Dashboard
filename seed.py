# seed.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.models import models
from datetime import datetime, timedelta
import random

def seed_data():
    db = SessionLocal()
    try:
        # 1. Clear existing data in correct relational order
        db.query(models.Alert).delete()
        db.query(models.AIDetection).delete()
        db.query(models.Video).delete()
        db.query(models.Camera).delete()
        db.query(models.Train).delete()
        db.commit()

        # 2. Create Train Records
        train_nums = ["12401", "12951", "12002", "12301"]
        train_objs = [models.Train(train_number=tn) for tn in train_nums]
        db.add_all(train_objs)
        db.flush()

        # 3. Create Camera Records linked to Trains
        cameras = []
        for i, train in enumerate(train_objs):
            for j in range(1, 3): # 2 cameras per train
                cam = models.Camera(camera_id=f"CAM_{train.train_number}_{j}", train_id=train.id)
                cameras.append(cam)
        db.add_all(cameras)
        db.flush()

        # 4. Create 20 Video Records with varying timestamps
        statuses = ["available", "processing"]
        alert_types = ["Unattended Baggage", "Crowd Limit Exceeded", "Unauthorized Entry"]
        
        for i in range(20):
            # Distribute videos across different cameras
            target_cam = cameras[i % len(cameras)]
            
            # Create varying timestamps (1 hour apart) to test date filtering
            timestamp = datetime.utcnow() - timedelta(hours=i)
            
            video = models.Video(
                camera_id=target_cam.id,
                video_url=f"https://s3.ap-south-1.amazonaws.com/rail-bucket/vid_{i+1}.mp4",
                stored_timestamp=timestamp,
                status=random.choice(statuses)
            )
            db.add(video)
            db.flush()

            # 5. Create AI Detections for every video
            is_alert = (i % 4 == 0) # Generate an alert every 4th record
            detection = models.AIDetection(
                video_id=video.id,
                detection_results={
                    "person_count": random.randint(0, 50),
                    "alert": is_alert,
                    "alert_type": random.choice(alert_types) if is_alert else None
                }
            )
            db.add(detection)

            # 6. Create Alert table entry if flagged
            if is_alert:
                alert = models.Alert(
                    video_id=video.id,
                    alert_type=detection.detection_results["alert_type"],
                    is_resolved=False
                )
                db.add(alert)

        db.commit()
        print(f"Success! Seeded {db.query(models.Video).count()} relational records.")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()