# Quick Start Guide - AI Orchestrator Full Stack

## 🚀 Running the Application

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker Desktop (running)
- Redis (via Docker Compose)

### Step 1: Start Backend Services
```bash
# Navigate to project root
cd d:\Projects\IA-ORCH

# Start Docker services (Redis, Postgres, etc.)
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

# Start Python backend
python main.py
```

**Backend will run on:** `http://localhost:8080`

### Step 2: Start Angular Frontend
```bash
# Open new terminal
cd d:\Projects\IA-ORCH\frontend

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

**Frontend will run on:** `http://localhost:4200`

### Step 3: Access the Application
Open your browser and navigate to:
```
http://localhost:4200
```

---

## 📋 What You'll See

### 1. Dashboard (Home Page)
- System statistics
- Active workbenches list
- Quick action buttons

### 2. Migration Wizard (`/migrate`)
- Create a new migration
- Select source and target stacks
- View migration results

### 3. Code Editor (`/editor`)
- Monaco editor (left pane)
- Live terminal (right pane)
- Create workbenches on-the-fly

### 4. Workbenches (`/workbenches`)
- View all active containers
- Manage workbench lifecycle

---

## 🧪 Testing the System

### Test 1: Create a Workbench
1. Go to Code Editor (`/editor`)
2. Click "+ Python" button
3. Wait for workbench creation
4. See it appear in the dropdown

### Test 2: Run Terminal Commands
1. Select a workbench
2. Type in terminal: `ls -la`
3. Press Enter
4. See output in real-time

### Test 3: Start a Migration
1. Go to Migration Wizard (`/migrate`)
2. Select source: "Java 21"
3. Select target: "Go 1.22"
4. Click "Start Migration"
5. View results with preview URL

---

## 🔧 Configuration

### Backend Configuration
Edit `main.py`:
```python
# Change port
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
```

### Frontend Configuration
Edit `frontend/proxy.conf.json`:
```json
{
  "/api": {
    "target": "http://localhost:8080"  // Backend URL
  }
}
```

---

## 🐛 Troubleshooting

### Issue: Frontend can't connect to backend
**Solution:** Check if Python backend is running on port 8080
```bash
curl http://localhost:8080/health
```

### Issue: WebSocket connection fails
**Solution:** Ensure backend WebSocket endpoint is accessible
```bash
# Check if endpoint exists
curl http://localhost:8080/docs
```

### Issue: Docker containers not starting
**Solution:** Check Docker Desktop is running
```bash
docker ps
```

---

## 📚 API Endpoints

### REST API
- `GET /health` - Health check
- `GET /api/workbench/list` - List workbenches
- `POST /api/workbench/create` - Create workbench
- `POST /api/migration/start` - Start migration
- `GET /api/status` - System status
- `GET /api/metrics` - System metrics

### WebSocket
- `WS /console/{workbench_id}` - Terminal connection

---

## 🎯 Next Steps

1. **Explore the UI**: Navigate through all pages
2. **Create Workbenches**: Try different tech stacks
3. **Run Migrations**: Test the migration wizard
4. **Use Terminal**: Execute commands in containers
5. **Check Metrics**: View system performance

---

## 📖 Further Reading

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Full system architecture
- [walkthrough.md](./walkthrough.md) - Implementation details
- [task.md](./task.md) - Development roadmap

Enjoy your Universal Migration Factory! 🚀