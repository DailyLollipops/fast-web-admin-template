# Create a new Alembic migration with a message passed via MESSAGE variable
# Usage: make create-migration MESSAGE="Add new users table"
create-migration:
	cd database && uv run alembic revision --autogenerate -m "$(MESSAGE)"

# Apply all migrations (upgrade database to latest revision)
run-migration:
	cd database && uv run alembic upgrade head

# Downgrade to a specific revision, "base", or steps (default 1 step)
# Usage:
#   make downgrade            			# downgrade 1 step
#   make downgrade TARGET=base   		# downgrade all migrations (to base)
#   make downgrade TARGET=ae1027a6acf  	# downgrade to specific revision
downgrade:
	cd database && uv run alembic downgrade $(TARGET)

create-superuser:
	uv run scripts/create_superuser.py

# Default TARGET to "-1" (one step) if not provided
TARGET ?= -1
