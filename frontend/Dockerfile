# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files (include lock file for reproducible builds)
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Set API URL for production build
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Build
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Create nginx config template with envsubst-safe variables
# Note: $uri and $host are nginx variables (keep as-is)
# BACKEND_URL is an env variable that gets substituted at startup
RUN cat > /etc/nginx/templates/default.conf.template << 'NGINX'
server {
    listen ${PORT};
    listen [::]:${PORT};
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;

    location /api {
        proxy_pass ${BACKEND_URL};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location /assets {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINX

# Railway provides PORT; default to 80
ENV PORT=80
ENV BACKEND_URL=http://localhost:8000

EXPOSE 80

# nginx:alpine image automatically processes /etc/nginx/templates/*.template
# using envsubst on startup, replacing ${PORT} and ${BACKEND_URL}
CMD ["nginx", "-g", "daemon off;"]
