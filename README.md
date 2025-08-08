# Backend Developer Technical Test - Expense Tracker API

A Django REST Framework-based Expense Tracker API with PostgreSQL database, JWT authentication, and Docker containerization.

## 🏗️ Project Overview

This project implements a complete expense tracking system with user authentication, expense management, and comprehensive reporting features. The application is fully containerized using Docker and includes a PostgreSQL database.

## 🚀 Features

### Core Features
- **User Authentication**: JWT-based registration and login system
- **Expense Management**: Create, view, and categorize expenses
- **Expense Analytics**: Summary reports with total spending and category breakdowns
- **RESTful API**: Clean and well-documented API endpoints
- **Database**: PostgreSQL with proper data modeling

### Technical Features
- **Docker Containerization**: Complete Docker setup with PostgreSQL
- **JWT Authentication**: Secure token-based authentication using SimpleJWT
- **Input Validation**: Comprehensive request validation and error handling
- **CORS Support**: Frontend integration ready
- **Admin Interface**: Django admin for backend management

## 📋 API Endpoints

### Authentication
```
POST /api/auth/register/     # User registration
POST /api/auth/login/        # User login
```

### Expenses
```
GET    /api/expenses/         # List all user expenses
POST   /api/expenses/         # Create new expense
GET    /api/expenses/{id}/    # Get specific expense
PUT    /api/expenses/{id}/    # Update expense
DELETE /api/expenses/{id}/    # Delete expense
GET    /api/expenses/summary/ # Get expense summary and analytics
```

## 🛠️ Technology Stack

- **Backend**: Django 5.1.6 + Django REST Framework
- **Database**: PostgreSQL 15
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Containerization**: Docker + Docker Compose
- **Web Server**: Gunicorn
- **Admin Interface**: Django Admin 

## 📦 Installation & Setup

### Prerequisites
- Docker and Docker Compose installed
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd reachverse
   ```

2. **Build and run with Docker**
   ```bash
   docker-compose up --build
   ```

3. **Create a superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application**
   - API Base URL: `http://localhost:8000`
   - Django Admin: `http://localhost:8000/admin/`
   

### Manual Setup (Alternative)

1. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run development server**
   ```bash
   python manage.py runserver
   ```    

## 🧪 Testing

Run unit tests:
```bash
# In Docker
docker-compose exec web python manage.py test

# Local environment
python manage.py test
```

## 📝 API Usage Examples

### Authentication
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "testuser", "password": "testpass123"}'

## 🐳 Docker Services

The application runs with the following services:

- **web**: Django application (port 8000)
- **db**: PostgreSQL database (port 5432)

## 🔧 Configuration

### Environment Variables
The application uses environment variables for configuration:

```env
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=django_password
DB_HOST=db
DB_PORT=5432
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

## 📁 Project Structure

```
reachverse/
├── project/                 # Django project settings
│   ├── settings.py         # Main settings file
│   ├── urls.py             # URL configuration
│   └── wsgi.py             # WSGI configuration
├── expenses_tracker/        # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # API views
│   ├── serializers.py      # DRF serializers
│   └── urls.py             # App URL patterns
├── Dockerfile              # Docker container definition
├── docker-compose.yml      # Docker services configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```


