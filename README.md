# DevCommunity - Community Forum Registration System

A containerized REST API for community member registration built with Flask, PostgreSQL, and Docker Compose. This project demonstrates a forum-style registration system where developers can join a community, view other members, and manage their profiles.

## Project Description

This project implements a complete community registration system that simulates a developer forum:

- **Member Registration**: Join the community with username, email, and password
- **Member Directory**: View all community members with "joined X ago" timestamps
- **User Authentication**: Login/logout with session management
- **Profile Management**: View and edit your profile, change password
- **Dashboard**: Real-time stats showing total members and active users
- **Search**: Filter members by name or email
- **Data Persistence**: PostgreSQL database with persistent storage
- **Security**: Password hashing using industry-standard algorithms

### Real-Life Application

This community registration system represents a common pattern found in:

- **Developer Forums**: Stack Overflow, Dev.to, Reddit programming communities
- **Online Communities**: Discord servers, Slack workspaces with member directories
- **Learning Platforms**: Course forums where students can see classmates
- **Open Source Projects**: Contributor registration and management

The system demonstrates how modern web communities handle:
- User onboarding and registration
- Member discovery and networking
- Profile management
- Session-based authentication

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
    http://localhost:5000  (Web App)
    http://localhost:8080  (Adminer)
```

---

## Technologies and Containers

| Container | Image | Port | Description |
|-----------|-------|------|-------------|
| **flask-api** | Custom (python:3.11-slim) | 5000 | REST API + Web Application |
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
DevCommunity/
├── docker-compose.yml      # Container orchestration configuration
├── Dockerfile              # Custom Flask application image
├── app.py                  # Flask REST API + Web Application
├── requirements.txt        # Python dependencies
├── init.sql                # Database initialization script
├── test.sh                 # API testing script with curl commands
├── .gitignore              # Git ignore rules
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

### 3. Access the Application

| Service | URL | Description |
|---------|-----|-------------|
| **DevCommunity** | http://localhost:5000 | Main web application |
| **Login Page** | http://localhost:5000/login | Member login |
| **Profile** | http://localhost:5000/profile | Your profile (after login) |
| **Health Check** | http://localhost:5000/health | System status |
| **Adminer** | http://localhost:8080 | Database GUI |

### 4. Test the Application

**Using the Web Interface:**
1. Open http://localhost:5000
2. Fill in the registration form to join the community
3. View the member list with "joined X ago" timestamps
4. Login at http://localhost:5000/login
5. Access your profile at http://localhost:5000/profile

**Using the API:**
```bash
# Register a new member
curl -X POST http://localhost:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "john_doe", "email": "john@example.com", "password": "securepass123"}'

# List all members
curl http://localhost:5000/api/users

# Get specific member
curl http://localhost:5000/api/users/1
```

**Run the test script:**
```bash
bash test.sh
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
| `GET` | `/` | Community dashboard |
| `GET` | `/login` | Login page |
| `GET` | `/logout` | Logout |
| `GET` | `/profile` | Member profile |
| `GET` | `/health` | Health check |
| `POST` | `/api/users` | Register new member |
| `GET` | `/api/users` | List all members |
| `GET` | `/api/users/<id>` | Get member by ID |
| `DELETE` | `/api/users/<id>` | Remove member |

### Request/Response Examples

#### Register Member
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
    "created_at": "2026-01-12T10:30:00"
  }
}
```

#### List Members
**Response (200 OK):**
```json
{
  "users": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2026-01-12T10:30:00",
      "last_login": "2026-01-12T11:00:00"
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
| 404 | Member not found |
| 409 | Conflict (duplicate username/email) |
| 500 | Internal server error |

---

## Features

### Web Interface
- Modern, clean UI with responsive design
- Real-time member count and activity stats
- Search/filter functionality for member directory
- "Joined X ago" time formatting
- Confirmation modal for member removal
- Toast notifications for actions

### Authentication
- Email/password login
- Session-based authentication
- Protected routes (profile page)
- Last login tracking

### Profile Management
- View account information
- Edit username and email
- Change password (with current password verification)

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

---

## Security Features

- **Password Hashing**: Passwords are hashed using PBKDF2-SHA256 (Werkzeug)
- **Input Validation**: All user inputs are validated before processing
- **SQL Injection Prevention**: Using parameterized queries (psycopg2)
- **No Password Exposure**: Passwords are never returned in API responses
- **Session Security**: Flask sessions with secret key

---

## Author

Created for the Virtualization of Computer Systems course.

---

## License

This project is for educational purposes.
