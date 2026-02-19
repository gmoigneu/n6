# Qdrant + Tailscale on Ubuntu VPS

Self-hosted Qdrant for N6's memory system, secured behind Tailscale with API key auth.

---

## 1. Install Tailscale

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Follow the auth link it prints. Once connected, note your VPS Tailscale IP — you'll need it in `~/.n6.toml` on each client machine:

```bash
tailscale ip -4
```

Verify auto-start is enabled (the installer sets this up, but confirm):

```bash
sudo systemctl enable --now tailscaled
```

---

## 2. Install Qdrant

**Create a dedicated user and directories:**

```bash
sudo useradd --system --no-create-home --shell /usr/sbin/nologin qdrant
sudo mkdir -p /opt/qdrant /var/lib/qdrant /etc/qdrant
sudo chown qdrant:qdrant /var/lib/qdrant
```

**Download the binary:**


```bash
sudo apt install qdrant
```

---

## 3. Configure Qdrant

Generate a strong API key:

```bash
openssl rand -hex 32
```

Create `/etc/qdrant/config.yaml`:

```yaml
storage:
  storage_path: /var/lib/qdrant

service:
  host: 0.0.0.0
  http_port: 6333
  grpc_port: 6334

api_key: "your-strong-random-key-here"
```

Lock down the config file (it contains the API key):

```bash
sudo chown qdrant:qdrant /etc/qdrant/config.yaml
sudo chmod 600 /etc/qdrant/config.yaml
```

---

## 4. Create a systemd service

Create `/etc/systemd/system/qdrant.service`:

```ini
[Unit]
Description=Qdrant vector database
After=network.target

[Service]
Type=simple
User=qdrant
Group=qdrant
ExecStart=/usr/bin/qdrant --config-path /etc/qdrant/config.yaml
WorkingDirectory=/var/lib/qdrant
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/qdrant

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now qdrant
sudo systemctl status qdrant
```

---

## 5. Firewall — Tailscale only

Allow Qdrant **only** on the Tailscale interface, block it everywhere else:

```bash
sudo ufw allow ssh
sudo ufw allow in on tailscale0 to any port 6333
sudo ufw allow in on tailscale0 to any port 6334
sudo ufw enable
sudo ufw status
```

Verify access control:

```bash
# Should timeout or refuse (public internet)
curl --max-time 5 http://<public-vps-ip>:6333/healthz

# Should return Qdrant version JSON (Tailscale network)
curl http://<tailscale-ip>:6333/healthz
```

---

## 6. Configure N6

Add to `~/.n6.toml` on each client machine (must be on your Tailscale network):

```toml
qdrant_host = "100.x.x.x"       # your VPS Tailscale IP
qdrant_port = 6333
qdrant_api_key = "your-strong-random-key-here"
```

---

## Updating Qdrant

```bash
# Stop service, replace binary, restart
sudo systemctl stop qdrant
QDRANT_VERSION=vX.Y.Z
curl -L "https://github.com/qdrant/qdrant/releases/download/${QDRANT_VERSION}/qdrant-x86_64-unknown-linux-gnu.tar.gz" \
  | sudo tar -xz -C /opt/qdrant
sudo systemctl start qdrant
```

---

## Security summary

| Layer | What it does |
|---|---|
| Tailscale | Network perimeter — port 6333 unreachable from public internet |
| UFW | Enforces Tailscale-only at the OS firewall level |
| Qdrant API key | Second factor — a compromised tailnet device still can't write without the key |
| systemd hardening | Qdrant process cannot write outside `/var/lib/qdrant` |
