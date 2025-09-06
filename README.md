# docker_django

This project is a Django application set up to run with Docker and Docker Compose.

## Prerequisites
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Quick Start

### 1. Clone the repository
```
git clone https://github.com/Nimesh9172/docker_django.git
cd docker_django
```

### 2. Build and start the containers
```
docker-compose up --build
```
This will build the Docker images and start the Django app and any other services defined in `docker-compose.yml`.

### 3. Access the application
- The Django app will be available at: [http://localhost:8000](http://localhost:8000)

### 4. Run migrations (if needed)
If you need to run Django migrations, use:
```
docker-compose exec web python manage.py migrate
```

### 5. Create a superuser (optional)
```
docker-compose exec web python manage.py createsuperuser
```

### 6. Collect static files (optional)
```
docker-compose exec web python manage.py collectstatic
```

## Stopping the project
To stop the containers, press `Ctrl+C` in the terminal where Docker Compose is running, or run:
```
docker-compose down
```

## Notes
- Make sure to update environment variables as needed in your Docker and Django settings.
- For development, you can modify the code and restart the containers as needed.

---

Feel free to update this README with more details about your project!
