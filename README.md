# Profile Intelligence Service API

A RESTful backend service that enriches a user’s name using multiple external APIs, processes the data, stores it, and exposes clean endpoints for retrieval and management.

---

## Live API

Base URL:  
https://debazz4.pythonanywhere.com

---

## Features

- Integrates with multiple third-party APIs
- Data processing and normalization
- Persistent storage using a relational database
- Idempotent profile creation (no duplicates)
- Filtering support
- Clean and consistent JSON responses
- Full test coverage using Django REST Framework

---

## External APIs Used

- Genderize → https://api.genderize.io?name={name}
- Agify → https://api.agify.io?name={name}
- Nationalize → https://api.nationalize.io?name={name}

---

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite
- Requests

---

## Installation & Setup

```bash
git clone https://github.com/debazz4/enrich-profiling-intelligence-api.git
cd enrich-profiling-intelligence-api

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

---

## CORS

Access-Control-Allow-Origin: *

---

## API Endpoints

### POST /api/profiles

Request:
{
  "name": "ella"
}

Response:
{
  "status": "success",
  "data": {
    "id": "uuid",
    "name": "ella",
    "gender": "female",
    "gender_probability": 0.99,
    "sample_size": 1234,
    "age": 46,
    "age_group": "adult",
    "country_id": "NG",
    "country_probability": 0.85,
    "created_at": "2026-04-01T12:00:00Z"
  }
}

---

### GET /api/profiles/{id}

---

### GET /api/profiles?gender=male&country_id=NG

---

### DELETE /api/profiles/{id}

---

## Error Handling

{
  "status": "error",
  "message": "Error message"
}

---

## Running Tests

python manage.py test

---

## Author

Adebola Ajewole Olatunde
