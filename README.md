# Profile Intelligence Query Engine

A scalable backend service that aggregates demographic data, stores structured profiles, and provides advanced querying capabilities including filtering, sorting, pagination, and natural language search.

---

## Base URL

```
https://debazz4.pythonanywhere.com
```

---

## Project Overview

This project was built as part of a backend engineering assessment to simulate a real-world **demographic intelligence system**.

The system:

* Integrates with multiple external APIs
* Stores enriched profile data
* Provides advanced querying capabilities
* Supports natural language search

---

## Features

### Data Enrichment (Stage 1)

* Gender prediction
* Age estimation
* Country inference

### Data Persistence

* UUID v7 identifiers
* UTC timestamps (ISO 8601)
* Idempotent profile creation

### Advanced Query Engine (Stage 2)

* Multi-condition filtering
* Sorting (asc/desc)
* Pagination (page & limit)
* Natural language query parsing

---

## Database Schema

| Field               | Type       | Description                 |
| ------------------- | ---------- | --------------------------- |
| id                  | UUID v7    | Primary key                 |
| name                | VARCHAR    | Unique name                 |
| gender              | VARCHAR    | male/female                 |
| gender_probability  | FLOAT      | Confidence score            |
| age                 | INT        | Predicted age               |
| age_group           | VARCHAR    | child/teenager/adult/senior |
| country_id          | VARCHAR(2) | ISO country code            |
| country_name        | VARCHAR    | Full country name           |
| country_probability | FLOAT      | Confidence score            |
| created_at          | TIMESTAMP  | UTC ISO 8601                |

---

## API Endpoints

### 1. Create Profile

**POST /api/profiles**

```json
{
  "name": "ella"
}
```

---

### 2. Get Profiles (Advanced Querying)

**GET /api/profiles**

#### Supported Filters

| Parameter               | Description                    |
| ----------------------- | ------------------------------ |
| gender                  | male/female                    |
| age_group               | child, teenager, adult, senior |
| country_id              | ISO code                       |
| min_age                 | Minimum age                    |
| max_age                 | Maximum age                    |
| min_gender_probability  | Min confidence                 |
| min_country_probability | Min confidence                 |

#### Example

```
/api/profiles?gender=male&country_id=NG&min_age=25
```

---

### Sorting

| Parameter | Values                              |
| --------- | ----------------------------------- |
| sort_by   | age, created_at, gender_probability |
| order     | asc, desc                           |

Example:

```
/api/profiles?sort_by=age&order=desc
```

---

### Pagination

| Parameter | Default | Max |
| --------- | ------- | --- |
| page      | 1       | —   |
| limit     | 10      | 50  |

Response:

```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 2026,
  "data": []
}
```

---

## Natural Language Search

**GET /api/profiles/search?q=...**

---

### Examples

| Query                  | Interpretation                              |
| ---------------------- | ------------------------------------------- |
| young males            | gender=male, age 16–24                      |
| females above 30       | gender=female, min_age=30                   |
| people from nigeria    | country_id=NG                               |
| adult males from kenya | gender=male, age_group=adult, country_id=KE |

---

### Example Request

```
/api/profiles/search?q=young males from nigeria
```

---

### Error Case

```json
{
  "status": "error",
  "message": "Unable to interpret query"
}
```

---

## Validation Rules

* Invalid numeric values → **422**
* Missing parameters → **400**
* Invalid queries → **error response**
* limit > 50 → automatically clamped

---

## Idempotency

Submitting the same name twice will not create duplicates.

```json
{
  "status": "success",
  "message": "Profile already exists",
  "data": {}
}
```

---

## External APIs Used

* Genderize
* Agify
* Nationalize

---

## Tech Stack

* Django
* Django REST Framework
* SQLite
* PythonAnywhere (deployment)

---

## Setup Instructions

```bash
git clone https://github.com/debazz4/your-repo.git
cd your-repo

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

---

## Data Seeding

Seed the database with provided dataset:

```bash
python manage.py seed_profiles **(you can --reset flag if you want to clear db first)
```

* Safe to re-run (no duplicates)
* Uses `get_or_create`

---

## Performance Considerations

* Indexed fields: gender, country_id, age
* Query filtering before pagination
* Limit capped at 50
* Efficient slicing used for pagination

---

## Additional Requirements Met

* CORS enabled (`Access-Control-Allow-Origin: *`)
* UUID v7 IDs
* UTC timestamps (ISO 8601)
* Consistent response structure

---

## Status

✔ Stage 1 Completed (100/100)
✔ Stage 2 Ready for Submission

---

## Author

**Adebola Ajewole**

GitHub: https://github.com/debazz4
