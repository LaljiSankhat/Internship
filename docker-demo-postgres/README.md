# Notes App - Docker Compose Practice with PostgreSQL

A full-stack notes application built with React (frontend) and FastAPI (backend), using PostgreSQL database, containerized with Docker and orchestrated using Docker Compose.

## 🏗️ Architecture

- **Frontend**: React app served with Nginx
- **Backend**: FastAPI REST API with PostgreSQL database
- **Database**: PostgreSQL 15 (Alpine)
- **Containerization**: Docker containers for all services
- **Orchestration**: Docker Compose for multi-container management

## 📁 Project Structure

```
docker-demo-postgres/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile          # Backend container definition
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

1. **Navigate to the project directory:**
   ```bash
   cd docker-demo-postgres
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Start PostgreSQL database container
   - Build and start the backend Docker container
   - Build and start the frontend Docker container
   - Set up networking between containers
   - Initialize the database schema

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

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
docker-compose logs postgres
docker-compose logs backend
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f
```

### Stopping the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes database data)
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

### Database Configuration

The PostgreSQL database is configured with:
- **Database**: `notesdb`
- **User**: `notesuser`
- **Password**: `notespwd`
- **Host**: `postgres` (service name in Docker network)
- **Port**: `5432`

These can be customized via environment variables in `docker-compose.yml`.

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

# PostgreSQL container
docker-compose exec postgres psql -U notesuser -d notesdb
```

### Access PostgreSQL Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U notesuser -d notesdb

# Once connected, you can run SQL commands:
# \dt              # List all tables
# SELECT * FROM notes;  # View all notes
# \q               # Exit psql
```

### Remove everything (containers, networks, volumes)
```bash
docker-compose down -v --rmi all
```

## 📝 Features

- ✅ Create, read, update, and delete notes
- ✅ Beautiful, responsive UI
- ✅ RESTful API with FastAPI
- ✅ PostgreSQL database for data persistence
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ CORS enabled for frontend-backend communication
- ✅ Volume mounting for database persistence
- ✅ Health checks for database service
- ✅ Automatic database initialization

## 🎓 Learning Points

This project demonstrates:

1. **Multi-container applications** - Running multiple services together
2. **Service networking** - Containers communicating via Docker network
3. **Volume mounting** - Persisting database data outside containers
4. **Dependency management** - Services depend on each other (backend depends on postgres)
5. **Environment variables** - Configuring services
6. **Build optimization** - Multi-stage builds for frontend
7. **Service orchestration** - Managing multiple containers with Compose
8. **Database integration** - Connecting application to PostgreSQL
9. **Health checks** - Ensuring database is ready before starting backend
10. **Service dependencies** - Using `depends_on` with health checks

## 🔍 Troubleshooting

### Port already in use
If ports 3000, 8000, or 5432 are already in use, modify the port mappings in `docker-compose.yml`:
```yaml
ports:
  - "3001:3000"  # Change host port
```

### Database connection errors
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check PostgreSQL logs: `docker-compose logs postgres`
- Verify database credentials match in `docker-compose.yml` and `main.py`

### Frontend can't connect to backend
Check that both services are on the same Docker network (defined in `docker-compose.yml`).

### Database not persisting
The PostgreSQL data is stored in a Docker volume named `postgres-data`. To remove it:
```bash
docker-compose down -v
```

### Backend can't connect to PostgreSQL
- Wait for PostgreSQL to be healthy (health check ensures this)
- Check environment variables in `docker-compose.yml`
- Verify network connectivity: `docker-compose exec backend ping postgres`

## 🗄️ Database Management

### Access PostgreSQL CLI
```bash
docker-compose exec postgres psql -U notesuser -d notesdb
```

### Backup Database
```bash
docker-compose exec postgres pg_dump -U notesuser notesdb > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U notesuser notesdb < backup.sql
```

### View Database Tables
```bash
docker-compose exec postgres psql -U notesuser -d notesdb -c "\dt"
```

### View All Notes
```bash
docker-compose exec postgres psql -U notesuser -d notesdb -c "SELECT * FROM notes;"
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

## 🎯 Next Steps

Try these exercises to practice:

1. Add environment variables file (`.env`) for configuration
2. Implement user authentication
3. Add Redis for caching
4. Set up database migrations (Alembic)
5. Add a reverse proxy (Traefik or Nginx)
6. Implement CI/CD with Docker
7. Add database backup automation
8. Set up monitoring and logging

## 🔄 Migration from SQLite to PostgreSQL

This project was migrated from SQLite to PostgreSQL. Key changes:

- Replaced `sqlite3` with `psycopg2` for database connectivity
- Changed SQL syntax from SQLite to PostgreSQL (e.g., `?` to `%s` for parameters)
- Updated data types (e.g., `INTEGER PRIMARY KEY AUTOINCREMENT` to `SERIAL PRIMARY KEY`)
- Added PostgreSQL service to `docker-compose.yml`
- Implemented connection retry logic for database initialization
- Added health checks for PostgreSQL service

---

Happy Docker Compose practicing with PostgreSQL! 🐳🐘
