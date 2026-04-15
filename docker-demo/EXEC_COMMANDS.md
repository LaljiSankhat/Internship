# How to Use Docker Exec Commands

The `exec` command allows you to execute commands inside a running container. This is very useful for debugging, inspecting files, running commands, and accessing the container's shell.

## 🐳 Docker Compose Exec (Recommended)

When using Docker Compose, use `docker-compose exec`:

### Basic Syntax
```bash
docker-compose exec <service-name> <command>
```

### Examples

#### 1. Access Backend Container Shell
```bash
# Access bash shell in backend container
docker-compose exec backend bash

# If bash is not available, use sh
docker-compose exec backend sh
```

#### 2. Access Frontend Container Shell
```bash
# Access shell in frontend container (usually sh for alpine images)
docker-compose exec frontend sh
```

#### 3. Run Single Commands

**Backend Examples:**
```bash
# Check Python version
docker-compose exec backend python --version

# List files in the container
docker-compose exec backend ls -la

# Check if database file exists
docker-compose exec backend ls -la /app/data

# View Python packages
docker-compose exec backend pip list

# Run a Python script
docker-compose exec backend python -c "print('Hello from container')"

# Check environment variables
docker-compose exec backend env

# View running processes
docker-compose exec backend ps aux
```

**Frontend Examples:**
```bash
# Check Node version
docker-compose exec frontend node --version

# List files in the container
docker-compose exec frontend ls -la /usr/share/nginx/html

# Check nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Test nginx configuration
docker-compose exec frontend nginx -t

# View nginx logs
docker-compose exec frontend cat /var/log/nginx/error.log
```

#### 4. Interactive Commands
```bash
# Run interactive Python shell
docker-compose exec -it backend python

# Run interactive bash with TTY
docker-compose exec -it backend bash

# Edit a file (if vi/nano is available)
docker-compose exec -it backend vi /app/main.py
```

#### 5. Database Operations (Backend)
```bash
# Access SQLite database
docker-compose exec backend sqlite3 /app/data/notes.db

# Once in sqlite, you can run:
# .tables          # List all tables
# SELECT * FROM notes;  # View all notes
# .quit            # Exit sqlite
```

#### 6. Check Container Resources
```bash
# Check disk usage
docker-compose exec backend df -h

# Check memory usage
docker-compose exec backend free -h

# Check network connectivity
docker-compose exec backend ping -c 3 frontend
docker-compose exec frontend ping -c 3 backend
```

---

## 🐋 Docker Exec (Without Compose)

If you're running containers individually (not with Docker Compose):

### Basic Syntax
```bash
docker exec <container-name> <command>
```

### Examples

```bash
# Access shell
docker exec -it notes-backend bash
docker exec -it notes-frontend sh

# Run commands
docker exec notes-backend python --version
docker exec notes-backend ls -la /app

# Interactive mode (use -it flags)
docker exec -it notes-backend python
docker exec -it notes-backend bash
```

---

## 📝 Common Use Cases

### 1. Debugging Application Issues

```bash
# Check if files are in the right place
docker-compose exec backend ls -la /app

# Check if database exists
docker-compose exec backend ls -la /app/data

# View application logs from inside container
docker-compose exec backend cat /app/logs/app.log
```

### 2. Testing Database

```bash
# Connect to SQLite database
docker-compose exec backend sqlite3 /app/data/notes.db

# Then run SQL queries:
# .tables
# SELECT COUNT(*) FROM notes;
# SELECT * FROM notes;
```

### 3. Installing Packages (Temporary)

```bash
# Install a package in backend (won't persist after container restart)
docker-compose exec backend pip install requests

# Test the package
docker-compose exec backend python -c "import requests; print(requests.__version__)"
```

### 4. Copying Files

```bash
# Copy file FROM container TO host
docker-compose cp backend:/app/data/notes.db ./notes-backup.db

# Copy file FROM host TO container
docker-compose cp ./test.py backend:/app/test.py
```

### 5. Viewing Configuration

```bash
# Check environment variables
docker-compose exec backend env | grep PYTHON

# View nginx config
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Check network connectivity between services
docker-compose exec backend curl http://frontend:3000
```

---

## 🔑 Important Flags

### `-it` Flags
- **`-i`**: Interactive mode (keeps STDIN open)
- **`-t`**: Allocate a pseudo-TTY (terminal)
- Use together (`-it`) for interactive commands like shells

```bash
# Interactive shell
docker-compose exec -it backend bash

# Non-interactive command (no -it needed)
docker-compose exec backend ls -la
```

### `-u` Flag (User)
```bash
# Run as specific user
docker-compose exec -u root backend bash
docker-compose exec -u 1000 backend bash
```

### `-e` Flag (Environment Variables)
```bash
# Set environment variable for the command
docker-compose exec -e DEBUG=1 backend python main.py
```

---

## 🎯 Practical Examples for Notes App

### Check if Backend is Working
```bash
# Test the API from inside backend container
docker-compose exec backend curl http://localhost:8000/
docker-compose exec backend curl http://localhost:8000/api/notes
```

### Inspect Database
```bash
# Open SQLite shell
docker-compose exec backend sqlite3 /app/data/notes.db

# In SQLite shell:
sqlite> .tables
sqlite> SELECT * FROM notes;
sqlite> .schema notes
sqlite> .quit
```

### Check Frontend Files
```bash
# List built frontend files
docker-compose exec frontend ls -la /usr/share/nginx/html

# Check if index.html exists
docker-compose exec frontend cat /usr/share/nginx/html/index.html
```

### Test Network Connectivity
```bash
# From backend, test connection to frontend
docker-compose exec backend curl http://frontend:3000

# From frontend, test connection to backend
docker-compose exec frontend wget -O- http://backend:8000/api/notes
```

### View Logs from Inside Container
```bash
# Check Python application output
docker-compose exec backend tail -f /proc/1/fd/1

# Check nginx access logs
docker-compose exec frontend tail -f /var/log/nginx/access.log
```

---

## ⚠️ Important Notes

1. **Container must be running**: The container must be running to use `exec`. Use `docker-compose ps` to check.

2. **Changes are temporary**: Changes made inside a container (like installing packages) are lost when the container is recreated unless they're in volumes.

3. **Use volumes for persistence**: Files in volumes persist, but changes to the container filesystem don't.

4. **Exit interactive shells**: Type `exit` or press `Ctrl+D` to exit an interactive shell.

---

## 🚀 Quick Reference

```bash
# Most common commands
docker-compose exec backend bash          # Access backend shell
docker-compose exec frontend sh           # Access frontend shell
docker-compose exec backend python        # Python REPL
docker-compose exec backend ls -la        # List files
docker-compose exec backend env           # Environment variables
docker-compose exec backend ps aux       # Running processes

# Check service status first
docker-compose ps                         # List running services
```

---

## 💡 Pro Tips

1. **Use tab completion**: Container names can be auto-completed with Tab key
2. **Combine with pipes**: `docker-compose exec backend ls | grep .py`
3. **Run as different user**: `docker-compose exec -u root backend bash`
4. **Execute in working directory**: Commands run in the WORKDIR specified in Dockerfile
5. **Use `docker-compose exec` instead of `docker exec`**: It's easier and works with service names

Happy debugging! 🐛🔍

