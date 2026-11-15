# SPARC Ambassador Application 2026

A standalone Django web application built for **SPARC 2026 Ambassador Recruitment**. It provides a responsive, theme-aware application portal backed by PostgreSQL for persistent applicant storage and an isolated asynchronous Gmail API pipeline for automated confirmation emails.

---

## Table of Contents

- [SPARC Ambassador Application 2026](#sparc-ambassador-application-2026)
  - [Table of Contents](#table-of-contents)
  - [System Architecture \& Workflow](#system-architecture--workflow)
  - [Key Features](#key-features)
  - [Project Structure](#project-structure)
  - [Prerequisites \& Installation](#prerequisites--installation)
  - [PostgreSQL Database Setup](#postgresql-database-setup)
  - [Environment Variables (`.env`)](#environment-variables-env)
  - [Google Cloud \& Gmail API OAuth 2.0 Setup](#google-cloud--gmail-api-oauth-20-setup)
  - [Running the Application \& Authorizing Gmail](#running-the-application--authorizing-gmail)
  - [CLI Management Commands](#cli-management-commands)
    - [Retry Pending or Failed Emails](#retry-pending-or-failed-emails)
  - [Running Automated Tests](#running-automated-tests)
  - [Production Deployment Checklist](#production-deployment-checklist)

---

## System Architecture & Workflow

The codebase separates applicant intake (`applications`) from outbound email delivery (`emails`) so that external API timeouts, expired tokens, or network interruptions never block or roll back a valid application submission.

```text
Applicant Submits Form (/apply/)
        │
        ▼
Django Validates Data & Saves AmbassadorApplications Row (PostgreSQL)
        │
        ▼
Creates MailJob Row (status="pending") Inside Atomic Transaction
        │
        ├──► Immediately Redirects Applicant to Confirmation Page (/success/)
        │
        └──► transaction.on_commit() Spawns Background Worker Thread
                    │
                    ▼
             Builds Multipart MIME Email (HTML + Plain Text)
                    │
                    ▼
             Dispatches via Gmail API (users.messages.send)
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
  status="sent"         status="failed"
  (Saves Message ID)    (Records Error; Recoverable via `send_pending`)
```

---

## Key Features

- **Portal Landing & Navigation (`/`):** Clean welcome interface with quick navigation to the public application form (`/apply/`) and the staff review interface (`/admin/`).
- **Sitewide Light & Dark Theme:** Top-right theme switcher with `localStorage` persistence and synchronous `<head>` initialization to prevent flash-of-unstyled-content (FOUC) across page loads.
- **Comprehensive Form & Server-Side Validation (`/apply/`):**
  - **Personal & University Details:** Enforces required fields, valid date-of-birth formatting, and case-insensitive email uniqueness.
  - **Conditional IEEE Membership Fields:** Dynamically reveals membership number, grade, student branch, and optional branch position in the UI while enforcing conditional requirements server-side.
  - **Formal Photograph Upload:** Validates allowed extensions (`JPG`, `JPEG`, `PNG`), authenticates image headers via `Pillow`, enforces the `10 MB` maximum upload ceiling, provides client-side thumbnail previews, and stores files under UUID-generated filenames.
  - **Website Biography:** Enforces the `50`-word maximum limit via both a live client-side word counter and server-side validators.
  - **Activities & Mandatory Declarations:** Stores multi-select outreach activities in a PostgreSQL `JSONField` (`jsonb`) and requires all four applicant agreements before submission.
- **Asynchronous Gmail API Delivery (`emails` app):**
  - **Idempotent Queueing:** Enforces a database `UniqueConstraint` per `(campaign, application)` on `MailJob` to prevent duplicate emails.
  - **OAuth 2.0 Web Server Flow with PKCE:** Staff-restricted authorization endpoints (`/init/oauth2/` and `/init/oauth2callback`) persist credentials to `token.json` and refresh expired access tokens automatically.
  - **Privacy-Safe Templates:** Sends multipart inline-styled HTML and plain-text confirmation emails while omitting sensitive identifiers (date of birth, student ID, and WhatsApp number).
- **Centralized Configuration:** All field lengths, upload thresholds, word limits, choices, and OAuth parameters are centralized in `sparc_ambassador_form/settings.py`, `applications/constants.py`, and `emails/constants.py`.

---

## Project Structure

```text
sparc-form/
├── manage.py
├── requirements.txt
├── .env                          # Local environment secrets (gitignored)
├── token.json                    # Generated Gmail OAuth token (gitignored)
├── .gitignore
├── sparc_ambassador_form/        # Core Django project configuration
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── applications/                 # Applicant intake, validation & portal views
│   ├── admin.py
│   ├── constants.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   ├── views.py
│   └── migrations/
├── emails/                       # Gmail OAuth, MailJob queue & retry CLI
│   ├── admin.py
│   ├── constants.py
│   ├── google_auth.py
│   ├── models.py
│   ├── sender.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── management/
│   │   └── commands/
│   │       └── send_pending.py
│   ├── migrations/
│   └── templates/
│       └── emails/
│           ├── ambassador_received.html
│           └── ambassador_received.txt
├── templates/                    # Shared site templates
│   ├── base.html
│   └── applications/
│       ├── welcome.html
│       ├── apply.html
│       └── success.html
├── static/                       # CSS & Vanilla JavaScript assets
│   └── applications/
│       ├── css/
│       │   └── form.css
│       └── js/
│           ├── form.js
│           └── theme.js
└── media/                        # User-uploaded formal photographs
    └── ambassador_photos/
```

---

## Prerequisites & Installation

- **Python:** 3.12+
- **PostgreSQL:** 14+

1. **Clone the repository and enter the project directory:**

   ```bash
   git clone https://github.com/D34D5H0T03/sparc-ambassador-form.git
   cd sparc-form
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install all project dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## PostgreSQL Database Setup

Create a dedicated PostgreSQL role and database for the recruitment portal:

```bash
sudo -u postgres psql
```

Execute the following SQL commands inside `psql`:

```sql
CREATE USER sparc_app WITH PASSWORD 'sparc123';
ALTER USER sparc_app CREATEDB;
CREATE DATABASE sparc_ambassador OWNER sparc_app;
\q
```

> **Note:** Granting `CREATEDB` allows `sparc_app` to create and tear down the isolated `test_sparc_ambassador` database when running `python3 manage.py test`.

---

## Environment Variables (`.env`)

Create a `.env` file in the project root directory (alongside `manage.py`) with the following variables:

```env
# Django Core
SECRET_KEY=replace-with-a-strong-random-secret-key
DEBUG=True

# PostgreSQL Database
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=127.0.0.1
DB_PORT=5432

# Google Cloud & Gmail API
DEV_GOOGLE_CLOUD_CLIENT_ID=your-client-id.apps.googleusercontent.com
DEV_GOOGLE_CLOUD_CLIENT_SECRET=your-client-secret
DEV_GOOGLE_CLOUD_PROJECT_ID=your-project-id
DEV_SCOPES=https://www.googleapis.com/auth/gmail.send

GOOGLE_MAIL_API_NAME=gmail
GOOGLE_MAIL_API_VERSION=v1

SITE_URL=http://localhost:8000
MAIL_SENDER=SPARC Ambassador <your-sending-account@gmail.com>
```

---

## Google Cloud & Gmail API OAuth 2.0 Setup

1. Open [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. Navigate to **APIs & Services → Library**, search for **Gmail API**, and click **Enable**.
3. Open **Google Auth Platform → Audience** (or **OAuth consent screen**):
   - Select **External** user type and keep the publishing status in **Testing**.
   - Under **Data Access / Scopes**, add `https://www.googleapis.com/auth/gmail.send`.
   - Under **Test users**, add the exact Gmail address configured in `MAIL_SENDER`.
4. Open **Google Auth Platform → Clients** (or **APIs & Services → Credentials**):
   - Click **Create client → OAuth client ID** and select **Web application**.
   - Under **Authorized redirect URIs**, add:
     ```text
     http://localhost:8000/init/oauth2callback
     ```
   - Copy the generated **Client ID**, **Client Secret**, and **Project ID** into your `.env` file.

---

## Running the Application & Authorizing Gmail

1. **Apply database migrations and create a staff superuser:**

   ```bash
   python3 manage.py migrate
   python3 manage.py createsuperuser
   ```

2. **Start the development server:**

   ```bash
   python3 manage.py runserver
   ```

3. **Authorize the sending Gmail account (one-time setup):**
   - Open `http://localhost:8000/admin/` in your browser and sign in with your superuser account. *(Use `localhost` rather than `127.0.0.1` so session cookies match the OAuth redirect URI.)*
   - Visit `http://localhost:8000/init/oauth2/`.
   - Sign in with the whitelisted sending Gmail account and grant permission to send mail.
   - Upon redirect to `/init/oauth2callback`, Django saves the access and refresh tokens to `token.json`.

4. **Access the portal:**
   - **Welcome Page:** `http://localhost:8000/`
   - **Application Form:** `http://localhost:8000/apply/`
   - **Admin Dashboard:** `http://localhost:8000/admin/`

> **Testing Mode Token Expiration:** While your Google Cloud app remains in **Testing** status, Google expires refresh tokens after **7 days**. If `MailJob` logs report that re-authorization is required, repeat step 3 and run `python3 manage.py send_pending`.

---

## CLI Management Commands

### Retry Pending or Failed Emails

If an email fails due to a transient network outage, server restart, or expired token, re-process all `pending` and `failed` jobs synchronously using:

```bash
python3 manage.py send_pending
```

To resume processing starting from a specific application primary key:

```bash
python3 manage.py send_pending --from-id 10
```

Already `sent` jobs are automatically skipped so applicants never receive duplicate confirmation emails.

---

## Running Automated Tests

Run the full unit and integration test suites for both `applications` and `emails`:

```bash
python3 manage.py test
```

If your PostgreSQL user does not hold `CREATEDB` permissions and `test_sparc_ambassador` was pre-created manually, run:

```bash
python3 manage.py test --keepdb
```

---

## Production Deployment Checklist

- Set `DEBUG=False` and configure `ALLOWED_HOSTS` in `sparc_ambassador_form/settings.py`.
- Update `SITE_URL` in `.env` to your public HTTPS domain (e.g., `https://sparc.example.com`).
- Register `https://<your-domain>/init/oauth2callback` under **Authorized redirect URIs** in Google Cloud Console.
- Place the official logo asset at `static/images/SPARC26LogoMin.png` so public email templates render the header logo.
- Configure your reverse proxy (Nginx/Caddy) to serve `STATIC_ROOT` and protect `MEDIA_ROOT` appropriately.