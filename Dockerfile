FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/claims-orchestrator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all services
COPY services/ ./services/
COPY web-ui/ ./web-ui/

# Create nginx config for web UI that uses PORT environment variable
RUN echo 'server {\n\
    listen ${PORT:-3000};\n\
    server_name localhost;\n\
    root /app/web-ui;\n\
    index index.html;\n\
    location / {\n\
        try_files $uri $uri/ @api;\n\
    }\n\
    location @api {\n\
        proxy_pass http://localhost:8000;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
    location /api/ {\n\
        proxy_pass http://localhost:8000/;\n\
        proxy_set_header Host $host;\n\
        proxy_set_header X-Real-IP $remote_addr;\n\
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n\
        proxy_set_header X-Forwarded-Proto $scheme;\n\
    }\n\
}' > /etc/nginx/sites-available/default

# Create supervisor config to run all services
RUN echo "[supervisord]\n\
nodaemon=true\n\
\n\
[program:claims-orchestrator]\n\
command=uvicorn src.main:app --host 0.0.0.0 --port 8000\n\
directory=/app/services/claims-orchestrator\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:verification-service]\n\
command=uvicorn src.main:app --host 0.0.0.0 --port 8001\n\
directory=/app/services/verification-service\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:valuation-service]\n\
command=uvicorn src.main:app --host 0.0.0.0 --port 8002\n\
directory=/app/services/valuation-service\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:payment-service]\n\
command=uvicorn src.main:app --host 0.0.0.0 --port 8003\n\
directory=/app/services/payment-service\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:vin-monitor]\n\
command=uvicorn src.main:app --host 0.0.0.0 --port 8004\n\
directory=/app/services/vin-monitor\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:audit-service]\n\
command=uvicorn src.main:app --host 0.0.0.0 --port 8005\n\
directory=/app/services/audit-service\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:nginx]\n\
command=nginx -g \"daemon off;\"\n\
autostart=true\n\
autorestart=true" > /etc/supervisor/conf.d/supervisord.conf

# Create startup script that substitutes PORT variable in nginx config
RUN echo '#!/bin/bash\n\
envsubst < /etc/nginx/sites-available/default > /etc/nginx/sites-available/default.tmp\n\
mv /etc/nginx/sites-available/default.tmp /etc/nginx/sites-available/default\n\
exec supervisord -c /etc/supervisor/conf.d/supervisord.conf' > /app/start.sh && chmod +x /app/start.sh

EXPOSE ${PORT:-3000}

CMD ["/app/start.sh"]
