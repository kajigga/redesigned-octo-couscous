FROM node:20-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_AUTH0_DOMAIN=bongawonga.us.auth0.com
ARG VITE_AUTH0_CLIENT_ID=hqvoam0pzpABmubbw2Hgq026cjctsfqP
ARG VITE_AUTH0_AUDIENCE=bongawonga-enterprises
ARG VITE_API_BASE_URL=https://orders.pizza42.bongawonga.com
RUN \
  echo "VITE_AUTH0_DOMAIN=${VITE_AUTH0_DOMAIN}" > .env.production && \
  echo "VITE_AUTH0_CLIENT_ID=${VITE_AUTH0_CLIENT_ID}" >> .env.production && \
  echo "VITE_AUTH0_AUDIENCE=${VITE_AUTH0_AUDIENCE}" >> .env.production && \
  echo "VITE_API_BASE_URL=${VITE_API_BASE_URL}" >> .env.production

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
