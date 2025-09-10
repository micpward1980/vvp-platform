FROM docker/compose:latest
WORKDIR /app
COPY . .
RUN apk add --no-cache docker-compose
EXPOSE 3000
CMD ["docker-compose", "up", "--build"]
