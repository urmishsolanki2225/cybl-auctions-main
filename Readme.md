Here is your corrected and professionally formatted **Step-by-Step Backend Run Guide**, with proper sequencing, grammar, and technical accuracy:

---

### ✅ Backend Setup Guide

#### 1. Navigate to the Backend Directory

```bash
cd backend
```

---

#### 2. Create a Virtual Environment

```bash
python -m venv venv
```

---

#### 3. Activate the Virtual Environment

| Platform      | Command                    |
| ------------- | -------------------------- |
| Linux / macOS | `source venv/bin/activate` |
| Windows (CMD) | `venv\Scripts\activate`    |

---

#### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

#### 5. Update MySQL Configuration (Optional)

Update your `my.cnf` or `my.ini` file to enable required settings like `max_allowed_packet`, etc., if needed.

---

#### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

#### 7. Run the Django Development Server

```bash
python manage.py runserver 192.168.201.35:8000
```

---

#### 8. Run the Project with WebSocket Support (ASGI)

```bash
daphne -b 192.168.201.35 -p 8000 backend.asgi:application
```

---

#### 9. Start Celery for Automated Auction Start/End

**Option 1: Standard (WSL/Linux recommended)**

```bash

#run this First
    wsl -d Ubuntu
    sudo service redis-server start
#Verify it's running:
    redis-cli ping
    # Output should be: PONG


celery -A backend worker -l info
celery -A backend beat -l info
```

**Option 2: fallback WSL (Windows fallback)**

```bash
celery -A backend worker --pool=solo --loglevel=info
```

---

#### 10. Update `requirements.txt` After Installing New Packages

```bash
pip freeze > requirements.txt
```

---

### ✅ React Frontend (Vite)

Navigate to the frontend project and run:

```bash
npm run dev -- --host
```

---

Let me know if you'd like this saved as a markdown `.md` file or converted into a project `README.md` style.
