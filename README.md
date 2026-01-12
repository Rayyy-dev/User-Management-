# User Registration System

A containerized REST API for user registration built with Flask, PostgreSQL, and Docker Compose. This project demonstrates a minimal authentication/signup system - a foundational component of most modern web applications.

## Project Description

This project implements a complete user registration system that allows:
- **User Registration**: Create new user accounts with username, email, and password
- **User Management**: List, retrieve, and delete user accounts
- **Web Interface**: HTML frontend with registration form and user list
- **Data Persistence**: PostgreSQL database with persistent storage
- **Security**: Password hashing using industry-standard algorithms
- **Input Validation**: Email format validation and input sanitization

### Real-Life Application

User registration systems are essential building blocks for:
- **Web Applications**: E-commerce sites, social media platforms, SaaS products
- **Authentication Services**: Single sign-on (SSO) systems, identity providers
- **Enterprise Systems**: Employee portals, customer management systems
- **Educational Platforms**: Learning management systems, student portals

This project serves as a foundation that can be extended with features like:
- Login/logout functionality
- Password reset via email
- Role-based access control
- OAuth integration

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      Docker Network (app-network)               │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Flask     │    │  PostgreSQL │    │   Adminer   │         │
│  │   API       │───▶│   Database  │◀───│   (DB GUI)  │         │
│  │  Port 5000  │    │  Port 5432  │    │  Port 8080  │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                   │                                    │
│        │                   ▼                                    │
│        │            ┌─────────────┐                            │
│        │            │   Volume    │                            │
│        │            │  postgres_  │                            │
│        │            │    data     │                            │
│        │            └─────────────┘                            │
└────────┼────────────────────────────────────────────────────────┘
         │
         ▼
    Host Machine
    http://localhost:5000  (API)
    http://localhost:8080  (Adminer)
```

---

## Technologies and Containers

| Container | Image | Port | Description |
|-----------|-------|------|-------------|
| **flask-api** | Custom (python:3.11-slim) | 5000 | REST API application |
| **postgres-db** | postgres:15 | 5432 | PostgreSQL database |
| **adminer** | adminer:latest | 8080 | Database management GUI |

### Technology Stack

- **Backend Framework**: Flask 3.0.0 (Python)
- **Frontend**: HTML/CSS/JavaScript (served by Flask)
- **Database**: PostgreSQL 15
- **Database GUI**: Adminer
- **Password Hashing**: Werkzeug (PBKDF2-SHA256)
- **Email Validation**: email-validator
- **Containerization**: Docker & Docker Compose

---

## Project Structure

```
Virtualisation Project/
├── docker-compose.yml      # Container orchestration configuration
├── Dockerfile              # Custom Flask application image
├── app.py                  # Flask REST API source code
├── requirements.txt        # Python dependencies
├── init.sql                # Database initialization script
├── test.sh                 # API testing script with curl commands
└── README.md               # Project documentation (this file)
```

---

## Prerequisites

Before running this project, ensure you have installed:

- **Docker**: [Download Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Included with Docker Desktop (Windows/Mac) or install separately on Linux

Verify installation:
```bash
docker --version
docker-compose --version
```

---

## Step-by-Step Instructions

### 1. Clone or Download the Project

Navigate to the project directory:
```bash
cd "Virtualisation Project"
```

### 2. Build and Start the Containers

```bash
docker-compose up --build
```

This command will:
- Build the custom Flask API image
- Pull PostgreSQL and Adminer images
- Create the Docker network and volume
- Start all three containers
- Initialize the database with the users table

Wait until you see:
```
flask-api    |  * Running on http://0.0.0.0:5000
```

### 3. Verify the Services

| Service | URL | Status Check |
|---------|-----|--------------|
| Flask API | http://localhost:5000 | Should show API info |
| Adminer | http://localhost:8080 | Should show login page |
| Health Check | http://localhost:5000/health | Should show "healthy" |

### 4. Test the API

Run the test script:
```bash
# On Linux/Mac
chmod +x test.sh
./test.sh

# On Windows (Git Bash)
bash test.sh
```

Or test manually with curl:
```bash
# Register a new user
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "securepass123"}'

# List all users
curl http://localhost:5000/api/users

# Get specific user
curl http://localhost:5000/api/users/1

# Delete user
curl -X DELETE http://localhost:5000/api/users/1
```

### 5. Access Adminer (Database GUI)

1. Open http://localhost:8080
2. Login with:
   - **System**: PostgreSQL
   - **Server**: postgres
   - **Username**: admin
   - **Password**: secretpassword
   - **Database**: userdb

### 6. Stop the Services

```bash
# Stop containers (preserves data)
docker-compose down

# Stop containers and remove volumes (clears all data)
docker-compose down -v
```

---

## API Documentation

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information |
| `GET` | `/health` | Health check |
| `POST` | `/api/users` | Register new user |
| `GET` | `/api/users` | List all users |
| `GET` | `/api/users/<id>` | Get user by ID |
| `DELETE` | `/api/users/<id>` | Delete user |

### Request/Response Examples

#### Register User
**Request:**
```json
POST /api/users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2026-01-11T10:30:00"
  }
}
```

#### List Users
**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2026-01-11T10:30:00"
    }
  ],
  "count": 1
}
```

### Validation Rules

- **Username**: 3-50 characters, alphanumeric and underscores only
- **Email**: Valid email format (validated using email-validator)
- **Password**: Minimum 6 characters (hashed before storage)

### Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request (validation failed) |
| 404 | User not found |
| 409 | Conflict (duplicate username/email) |
| 500 | Internal server error |

---

## Troubleshooting

### Container won't start
```bash
# Check container logs
docker-compose logs flask-api
docker-compose logs postgres

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

### Database connection error
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Wait a few seconds after starting - PostgreSQL needs time to initialize

### Port already in use
```bash
# Check what's using the port
netstat -ano | findstr :5000   # Windows
lsof -i :5000                  # Linux/Mac

# Change port in docker-compose.yml if needed
```

### Permission denied (test.sh)
```bash
chmod +x test.sh
```

---

## Security Features

- **Password Hashing**: Passwords are hashed using PBKDF2-SHA256 (Werkzeug)
- **Input Validation**: All user inputs are validated before processing
- **SQL Injection Prevention**: Using parameterized queries (psycopg2)
- **No Password Exposure**: Passwords are never returned in API responses

---

## Author

Created for the Virtualization of Computer Systems course.

---

## License

This project is for educational purposes.
