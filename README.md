# NATURAL NEWS VIP LOGIN

## Backend

Build with FastAPI, FastMail, Apscheduler, SQLModel.

### How to run?

#### Docker

Build Docker image with:

```bash
$ docker build . -t backend --progress plain -f dockerfiles/backend.Dockerfile
```

Run Docker container with:

```bash
$ docker run -p 8000:8000 backend
```

#### Unix like OS

```bash
$ chmod +x scripts/run.sh

$ ./scripts/run.sh
```

#### Windows

Go to scripts folder, right click into run.bat file, choose Run

#### OpenAPI Docs

Open your web browser, go to http://0.0.0.0:8000/docs to review routes and models

### Database schemas:

![DB Schemas](./docs/backend/db_schemas.png)
