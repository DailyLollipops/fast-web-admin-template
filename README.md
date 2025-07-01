# 🧩 FastWeb Admin Web Template

A full-stack web application template featuring:

- ✅ **FastAPI** – high-performance backend
- 🗃️ **MySQL** – relational database
- 🧬 **SQLModel** – ORM for interacting with the DB
- 🔄 **Alembic** – database migrations
- 🔐 **Caddy** – automatic HTTPS and reverse proxy
- 🐳 **Docker** – containerized environment
- 🖥️ **React Admin** – frontend admin interface

---

## 🚀 Quick Start

### 1. Copy the Template

Clone or copy this repository into your project directory.

### 2. Generate Environment Config File

Run the following command to generate an `.env` file for your app:

```bash
python tools/manage.py generate-env <app_name>
```

### 3. Populate the `.env` File

Open the generated .env file and fill in any missing or required values, such as database credentials, secrets, ports, etc.

### 4. Generate Docker Compose File

After setting up your environment file, generate the `docker-compose.yaml` file:

```bash
python tools/manage.py generate-compose-file <app_name>
```

Replace <app_name> with the same name you used in step 2.

---

## 🧩 Development

### Running migrations

After defining custom model in `api/models/`, generate and migrate with alembic:

```bash
python tools\manage.py generate-model-route <model_name>
```

### Autogenerate API endpoint

After defining custom model in `api/models/`, bootstrap api endpoint with:

```bash
python tools\manage.py generate-model-route <model_name>
```

To add authentication to each CRUD operation:

- `--create-login-required`: Require login for CREATE route
- `--read-login-required`: Require login for READ route
- `--update-login-required`: Require login for UPDATE route
- `--delete-login-required`: Require login for DELETE route

---

## ⚒️ Additional Notes

- All configurations are environment-specific and customizable.
- The generated docker-compose.yaml will be tailored to your environment variables.
- Alembic migration setup is included and works with SQLModel.
- Caddy is configured for automatic TLS and reverse proxying to your FastAPI backend.

---

## Project Structure (Summary)

```
.
├── backend/              # FastAPI backend code
├── web/                  # React Admin frontend
├── tools/                # Management and setup scripts
├── docker/               # Docker-related files (Dockerfiles, Caddy configs)
├── .env                  # Generated environment config
├── docker-compose.yaml   # Generated docker compose config

```
