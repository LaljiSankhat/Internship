# How to Run Frontend and Backend

## Method 1: Using Docker Compose (Recommended) 🐳

This is the easiest way to run both services together.

### Step 1: Navigate to the project directory
```bash
cd /home/web-h-013/Learning/docker-demo
```

### Step 2: Build and start both services
```bash
docker-compose up --build
```

This will:
- Build the backend Docker image
- Build the frontend Docker image  
- Start both containers
- Set up networking between them

### Step 3: Access the application
- **Frontend**: Open http://localhost:3000 in your browser
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Run in background (detached mode)
```bash
docker-compose up -d --build
```

### Stop the services
```bash
docker-compose down
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend

# Follow logs
docker-compose logs -f
```

---

## Method 2: Run Services Individually with Docker

### Run Backend Only

```bash
# Navigate to backend directory
cd /home/web-h-013/Learning/docker-demo/backend

# Build the image
docker build -t notes-backend .

# Run the container
docker run -d \
  --name notes-backend \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  notes-backend
```

Access backend at: http://localhost:8000

### Run Frontend Only

```bash
# Navigate to frontend directory
cd /home/web-h-013/Learning/docker-demo/frontend

# Build the image
docker build -t notes-frontend .

# Run the container
docker run -d \
  --name notes-frontend \
  -p 3000:3000 \
  notes-frontend
```

Access frontend at: http://localhost:3000

**Note**: If running separately, you'll need to update the frontend API URL to point to `http://localhost:8000` instead of using the Docker service name.

---

## Method 3: Run Without Docker (Development Mode)

### Run Backend Locally

```bash
# Navigate to backend directory
cd /home/web-h-013/Learning/docker-demo/backend

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Run Frontend Locally

```bash
# Navigate to frontend directory
cd /home/web-h-013/Learning/docker-demo/frontend

# Install dependencies
npm install

# Start development server
npm start
```

**Note**: Make sure to update `frontend/src/App.js` to use `http://localhost:8000` as the API URL when running locally.

---

## Quick Commands Reference

### Docker Compose Commands
```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart backend
docker-compose restart frontend
```

### Individual Docker Commands
```bash
# List running containers
docker ps

# Stop a container
docker stop notes-backend
docker stop notes-frontend

# Remove a container
docker rm notes-backend
docker rm notes-frontend

# View container logs
docker logs notes-backend
docker logs notes-frontend

# Execute command in container
docker exec -it notes-backend bash
docker exec -it notes-frontend sh
```

---

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use:
- Change the port mapping in `docker-compose.yml`
- Or stop the service using that port

### Frontend Can't Connect to Backend
- Make sure both services are running
- Check that they're on the same Docker network (if using Docker Compose)
- Verify the API URL in the frontend code

### Database Not Persisting
- Ensure the `backend/data` directory exists
- Check volume mounts in docker-compose.yml

---

## Recommended Approach

**For Docker Compose practice**: Use **Method 1** (Docker Compose) as it demonstrates:
- Multi-container orchestration
- Service networking
- Dependency management
- Volume mounting

This is the best way to practice Docker Compose! 🚀










