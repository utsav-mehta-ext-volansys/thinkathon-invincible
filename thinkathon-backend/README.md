#  FastAPI Auth Backend (MongoDB + JWT)

This project is a lightweight authentication backend built using **FastAPI** and **MongoDB (via Motor)**, secured with **JWT** tokens.

## Features

- User Signup and Login APIs
- JWT token generation with expiry support
- Password hashing and verification
- MongoDB async access using Motor
- Proper error handling for invalid login and unregistered email

##  Stack Used

- **FastAPI** – API framework
- **Motor** – Async MongoDB driver
- **Pydantic** – Data validation
- **python-jose** – JWT handling
- **Uvicorn** – ASGI server

##  Quick Start

1. Clone the repo and install dependencies (`pip install -r requirements.txt`)
2. Create a `.env` file with Mongo URL and JWT secret
3. Use DB name - `healthcare`
4. Run the server with: `uvicorn main:app --reload`

##  Structure (High Level)

- `main.py` – FastAPI app and routing
- `routes/auth_routes.py` – Signup & login endpoints
- `models/auth_model.py` – Request/response model
- `schemas/auth_schemas.py` – Request/response schemas
- `utils.py` – JWT & password helpers

