# ==============================================================================
# JurisAI Frontend Multi-Stage Dockerfile
# Stage 1: Build React/Vite single page app
# Stage 2: Serve optimized assets with Nginx alpine
# ==============================================================================

# Build Stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy dependency definitions
COPY package*.json ./
RUN npm ci

# Copy sources and compile
COPY . .
RUN npm run build

# Production Nginx Stage
FROM nginx:alpine

# Copy built dist files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration with reverse proxy for /api
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=20s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
