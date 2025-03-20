#!/bin/bash

# Define project name
PROJECT_NAME="natural-news-vip-login"

# Create main project directory
mkdir -p $PROJECT_NAME/app/{api/routes,core,models,schemas,services}

# Create test directory
mkdir -p $PROJECT_NAME/tests

# Create essential files
touch $PROJECT_NAME/app/api/routes/__init__.py
touch $PROJECT_NAME/app/api/routes/users.py
touch $PROJECT_NAME/app/api/routes/items.py
touch $PROJECT_NAME/app/api/dependencies.py

touch $PROJECT_NAME/app/core/__init__.py
touch $PROJECT_NAME/app/core/config.py
touch $PROJECT_NAME/app/core/security.py

touch $PROJECT_NAME/app/models/__init__.py
touch $PROJECT_NAME/app/models/user.py
touch $PROJECT_NAME/app/models/item.py

touch $PROJECT_NAME/app/schemas/__init__.py
touch $PROJECT_NAME/app/schemas/user.py
touch $PROJECT_NAME/app/schemas/item.py

touch $PROJECT_NAME/app/services/__init__.py
touch $PROJECT_NAME/app/services/user_service.py
touch $PROJECT_NAME/app/services/item_service.py

touch $PROJECT_NAME/app/database.py
touch $PROJECT_NAME/app/main.py

touch $PROJECT_NAME/tests/__init__.py
touch $PROJECT_NAME/tests/test_users.py
touch $PROJECT_NAME/tests/test_items.py

# Create root files
touch $PROJECT_NAME/.env
touch $PROJECT_NAME/.gitignore
touch $PROJECT_NAME/requirements.txt
touch $PROJECT_NAME/README.md

echo "✅ FastAPI project structure created successfully in '$PROJECT_NAME'."
