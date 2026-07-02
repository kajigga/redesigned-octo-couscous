.PHONY: setup-frontend build-frontend run-frontend run-backend bump-backend bump-frontend

setup-frontend:
	cd frontend ; \
	npm install 

build-frontend:
	cd frontend && npm ci && \
	  VITE_API_BASE_URL=https://orders.pizza42.bongawonga.com \
	  VITE_GIT_SHA=$$(git rev-parse --short HEAD) \
	  npm run build

run-frontend:
	cd frontend; npm run dev

run-backend:
	cd backend; uv run python -m app

bump-backend:
	@cd backend && uv version --bump $${PART:-patch} --no-sync

bump-frontend:
	@cd frontend && npm version $${PART:-patch} --no-git-tag-version
