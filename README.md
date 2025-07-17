# Bitespeed Backend Task: Identity Reconciliation Service

This repository contains the solution for the Bitespeed Backend Developer Task. It's a Django-based web service designed to identify and consolidate customer contact information.

## Live Endpoint

The `/identify` endpoint is hosted on Railway and is publicly accessible:

**URL:** `https://bitespeed-identity-reconciliation-production-dca9.up.railway.app/identify/`

## Tech Stack

- **Framework:** Django
- **Language:** Python
- **Database:** PostgreSQL (via `dj-database-url`)
- **WSGI Server:** Gunicorn
- **Static Files:** WhiteNoise
- **Deployment:** Railway.app

---

## Project Overview

The core of this application is the `/identify` API endpoint. It receives customer contact information (email and/or phone number) and consolidates it according to a set of rules:

1.  **New Contact:** If the contact information is entirely new, a "primary" contact record is created.
2.  **Existing Contact:** If the information matches an existing contact, the service returns all linked information (all emails, all phone numbers) associated with that identity.
3.  **New Information for Existing Contact:** If the request contains new information linked to an existing identity (e.g., a new email for a known phone number), a "secondary" contact record is created and linked to the primary one.
4.  **Merging Identities:** If a request links two previously separate "primary" contacts, the older one remains "primary," and the newer one is updated to "secondary" status, effectively merging the two identities.

The logic ensures that all related contact entries for a single person are linked to a single, oldest "primary" contact.

---

## Local Setup and Installation

To run this project on your local machine, follow these steps:

**Prerequisites:**
- Python 3.11+
- `pip` and `venv`

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd bitespeed-identity-reconciliation
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Create a `.env` file in the project root directory. You will need a PostgreSQL database. You can easily create one for free on Railway or use a local installation.

    ```.env
    SECRET_KEY='your-strong-django-secret-key'
    DATABASE_PUBLIC_URL='postgres://user:password@host:port/dbname'
    ```

5.  **Run Database Migrations**
    This command will create the `Contact` table in your database.
    ```bash
    python manage.py migrate
    ```

6.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

---

## API Endpoint: `/identify`

- **Method:** `POST`
- **Content-Type:** `application/json`

### Request Body

```json
{
	"email": "mcfly@hillvalley.edu",
	"phoneNumber": "123456"
}
```
*Note: At least one of `email` or `phoneNumber` must be provided.*

### Example `curl` Request

```bash
curl -X POST https://bitespeed-identity-reconciliation-production-dca9.up.railway.app/identify/ \
  -H "Content-Type: application/json" \
  -d '{
        "email": "george@hillvalley.edu",
        "phoneNumber": "717171"
      }'
```

### Success Response (200 OK)

The response contains a consolidated view of the contact's identity.

```json
{
    "contact": {
        "primaryContactId": 11,
        "emails": ["george@hillvalley.edu", "biffsucks@hillvalley.edu"],
        "phoneNumbers": ["919191", "717171"],
        "secondaryContactIds": [27]
    }
}
```