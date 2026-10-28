# Healthcare Application Backend (Django & DRF)

A healthcare management REST API built with **Django**, **Django REST Framework (DRF)**, **SimpleJWT**, and **PostgreSQL**.



## 📁 Project Structure

```text
healthcare_project/
├── .env                              # Environment configuration (secrets & DB credentials)
├── .env.example                      # Template for environment configuration
├── .gitignore                        # Git ignore file
├── create_db.py                      # Python script to automatically create PostgreSQL database
├── manage.py                         # Django administrative CLI
├── requirements.txt                  # Python dependencies
├── README.md                         # Project documentation and Postman testing guide
│
├── healthcare_project/               # Main project configuration
│   ├── __init__.py
│   ├── asgi.py                       # ASGI configuration
│   ├── settings.py                   # Django settings (DB, DRF, JWT, python-dotenv)
│   ├── urls.py                       # Root URL routing (includes admin and /api/)
│   └── wsgi.py                       # WSGI configuration
│
└── api/                              # Application app
    ├── __init__.py
    ├── admin.py                      # Django admin panel configuration
    ├── apps.py                       # App configuration
    ├── backends.py                   # Authentication backend (email or username login)
    ├── models.py                     # Patient, Doctor, PatientDoctorMapping models
    ├── serializers.py                # DRF serializers with validation
    ├── views.py                      # ViewSets and APIViews
    ├── urls.py                       # DefaultRouter and endpoint routes
    ├── tests.py                      # Unit and integration test suite
    └── migrations/                   # Schema migrations
        ├── __init__.py
        └── 0001_initial.py           # Initial database migration
```

---

##  Required Dependencies (`requirements.txt`)

```text
Django>=4.2,<6.0
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.3.0
psycopg2-binary>=2.9.9
python-dotenv>=1.0.0
```

Install them with:
```bash
pip install -r requirements.txt
```

---

##  1. Setting Up the `.env` File

At the root of the project, a `.env` file is used to store sensitive settings and credentials.

### Example `.env` contents:

```env

# Healthcare Project Environment Configuration


# Django Secret Key and Debug Mode
SECRET_KEY=django-insecure-healthcare-system-development-secret-key-2026-safe-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Configuration (PostgreSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=missmago15
DB_HOST=localhost
DB_PORT=5432

# SimpleJWT Token Lifetimes
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=1
```

### Configuration Parameters Explained:
- **`SECRET_KEY`**: A unique secret key used by Django for cryptographic signing.
- **`DEBUG`**: Set to `True` for development, `False` for production.
- **`ALLOWED_HOSTS`**: Comma-separated list of host/domain names that this Django site can serve.
- **`DB_ENGINE`**: Set to `django.db.backends.postgresql`.
- **`DB_NAME`**: Name of the database (default: `healthcare_db`).
- **`DB_USER`**: Your local PostgreSQL username (default: `postgres`).
- **`DB_PASSWORD`**: Your local PostgreSQL password (e.g. `missmago15`).
- **`DB_HOST`**: Host where PostgreSQL is running (default: `localhost`).
- **`DB_PORT`**: Port where PostgreSQL is running (default: `5432`).

---

##  2. Database Creation & Running Migrations

### Step A: Create the Database
Because PostgreSQL requires `CREATE DATABASE` to run outside a transaction block (autocommit mode), run the included helper script:

```powershell
python create_db.py
```

This connects to your local PostgreSQL server, enables autocommit mode, checks if `healthcare_db` exists, and creates it if not.

### Step B: Run Django Migrations

Apply the database schema and create all necessary tables:

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Step C: (Optional) Create Superuser for Django Admin

```powershell
python manage.py createsuperuser
```

### Step D: Start the Server

```powershell
python manage.py runserver
```
The server will start at: `http://127.0.0.1:8000/`

---

## 📮 3. Testing the Endpoints Using Postman

**Base URL**: `http://127.0.0.1:8000/api/`

---

### Step 1: Register a New User
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/auth/register/`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (`raw` JSON):
```json
{
  "name": "Dr. John Doe",
  "email": "johndoe@example.com",
  "password": "StrongPassword123!"
}
```
- **Expected Status**: `201 Created`
- **Response**:
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "username": "johndoe@example.com",
    "email": "johndoe@example.com",
    "name": "Dr. John Doe"
  }
}
```

---

### Step 2: Log In & Obtain JWT Tokens
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/auth/login/`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (`raw` JSON):
```json
{
  "email": "johndoe@example.com",
  "password": "StrongPassword123!"
}
```
*(You can also use `"username"` instead of `"email"`)*
- **Expected Status**: `200 OK`
- **Response**:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

> **Important**: Copy the `access` token. In subsequent requests in Postman:
> 1. Go to the **Authorization** tab.
> 2. Select Type: **Bearer Token**.
> 3. Paste your token into the **Token** field.
> *(Or add header: `Authorization: Bearer <your_access_token>`)*

---

### Step 3: Doctor Management (`/api/doctors/`)

#### 3.1 Create a Doctor
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/doctors/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
  - `Content-Type: application/json`
- **Body** (`raw` JSON):
```json
{
  "name": "Gregory House",
  "specialty": "Diagnostic Medicine",
  "contact_info": "house@princeton.edu"
}
```
- **Expected Status**: `201 Created`

#### 3.2 List All Doctors
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/api/doctors/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `200 OK`

#### 3.3 Get Specific Doctor
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/api/doctors/1/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `200 OK`

#### 3.4 Update Doctor Details
- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8000/api/doctors/1/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
  - `Content-Type: application/json`
- **Body** (`raw` JSON):
```json
{
  "name": "Dr. Gregory House, M.D.",
  "specialty": "Nephrology & Infectious Disease",
  "contact_info": "house.md@princeton.edu"
}
```
- **Expected Status**: `200 OK`

#### 3.5 Delete Doctor Record
- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8000/api/doctors/1/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `204 No Content`

---

### Step 4: Patient Management (`/api/patients/`)
*Note: Users can only retrieve, update, or delete patients that they specifically created.*

#### 4.1 Create a Patient
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/patients/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
  - `Content-Type: application/json`
- **Body** (`raw` JSON):
```json
{
  "name": "Sarah Connor",
  "age": 35,
  "gender": "Female",
  "contact_info": "sarah.connor@cyberdyne.org"
}
```
- **Expected Status**: `201 Created`
- *(The `created_by` field is automatically populated with the authenticated user)*

#### 4.2 List Authenticated User's Patients
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/api/patients/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `200 OK`

#### 4.3 Get Specific Patient
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/api/patients/1/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `200 OK` *(or `404 Not Found` if created by another user)*

#### 4.4 Update Patient Details
- **Method**: `PUT`
- **URL**: `http://127.0.0.1:8000/api/patients/1/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
  - `Content-Type: application/json`
- **Body** (`raw` JSON):
```json
{
  "name": "Sarah Connor",
  "age": 36,
  "gender": "Female",
  "contact_info": "new.contact@cyberdyne.org"
}
```
- **Expected Status**: `200 OK`

#### 4.5 Delete Patient Record
- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8000/api/patients/1/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `204 No Content`

---

### Step 5: Patient-Doctor Mapping (`/api/mappings/`)

#### 5.1 Assign a Doctor to a Patient
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/mappings/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
  - `Content-Type: application/json`
- **Body** (`raw` JSON):
```json
{
  "patient_id": 1,
  "doctor_id": 1
}
```
- **Expected Status**: `201 Created`
- **Response**:
```json
{
  "id": 1,
  "patient": {
    "id": 1,
    "name": "Sarah Connor",
    "age": 36,
    "gender": "Female",
    "contact_info": "new.contact@cyberdyne.org",
    "created_by": "johndoe@example.com"
  },
  "doctor": {
    "id": 1,
    "name": "Dr. Gregory House, M.D.",
    "specialty": "Nephrology & Infectious Disease",
    "contact_info": "house.md@princeton.edu"
  },
  "assigned_at": "2026-10-28T10:00:00Z"
}
```

#### 5.2 Retrieve All Patient-Doctor Mappings
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/api/mappings/`
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `200 OK`

#### 5.3 Get All Doctors Assigned to a Specific Patient
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/api/mappings/1/`
*(where `1` is the `patient_id`)*
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `200 OK`
- **Response**:
```json
[
  {
    "id": 1,
    "name": "Dr. Gregory House, M.D.",
    "specialty": "Nephrology & Infectious Disease",
    "contact_info": "house.md@princeton.edu",
    "created_at": "2026-10-28T10:00:00Z",
    "updated_at": "2026-10-28T10:00:00Z"
  }
]
```

#### 5.4 Remove a Doctor from a Patient
- **Method**: `DELETE`
- **URL**: `http://127.0.0.1:8000/api/mappings/1/`
*(where `1` is the `mapping_id`)*
- **Headers**:
  - `Authorization: Bearer <your_access_token>`
- **Expected Status**: `200 OK`
- **Response**:
```json
{
  "message": "Successfully unassigned Dr. Gregory House, M.D. from patient Sarah Connor."
}
```

---

##  4. Running the Automated Test Suite

To verify all endpoints, permissions, serializers, and models:

```powershell
python manage.py test api
```
