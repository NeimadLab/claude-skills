
# Cloud Setup Guide

Deploy Loom on a remote server so cloud-based AI tools (Claude.ai, ChatGPT, Gemini, CI/CD pipelines) can access your project memory from anywhere.

## When You Need Remote Loom

| Scenario | Local | Remote |
|----------|:-----:|:------:|
| Claude Code on your laptop | ✅ | Not needed |
| Cursor on your laptop | ✅ | Not needed |
| Claude.ai in browser | ❌ | ✅ |
| ChatGPT with custom actions | ❌ | ✅ |
| Claude on your phone | ❌ | ✅ |
| CI/CD pipeline logging decisions | ❌ | ✅ |
| Team sharing one project memory | ❌ | ✅ |
| Multiple devices, one memory | ❌ | ✅ |

**Rule of thumb:** if the AI tool runs inside your machine, use local. If it runs in the cloud (browser-based, mobile, or server), you need remote.

## Architecture

```
Cloud AI Tool (Claude.ai / ChatGPT / Gemini)
       │
       │ HTTPS + MCP-over-SSE
       ▼
┌─────────────────────────┐
│   Loom Gateway          │  ← Your server (VPS, Fly.io, Railway, AWS)
│   Auth + Policy + Audit │
│   MCP SSE endpoint      │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│   Loom Core             │
│   SQLite memory.db      │
│   events.jsonl          │
│   runtime.json          │
└─────────────────────────┘
```

## Option 1: Docker on a VPS (Recommended for Solo Devs)

The simplest setup. Works on any VPS provider (Hetzner, DigitalOcean, Linode, OVH, etc.). Cost: $4–6/month.

### Step 1: Provision a VPS

Any Linux VPS with 1GB RAM and Docker installed. Ubuntu 24.04 recommended.

```bash
# On your VPS
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable docker
```

### Step 2: Deploy Loom

```bash
# Clone the repo
git clone https://github.com/NeimadLab/loom.git
cd loom

# Set your API key
export LOOM_API_KEY=$(openssl rand -hex 32)
echo "Your API key: $LOOM_API_KEY"
echo "Save this — you'll need it to connect AI tools."

# Optional: clone your project repo into the workspace
git clone https://github.com/you/your-project.git /workspace/project

# Start Loom
docker compose -f deploy/docker/docker-compose.yaml up -d
```

### Step 3: Set Up HTTPS (Required)

MCP-over-SSE requires HTTPS. Use Caddy (simplest) or nginx + Let's Encrypt.

```bash
# Install Caddy
sudo apt install -y caddy

# Configure reverse proxy
cat > /etc/caddy/Caddyfile << 'EOF'
loom.yourdomain.com {
    reverse_proxy localhost:8443
}
EOF

sudo systemctl restart caddy
```

Your Loom server is now accessible at `https://loom.yourdomain.com/mcp`.

### Step 4: Verify

```bash
# Test from your local machine
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://loom.yourdomain.com/health
```

## Option 2: Fly.io (Recommended for Zero-Ops)

Fly.io handles TLS, deployment, and persistence. Free tier available.

### Step 1: Install Fly CLI

```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

### Step 2: Deploy

```bash
cd loom

# Create the app
fly launch --name my-loom --region cdg --no-deploy

# Create persistent volume for .loom/ data
fly volumes create loom_data --size 1 --region cdg

# Set your API key
fly secrets set LOOM_API_KEY=$(openssl rand -hex 32)
```

Create `fly.toml` in the project root (or use the one in `deploy/fly-io/`):

```toml
app = "my-loom"
primary_region = "cdg"

[build]
  dockerfile = "deploy/docker/Dockerfile"

[env]
  LOOM_TRANSPORT = "sse"
  LOOM_LOG_LEVEL = "info"

[mounts]
  source = "loom_data"
  destination = "/workspace/.loom"

[[services]]
  internal_port = 8443
  protocol = "tcp"

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

```bash
fly deploy
```

Your Loom server is at `https://my-loom.fly.dev/mcp`.

### Step 3: Verify

```bash
fly logs  # check for startup messages
curl -H "Authorization: Bearer $(fly secrets list | grep LOOM_API_KEY)" \
     https://my-loom.fly.dev/health
```

## Option 3: Railway

```bash
# Install Railway CLI
npm install -g @railway/cli
railway login

# Deploy from the repo
cd loom
railway init
railway up

# Set API key
railway variables set LOOM_API_KEY=$(openssl rand -hex 32)
```

Railway auto-detects the Dockerfile and provides a public URL with TLS.

## Option 4: AWS / GCP / Azure

For enterprise deployments, deploy the Docker container to:

- **AWS:** ECS Fargate with an EFS volume for `.loom/` persistence, ALB for HTTPS
- **GCP:** Cloud Run with a mounted Cloud Storage bucket or Persistent Disk
- **Azure:** Container Instances with Azure Files mount

The key requirements are:
1. The `.loom/` directory must be on persistent storage (not ephemeral container filesystem)
2. HTTPS termination in front of the container
3. The `LOOM_API_KEY` environment variable set

## Connecting Cloud AI Tools

Once your remote Loom is running, connect AI tools to it.

---

### Claude.ai (Browser)

Claude.ai supports MCP integrations (called "connectors" or "skills") through its settings.

**Option A: MCP Integration (if available in your plan)**

1. Go to Claude.ai → Settings → Integrations / MCP
2. Add a new MCP server:
   - **URL:** `https://loom.yourdomain.com/mcp`
   - **Transport:** SSE
   - **Authentication:** Bearer token → paste your `LOOM_API_KEY`
3. Save and start a new conversation

**Option B: Claude Project with custom instructions**

If MCP isn't available in your Claude.ai plan, you can use Loom indirectly:

1. Create a Claude Project
2. In the project system prompt, add:

```
You have access to a Loom workspace via API. Before starting work:
1. Read the current context by calling the Loom API
2. Log decisions as you make them
3. Generate a handoff summary at the end of the session

Loom API endpoint: https://loom.yourdomain.com
API key: [stored in project settings, not in the prompt]
```

This is a workaround until native MCP support is available on all plans.

---

### ChatGPT (Custom GPT with Actions)

ChatGPT supports external APIs through Custom GPT "Actions".

1. Create a Custom GPT at [chat.openai.com/gpts/editor](https://chat.openai.com/gpts/editor)
2. Add an **Action** with the following OpenAPI spec:

```yaml
openapi: 3.1.0
info:
  title: Loom Workspace Memory
  version: 0.2.0
servers:
  - url: https://loom.yourdomain.com
paths:
  /api/search:
    post:
      operationId: searchMemory
      summary: Search project memory
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: string
              required: [query]
      responses:
        '200':
          description: Search results
  /api/log-decision:
    post:
      operationId: logDecision
      summary: Log a decision
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                decision:
                  type: string
                rationale:
                  type: string
              required: [decision, rationale]
      responses:
        '200':
          description: Decision logged
  /api/handoff:
    get:
      operationId: getHandoffSummary
      summary: Get handoff summary for session onboarding
      responses:
        '200':
          description: Handoff summary
```

3. Set authentication to **API Key** with your `LOOM_API_KEY` in the header
4. In the GPT instructions, add:

```
At the start of every conversation, call getHandoffSummary to load project context.
Log all architectural decisions with logDecision.
Search existing decisions before making new ones with searchMemory.
```

> **Note:** The REST API endpoints (`/api/search`, `/api/log-decision`, `/api/handoff`) are planned for V0.3. Currently, Loom exposes only the MCP protocol. The ChatGPT integration will be fully functional when the REST API ships.

---

### Gemini (Google AI Studio)

Google AI Studio and Gemini support MCP through their extensions system:

1. In AI Studio, go to **Extensions** → **Add MCP Server**
2. Enter the SSE endpoint: `https://loom.yourdomain.com/mcp`
3. Configure authentication with your API key

Gemini CLI users can also connect via their MCP config:

```json
{
  "mcpServers": {
    "loom": {
      "type": "sse",
      "url": "https://loom.yourdomain.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_LOOM_API_KEY"
      }
    }
  }
}
```

---

### Claude Code (Remote)

You can also configure Claude Code on your laptop to talk to a remote Loom server instead of a local one:

```bash
loom connect claude-code --remote https://loom.yourdomain.com
```

Or manually in `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "loom": {
      "type": "sse",
      "url": "https://loom.yourdomain.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_LOOM_API_KEY"
      }
    }
  }
}
```

This is useful when you want a central Loom instance that all your devices connect to.

---

### CI/CD Pipelines (GitHub Actions, GitLab CI)

Your CI/CD pipeline can log decisions and test results to Loom:

```yaml
# .github/workflows/ci.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: npm test
      - name: Log test results to Loom
        if: always()
        env:
          LOOM_API_KEY: ${{ secrets.LOOM_API_KEY }}
          LOOM_URL: https://loom.yourdomain.com
        run: |
          pip install loom
          loom log "CI: tests ${{ job.status }} on ${{ github.sha }}" \
            --rationale "Automated CI run on branch ${{ github.ref_name }}"
```

## Security Checklist

Before exposing Loom to the internet:

- [ ] HTTPS enabled (TLS 1.3)
- [ ] Strong API key generated (`openssl rand -hex 32`)
- [ ] API key stored securely (not in code, use env vars or secrets manager)
- [ ] `.loom/` data on persistent storage (not ephemeral container fs)
- [ ] Firewall allows only port 443
- [ ] Loom logs enabled for audit trail
- [ ] Consider IP allowlisting for enterprise use

## Troubleshooting

### "Connection refused" from AI tool

1. Check the server is running: `curl https://loom.yourdomain.com/health`
2. Check TLS is working: `openssl s_client -connect loom.yourdomain.com:443`
3. Check the API key matches: verify in Fly.io secrets / Docker env

### "Unauthorized" errors

The API key in the AI tool's config doesn't match the one on the server. Double-check both.

### Memory not persisting across container restarts

The `.loom/` directory must be on a persistent volume, not the container's ephemeral filesystem. Check your volume mounts.

### High latency from AI tools

Loom should respond in <100ms for memory operations. If slower:
- Check server region (deploy close to the AI service's region)
- Check volume I/O performance (some cheap VPS have slow disks)
- Check if SQLite WAL mode is active (it should be by default)
