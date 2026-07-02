ARM_HOST = arm
REMOTE_DIR = /root/pizza42

RSYNC_OPTS = -avz --delete \
	--exclude '.git' \
	--exclude 'node_modules' \
	--exclude '.venv' \
	--exclude 'dist' \
	--exclude '__pycache__' \
	--exclude '.pytest_cache' \
	--exclude '.env' \
	--exclude '.env.local' \
	--exclude '.env.*.local' \
	--exclude 'orders.db' \
	--exclude 'instance'

.PHONY: deploy deploy-backend deploy-frontend

deploy-backend:
	rsync $(RSYNC_OPTS) backend/ $(ARM_HOST):$(REMOTE_DIR)/backend/
	scp backend/.env $(ARM_HOST):$(REMOTE_DIR)/backend.env
	ssh $(ARM_HOST) "chmod 600 $(REMOTE_DIR)/backend.env"
	ssh $(ARM_HOST) "cd /root && docker compose build pizza42-backend && docker compose up -d pizza42-backend"

deploy-frontend:
	rsync $(RSYNC_OPTS) frontend/ $(ARM_HOST):$(REMOTE_DIR)/frontend/
	ssh $(ARM_HOST) "cd /root && docker compose build pizza42-frontend && docker compose up -d pizza42-frontend"

deploy: deploy-backend deploy-frontend
