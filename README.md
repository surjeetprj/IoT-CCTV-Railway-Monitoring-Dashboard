
---

# **Railway CCTV Monitoring Dashboard - Backend**

This is a production-ready **FastAPI** backend designed for real-time monitoring of railway CCTV footage. It implements a fully normalized relational database, JWT authentication, and a scalable ingest API to satisfy the **Senior Developer** requirements for the Railway Monitoring Project.

---

### **Core Features**

* **Relational DB Design**: Implements a normalized schema with 5 linked tables: **Trains, Cameras, Videos, AI Detections, and Alerts**.
* **JWT Authentication**: Secure endpoints using OAuth2 Password Flow with Bearer tokens.
* **Relational Ingest API**: A single endpoint (`/api/v1/ingest`) that coordinates data entry across the entire relational hierarchy.
* **Advanced Filtering**: Support for filtering video logs by train number, camera ID, and specific date ranges.
* **Global Error Handling**: Centralized middleware to handle database connection issues and internal server errors gracefully.

---

### **Tech Stack**

* **Framework**: FastAPI
* **Database**: PostgreSQL (Relational)
* **ORM**: SQLAlchemy
* **Security**: Python-JOSE (JWT) & Passlib (Bcrypt)
* **Validation**: Pydantic v2

---

### **Installation & Setup**

#### **1. Install Dependencies**

Ensure you have Python 3.9+ installed, then run:

```bash
pip install -r requirements.txt

```

#### **2. Environment Configuration**

Create a `.env` file in the root directory:

```text
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/railway_db
SECRET_KEY=your_generated_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

```

#### **3. Database Initialization**

The application automatically creates tables on startup. To populate the system with professional test data:

```bash
# Run the relational seed script
python seed.py

```

---

### **Usage**

#### **1. Start the Server**

```bash
uvicorn app.main:app --reload

```

#### **2. API Documentation**

Access the interactive Swagger UI at: **`http://127.0.0.1:8000/docs`**.

#### **3. Authentication Flow**

1. Locate the **Authorize** button at the top right of the Swagger UI.
2. Use the credentials:
* **Username**: `admin`
* **Password**: `password123`


3. Once authorized, all protected endpoints (marked with a lock icon) will be accessible.

---

### **Project Architecture**

The project follows a modular "Clean Architecture" structure as required in **Part 4**:

```text
├── app/
│   ├── api/v1/endpoints/   # Auth, Ingest, and Video logic
│   ├── core/               # JWT Security and Logging config
│   ├── db/                 # DB Session and Base class
│   ├── models/             # Relational SQLAlchemy Models
│   ├── schemas/            # Pydantic Schemas (Input/Output)
│   └── main.py             # App entry & Exception handlers
├── seed.py                 # Relational Data Seeding script
└── requirements.txt        # Project dependencies

```

---

### **Design Justification (Part 2.1)**

* **Normalization**: By separating **Trains** and **Cameras** from **Videos**, we prevent data redundancy and ensure referential integrity.
* **Performance**: We implemented B-Tree indexes on `train_number` and `stored_timestamp` to ensure sub-second query times for the dashboard summary.
* **Scalability**: Moving AI detections and Alerts to separate tables allows for high-frequency data ingestion without bloating the primary video records.

---
