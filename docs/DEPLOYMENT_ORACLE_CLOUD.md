# Scarda Deployment Guide — Oracle Cloud Always Free

This guide deploys the full Scarda stack (TimescaleDB + Backend + Frontend + Mock FusionSolar)
on a single Oracle Cloud Always Free VM at **zero cost**, with automatic HTTPS.

## Architecture

```
Internet (HTTPS)
      │
      ▼
┌──────────────────────────────────────────┐
│  Oracle Cloud ARM VM (Always Free)       │
│  4 OCPU / 24 GB RAM / 200 GB disk        │
│                                          │
│  Docker Compose:                         │
│  ├── Caddy (port 80/443) — auto HTTPS    │
│  ├── TimescaleDB (internal only)         │
│  ├── Scarda Backend (port 8000 internal) │
│  ├── Scarda Frontend (nginx, internal)   │
│  └── Mock FusionSolar (internal)         │
└──────────────────────────────────────────┘
```

The database is **not exposed to the internet** — only Caddy (ports 80 + 443) is public.

---

## Step 1: Get an Oracle Cloud Account

1. Go to https://www.oracle.com/cloud/free/
2. Sign up (requires a credit card for verification, but you will **not be charged**)
3. Choose a region close to you (e.g. ap-mumbai-1 for South Asia, eu-frankfurt-1 for Europe)

---

## Step 2: Create an Always Free ARM VM

1. Go to **Compute → Instances → Create Instance**
2. Set these values:
   - **Name**: `scarda`
   - **Image**: Canonical Ubuntu 22.04 (click "Change image" if it's not Ubuntu)
   - **Shape**: Click "Change shape" → **Ampere** → `VM.Standard.A1.Flex`
   - **Shape config**: 4 OCPU, 24 GB RAM (this is within the free tier)
   - **SSH key**: Generate or upload your SSH public key (you need this to log in)
   - **Boot volume**: Leave defaults (47 GB is fine, or increase to 200 GB)
3. Click **Create**

Wait ~2 minutes for the VM to be provisioned. Note the **Public IP Address**.

---

## Step 3: Open Firewall Ports

By default, Oracle Cloud blocks all inbound traffic. You need to open ports 80 and 443.

### In the Oracle Cloud Console:

1. Go to **Networking → Virtual Cloud Networks**
2. Click your VCN (named `Default VCN` or similar)
3. Click **Security Lists** → your default security list
4. Click **Add Ingress Rules** and add two rules:

| Source CIDR | IP Protocol | Destination Port | Description |
|-------------|-------------|------------------|-------------|
| 0.0.0.0/0   | TCP         | 80               | HTTP        |
| 0.0.0.0/0   | TCP         | 443               | HTTPS       |

---

## Step 4: Point Your Domain

1. In your DNS provider (Cloudflare, GoDaddy, etc.), create an **A record**:
   - **Name**: `scarda` (or `@` for root domain)
   - **Value**: your VM's public IP
   - **TTL**: Auto

2. If using Cloudflare, set the record to **DNS only** (grey cloud) initially.
   Caddy needs to talk to Let's Encrypt directly to obtain certificates.
   You can enable the orange cloud (proxy) later if desired.

---

## Step 5: SSH Into the VM and Set Up

```bash
# Connect (replace with your VM's public IP and SSH key path)
ssh -i ~/.ssh/your-key ubuntu@YOUR_VM_PUBLIC_IP
```

### Install Docker:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
# Log out and back in for the docker group to take effect
exit
ssh -i ~/.ssh/your-key ubuntu@YOUR_VM_PUBLIC_IP
```

Verify:
```bash
docker --version
docker compose version
```

### Clone the repositories:

```bash
git clone https://github.com/yasithnirmal88/Scarda.git
git clone https://github.com/yasithnirmal88/mock-fusionsolar.git
# mock-fusionsolar must be a sibling directory of Scarda
```

The directory structure should be:
```
/home/ubuntu/
├── Scarda/
│   ├── docker-compose.prod.yml
│   ├── Caddyfile
│   ├── .env.production.example
│   ├── backend/
│   └── frontend/
└── mock-fusionsolar/
    └── Dockerfile
```

---

## Step 6: Configure Environment

```bash
cd Scarda
cp .env.production.example .env.production
nano .env.production
```

Set these critical values:

```bash
# Your domain (must match DNS A record)
DOMAIN=scarda.yourdomain.com

# Strong database password
DB_PASSWORD=use_a_strong_random_password

# Strong JWT secret (generate with: openssl rand -hex 32)
SECRET_KEY=paste_output_of_openssl_rand_here

# CORS — your frontend URL
CORS_ORIGINS=https://scarda.yourdomain.com
```

Leave `HUAWEI_BASE_URL=http://mock:8001` for now — the mock provides test data.

---

## Step 7: Launch the Stack

```bash
cd Scarda
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

This will:
1. Build the backend, frontend, and mock Docker images
2. Start TimescaleDB
3. Run Alembic migrations automatically on startup
4. Start the live data scheduler (polls mock every 10 minutes)
5. Start Caddy (obtains HTTPS certificate automatically)

Check status:
```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f backend
```

Wait for the backend log to show:
```
Application startup complete.
```

---

## Step 8: Verify

### Backend health:
```bash
curl -k https://scarda.yourdomain.com/api/health
```

### Check the database:
```bash
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d solar_aim -c \
  "SELECT COUNT(*) FROM string_readings;"
```

### Open the frontend:
Navigate to `https://scarda.yourdomain.com` in your browser.

---

## Step 9: Backfill Historical Data

The backend runs a 90-day backfill on startup by default (`HISTORICAL_BACKFILL_ON_STARTUP=true`).
This takes a few minutes. Watch the logs:

```bash
docker compose -f docker-compose.prod.yml logs -f backend | grep -i "backfill"
```

After backfill completes, verify the data:
```bash
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d solar_aim -c \
  "SELECT COUNT(*), MIN(recorded_at), MAX(recorded_at) FROM string_readings;"
```

After the first successful backfill, set `HISTORICAL_BACKFILL_ON_STARTUP=false` in `.env.production`
to avoid re-running it on every restart.

---

## Operations

### View logs:
```bash
docker compose -f docker-compose.prod.yml logs -f
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f mock
```

### Restart a service:
```bash
docker compose -f docker-compose.prod.yml restart backend
```

### Update to latest code:
```bash
cd Scarda
git pull
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

### Stop everything:
```bash
docker compose -f docker-compose.prod.yml down
```

### Database backup (set up as a daily cron job):
```bash
# Add to crontab: 0 3 * * * (runs at 3 AM daily)
docker compose -f /home/ubuntu/Scarda/docker-compose.prod.yml exec -T db \
  pg_dump -U postgres solar_aim | gzip > /home/ubuntu/backups/scarda_$(date +\%Y\%m\%d).sql.gz

# Keep only the last 30 days of backups
find /home/ubuntu/backups/ -name "scarda_*.sql.gz" -mtime +30 -delete
```

---

## Switching to Real Huawei API (Future)

When you have real Huawei credentials:

1. Edit `.env.production`:
   ```bash
   HUAWEI_BASE_URL=https://real-huawei-api-url
   HUAWEI_USERNAME=real_username
   HUAWEI_PASSWORD=real_password
   HUAWEI_PLANT_CODE=real_plant_code
   ```

2. Remove the mock service from `docker-compose.prod.yml` (comment out the `mock:` block)

3. Restart:
   ```bash
   docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
   ```

4. Run a fresh backfill if you set `HISTORICAL_BACKFILL_ON_STARTUP=true` temporarily

---

## Cost

| Resource | Free Tier Limit | Scarda Usage |
|----------|----------------|-------------|
| ARM VM   | 4 OCPU / 24 GB | 4 OCPU / 24 GB ✓ |
| Block storage | 200 GB | ~50 GB ✓ |
| Egress | 10 TB/month | < 10 GB/month ✓ |
| DNS | Free (Cloudflare) | 1 record ✓ |

**Total monthly cost: $0**

The only thing to watch: Oracle's free tier VMs can be reclaimed if the account is inactive
for extended periods. Log in to the Oracle Cloud console occasionally to keep it active.
