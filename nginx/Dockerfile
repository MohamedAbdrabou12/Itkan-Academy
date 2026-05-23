# ── Stage 1: Build the React frontend ────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

# Accept build-time API URL
ARG VITE_APP_API_URL
ENV VITE_APP_API_URL=$VITE_APP_API_URL

COPY Itkan-Academy-FE/ .
RUN npm ci && npx vite build

# ── Stage 2: Serve with Nginx ────────────────────────────
FROM nginx:alpine

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY Itkan-Academy/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built frontend from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
