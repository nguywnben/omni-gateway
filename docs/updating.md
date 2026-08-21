# Updating Omni Gateway

Update only after the console reports that a newer version is available. Replace `<version>` with the version shown in the console, such as `1.3.1`, and back up the persistent data directory before changing a production deployment.

## Docker

Pull the reported release image, then replace the container using the same port, environment variables, and volume mounts as the current deployment:

```bash
sudo docker pull nguywnben/omni-gateway:<version>
sudo docker stop omni-gateway
sudo docker rm omni-gateway
```

Run the original `docker run` command again. Keep the existing credential and log mounts. For example:

```bash
sudo docker run -d \
  --name omni-gateway \
  --restart unless-stopped \
  -p 4283:4283 \
  -v /opt/omni-gateway/creds:/app/backend/data/creds \
  -v /opt/omni-gateway/logs:/app/backend/data/logs \
  nguywnben/omni-gateway:<version>
```

## Docker Compose

From the cloned repository, pull the reported image and recreate the service:

```bash
IMAGE=nguywnben/omni-gateway:<version> docker compose -f deploy/docker-compose.yml pull
IMAGE=nguywnben/omni-gateway:<version> docker compose -f deploy/docker-compose.yml up -d
```

If the compose files changed in the release, update the repository first:

```bash
git pull --ff-only origin main
IMAGE=nguywnben/omni-gateway:<version> docker compose -f deploy/docker-compose.yml pull
IMAGE=nguywnben/omni-gateway:<version> docker compose -f deploy/docker-compose.yml up -d
```

## Verify The Update

Confirm that the container is running and the service is healthy:

```bash
sudo docker ps --filter name=omni-gateway
curl -fsS http://127.0.0.1:4283/health
```

The health endpoint should return `{"status":"ok"}`. Open the About page afterwards to confirm the new version.

## Roll Back

If the new image does not start correctly, run the same deployment command with the previously working image tag, such as `nguywnben/omni-gateway:1.2.1`. Persistent credentials, configuration, usage data, and logs remain intact as long as the existing mounted directories are preserved.
