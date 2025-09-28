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

## ⚒️ Dependencies

- Docker
- [uv (uv)](https://docs.astral.sh/uv/)

---

## 🚀 Quick Start

### 1. Copy the Template

Clone or copy this repository into your project directory.

### 2. Bootstrap the application

Run the following command to generate the required files for your app:

```bash
uv run tools/setup.py bootstrap <app_name>
```

### 3. Populate the generated files

Open the generated .env file and fill in any missing or required values, such as database credentials, secrets, ports, etc.

For prod environment, update domain in `provision/Caddyfile.prod`

### 4. Start containers

Use either `dev` or `prod` profiles to start containers:

```bash
docker compose --profile <profile> up -d --remove-orphans
```

### 5. Run initial migration

```bash
docker compose exec api make run-migration
```

### 6. Generating the system account

System accounts can manage system application settings.
To create one:

```bash
docker compose exec api make create-superuser
```

_Note: mentions on container `api` refer to the dev `api` container, if on production mode (e.g. `--profile prod`), use `pr-api` instead._

## 🧩 Development

### Running migrations

After defining custom model in `api/models/`, generate and migrate with alembic:

```bash
docker compose exec api make create-migration MESSAGE="$message"
```

### Generate API endpoint

After defining custom model in `api/models/`, bootstrap api endpoint with:

```bash
uv run tools/workflow.py generate-model-route <model_name>
```

To add authentication to each CRUD operation:

- `--create-login-required`: Require login for CREATE route
- `--read-login-required`: Require login for READ route
- `--update-login-required`: Require login for UPDATE route
- `--delete-login-required`: Require login for DELETE route

### Generate model factory

After defining custom model in `api/models/`, bootstrap model factory with:

```bash
uv run tools/workflow.py generate-model-factory <model_name>
```

### Seeding database from factory

Update factory file with defined custom list or override the random generator function.

After updating the factory file, run seeder with:

```bash
docker compose exec api uv run database/seeder.py seed-<mode>

modes:
    - random    # calls factory.random_generator
    - list      # calls factory.list_generator

Options:
  -n, --num     INTEGER     Seed n number of models
  --force                   Force save data if table has data
  --only        TEXT        Only seed specific models
  --help                    Show this message and exit.
```

### Testing

Run test under `testing/tests`

```bash
docker compose run --rm testing uv run pytest
```

Run specific test file

```bash
docker compose run --rm testing uv run pytest path/to/test_file.py

# Sample: docker compose run --rm testing uv run pytest tests/unit_tests/test_user.py
```

Run specific test case

```bash
docker compose run --rm testing uv run pytest path/to/test_file.py::test_case

# Sample: docker compose run --rm testing uv run pytest tests/unit_tests/test_auth.py::test_login_wrong_password
```

Testing uses pytest internally and any args would apply as well

_TODO: Add integration tests_

---

## 📈 Jaeger Tracing

This template supports distributed tracing using **Jaeger** for monitoring and debugging requests across services.

Jaeger is included as a service in the Docker Compose configuration and is accessible via:

```bash
# For dev environment
https://localhost/jaeger/

# For prod environment
https://<domain>/jaeger/
```

### Configuring Jaeger

During the bootstrap project process, the system would prompt for the jaeger authentication credentials. This process generates the required password hash for the basic_auth directive for `caddy`.

```bash
λ uv run tools\setup.py bootstrap sample
Jaeger username: admin
Jaeger password:
Repeat for confirmation:
```

If later on, you wish to update the jaeger authentication details, you can do so by editing `.env` and changing the variables:

- JAEGER_USER
- JAEGER_PASSWORD
- JAEGER_PASSWORD_HASH

But you have to manually generate the password hash via bcrypt.

A convenient tool is added to automatically generate the password hash and update the .env file via:

```bash
uv run tools\setup.py update-jaeger-credentials
```

## Project Structure (Summary)

```
.
├── api/                  # FastAPI backend code
├── provision/            # Provision files
├── testing/              # Testing files
├── tools/                # Management and setup scripts
├── web/                  # React Admin frontend
├── .env                  # Generated environment config
├── docker-compose.yaml   # Generated docker compose config

```
