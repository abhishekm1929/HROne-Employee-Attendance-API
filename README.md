# Employee Attendance & Analytics API

A FastAPI and MongoDB service for employee attendance tracking, punch-in/out workflows with business rules (grace period, overtime, overnight shifts), manual corrections with an audit trail, and analytics endpoints powered by MongoDB aggregation pipelines.

## Prerequisites
- Python 3.11+
- MongoDB 6.0+ (Tested against MongoDB 7.0)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables:**
   Configure connection settings (defaults to `mongodb://localhost:27017` and `attendance_db`):
   ```bash
   export MONGO_URI="mongodb://localhost:27017"
   export MONGO_DB="attendance_db"
   ```

3. **Seed Sample Data (Optional):**
   ```bash
   python sample_seed.py
   ```

4. **Start the API Server:**
   ```bash
   uvicorn app.main:app --port 8000
   ```

All necessary database indexes are created automatically and idempotently at startup.

## Deliverables Included
- `app/main.py`: Complete FastAPI application with all 11 endpoints + readiness probe.
- `requirements.txt`: Python package dependencies.
- `REVIEW.md`: Comprehensive review of starter code defects, symptoms, and fixes.
- `DECISIONS.md`: Technical rationale addressing indexing, concurrency, tie-breaking, headcount, and scale.
