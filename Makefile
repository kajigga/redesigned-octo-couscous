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

.PHONY: deploy deploy-backend deploy-frontend build-frontend bump-backend bump-frontend

setup-frontend:
	cd frontend ; \
	npm install 

build-frontend:
	cd frontend && npm ci && \
	  VITE_API_BASE_URL=https://orders.pizza42.bongawonga.com \
	  VITE_GIT_SHA=$$(git rev-parse --short HEAD) \
	  npm run build

deploy-backend:
	rsync $(RSYNC_OPTS) backend/ $(ARM_HOST):$(REMOTE_DIR)/backend/
	scp backend/.env $(ARM_HOST):$(REMOTE_DIR)/backend.env
	ssh $(ARM_HOST) "echo GIT_SHA=$$(git rev-parse --short HEAD) >> $(REMOTE_DIR)/backend.env"
	ssh $(ARM_HOST) "chmod 600 $(REMOTE_DIR)/backend.env"
	ssh $(ARM_HOST) "cd /root && docker compose build pizza42-backend && docker compose up -d pizza42-backend"

deploy-frontend: build-frontend
	rsync -avz --delete frontend/dist/ $(ARM_HOST):$(REMOTE_DIR)/frontend/dist/
	rsync -avz frontend/nginx.conf $(ARM_HOST):$(REMOTE_DIR)/frontend/nginx.conf
	scp frontend/.env.production $(ARM_HOST):$(REMOTE_DIR)/frontend/.env.production
	ssh $(ARM_HOST) "docker compose up -d pizza42-frontend"

deploy-frontend-image:
	rsync -avz --delete --exclude node_modules --exclude dist --exclude '.env.*' frontend/ $(ARM_HOST):$(REMOTE_DIR)/frontend/
	ssh $(ARM_HOST) "cd /root && docker compose build pizza42-frontend && docker compose up -d pizza42-frontend"

run-frontend:
	cd frontend; npm run dev

run-backend:
	cd backend; uv run python -m app

deploy: deploy-backend deploy-frontend

bump-backend:
	@cd backend && uv version --bump $${PART:-patch} --no-sync

bump-frontend:
	@cd frontend && npm version $${PART:-patch} --no-git-tag-version
