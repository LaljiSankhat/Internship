# Notes App - Docker Compose Practice

A full-stack notes application built with React (frontend) and FastAPI (backend), containerized with Docker and orchestrated using Docker Compose.

## 🏗️ Architecture

- **Frontend**: React app served with Nginx
- **Backend**: FastAPI REST API with SQLite database
- **Containerization**: Docker containers for both services
- **Orchestration**: Docker Compose for multi-container management

## 📁 Project Structure

```
docker-demo/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container definition
│   └── data/               # SQLite database (created at runtime)
├── frontend/
│   ├── src/                # React source code
│   ├── public/             # Static files
│   ├── package.json        # Node dependencies
│   ├── Dockerfile          # Frontend container definition
│   └── nginx.conf          # Nginx configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- Docker installed on your system
- Docker Compose installed (usually comes with Docker Desktop)

### Running the Application

1. **Clone or navigate to the project directory:**
   ```bash
   cd docker-demo
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the backend Docker image
   - Build the frontend Docker image
   - Start both containers
   - Set up networking between containers

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Running in Detached Mode

To run containers in the background:

```bash
docker-compose up -d --build
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Stopping the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes database)
docker-compose down -v
```

## 🔧 Development

### Backend Development

The backend API provides the following endpoints:

- `GET /api/notes` - Get all notes
- `GET /api/notes/{id}` - Get a specific note
- `POST /api/notes` - Create a new note
- `PUT /api/notes/{id}` - Update a note
- `DELETE /api/notes/{id}` - Delete a note

### Frontend Development

The frontend is a React application that communicates with the backend API. The API URL is configured via environment variables.

### Rebuilding After Changes

If you make changes to the code:

```bash
# Rebuild and restart
docker-compose up --build

# Or rebuild specific service
docker-compose build backend
docker-compose up
```

## 🐳 Docker Commands Reference

### Build images
```bash
docker-compose build
```

### Start services
```bash
docker-compose up
```

### Stop services
```bash
docker-compose down
```

### View running containers
```bash
docker-compose ps
```

### Execute commands in containers
```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh
```

### Remove everything (containers, networks, volumes)
```bash
docker-compose down -v --rmi all
```

## 📝 Features

- ✅ Create, read, update, and delete notes
- ✅ Beautiful, responsive UI
- ✅ RESTful API with FastAPI
- ✅ SQLite database for data persistence
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ CORS enabled for frontend-backend communication
- ✅ Volume mounting for database persistence

## 🎓 Learning Points

This project demonstrates:

1. **Multi-container applications** - Running multiple services together
2. **Service networking** - Containers communicating via Docker network
3. **Volume mounting** - Persisting data outside containers
4. **Dependency management** - Frontend depends on backend
5. **Environment variables** - Configuring services
6. **Build optimization** - Multi-stage builds for frontend
7. **Service orchestration** - Managing multiple containers with Compose

## 🔍 Troubleshooting

### Port already in use
If ports 3000 or 8000 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change host port
```

### Database not persisting
Ensure the `backend/data` directory exists and has proper permissions.

### Frontend can't connect to backend
Check that both services are on the same Docker network (defined in `docker-compose.yml`).

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

## 🎯 Next Steps

Try these exercises to practice:

1. Add a database service (PostgreSQL) using Docker Compose
2. Add environment variables file (`.env`)
3. Implement user authentication
4. Add Redis for caching
5. Set up health checks for services
6. Add a reverse proxy (Traefik or Nginx)
7. Implement CI/CD with Docker

---

Happy Docker Compose practicing! 🐳

