FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    nginx \\
    supervisor \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY services/claims-orchestrator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy all services
COPY services/ ./services/
COPY web-ui/ ./web-ui/

# Create nginx config
RUN echo 'server {\\n\\
    listen 3000;\\n\\
    root /app/web-ui;\\n\\
    index index.html;\\n\\
    location / { try_files $uri $uri/ =404; }\\n\\
    location /api/ {\\n\\
        proxy_pass http://localhost:8000/;\\n\\
        proxy_set_header Host $host;\\n\\
    }\\n\\
}' > /etc/nginx/sites-available/default

# Create supervisor config
RUN echo "[supervisord]\\n\\
nodaemon=true\\n\\
[program:claims-orchestrator]\\n\\
command=uvicorn src.main:app --host 0.0.0.0 --port 8000\\n\\
directory=/app/services/claims-orchestrator\\n\\
autostart=true\\n\\
[program:verification-service]\\n\\
command=uvicorn src.main:app --host 0.0.0.0 --port 8001\\n\\
directory=/app/services/verification-service\\n\\
autostart=true\\n\\
[program:valuation-service]\\n\\
command=uvicorn src.main:app --host 0.0.0.0 --port 8002\\n\\
directory=/app/services/valuation-service\\n\\
autostart=true\\n\\
[program:payment-service]\\n\\
command=uvicorn src.main:app --host 0.0.0.0 --port 8003\\n\\
directory=/app/services/payment-service\\n\\
autostart=true\\n\\
[program:vin-monitor]\\n\\
command=uvicorn src.main:app --host 0.0.0.0 --port 8004\\n\\
directory=/app/services/vin-monitor\\n\\
autostart=true\\n\\
[program:audit-service]\\n\\
command=uvicorn src.main:app --host 0.0.0.0 --port 8005\\n\\
directory=/app/services/audit-service\\n\\
autostart=true\\n\\
[program:nginx]\\n\\
command=nginx -g \\"daemon off;\\"\\n\\
autostart=true" > /etc/supervisor/conf.d/supervisord.conf

EXPOSE 3000
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
