# Build stage
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Set API URL for production build
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

# Build
RUN npm run build

# Production stage - serve with nginx
FROM nginx:alpine

# Copy custom nginx config
COPY --from=build /app/dist /usr/share/nginx/html

# Create nginx config for SPA routing
RUN echo 'server { \
    listen 80; \
    listen [::]:80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location /api { \
        proxy_pass ${BACKEND_URL}; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf.template

# Use PORT env variable from Railway
ENV PORT=80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
