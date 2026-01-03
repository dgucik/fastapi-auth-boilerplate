# ⚡️ FastAPI DDD/CQRS Boilerplate: Auth & Users Module

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Containerized-Docker-blue?logo=docker)
![Poetry](https://img.shields.io/badge/Poetry-Managed-blueviolet?logo=poetry&logoColor=white)
![Code Style](https://img.shields.io/badge/Code%20Style-Ruff-black)
![Type Checker](https://img.shields.io/badge/Type%20Checker-Mypy-blue)

A production-ready, scalable boilerplate for **FastAPI** applications, featuring a robust implementation of **Authentication** and **User Management** modules.

This project is designed as a learning resource and a starting point for complex systems, strictly following **Domain-Driven Design (DDD)**, **CQRS** (Command Query Responsibility Segregation), and **Clean Architecture** principles.

## ✨ Features

This boilerplate provides a complete foundation for building secure APIs:

* **Authentication & Identity:**
    * Full **Registration** and Login logic handled within the Auth module.
    * Robust **Token-Based Authentication** implementation.
* **Security:**
    * Stateless **JWT** (JSON Web Tokens) handling with Access & Refresh token rotation.
* **User Management:**
    * Decoupled **User Profile** creation (triggered via Integration Event).
    * Profile data management and retrieval.
* **Scalable Structure:**
    * Modular Monolith design allowing easy transition to microservices if needed.

## 🏗 Architecture & Design Patterns

This boilerplate uses **Vertical Slicing** (Modular Monolith) to organize code by business features rather than technical layers.

### Key Architectural Concepts

* **Clean Architecture:** Organizes code around the business logic, adhering to the **Dependency Rule** (dependencies point inwards).
    * **Inner Layers (`Domain`, `Application`):** Contain the core **business rules and use cases**, completely agnostic of technical details (databases, frameworks).
    * **Outer Layers (`Infrastructure`, `API`):** Act as plugins/adapters that implement interfaces defined by the core to communicate with the external world.
* **Domain-Driven Design (DDD):** The core business logic is isolated within the `Domain` layer, free of frameworks and external dependencies. We use Aggregates, Entities, and Value Objects to model business rules.
* **CQRS (Command Query Responsibility Segregation):**
    * **Commands:** Handle write operations and state changes.
    * **Queries:** Handle read operations.
* **Event-Driven Architecture (In-Memory):**
    * **Domain Events:** Used strictly *within* a module to trigger internal side effects (e.g., sending a confirmation email immediately after account registration).
    * **Integration Events:** Published via the **In-Memory Event Bus** to notify the rest of the system about state changes.
* **Module Communication:**
    * Modules are autonomous "black boxes" that do not import each other's internal code. Communication happens in two ways:
        1. **Synchronous (Contracts via DI):** When a module needs data from another (e.g., `Users` needs identity details from `Auth`), it uses **Public Contracts** (Interfaces) injected via **Dependency Injection**.
        2. **Asynchronous (Integration Events):** Modules subscribe to Integration Events from other modules to react to changes (e.g., `Users` module creating a User Entry when the `AccountRegistered` integration event occurs).

## 📂 Project Structure

Code is organized into independent business modules (e.g., `auth`, `users`).

```text
src/
├── modules/                        # Independent Business Modules
│   ├── auth/
│   │   ├── api/                    # Routes / Controllers
│   │   ├── application/            # Use Cases (Commands/Queries/Event Handlers)
│   │   ├── domain/                 # Core Logic (Aggregates, Entities, Value Objects)
│   │   ├── infrastructure/         # Implementation (Repo, Adapters)
│   │   └── container.py            # Module-specific DI Container
│   ├── users/
│   │   ├── api/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   └── container.py
├── shared/                         # Shared Kernel (Event Bus, Base Classes)
│   ├── application/
│   ├── domain/
│   └── infrastructure/
├── container.py                    # Main DI Container (Wiring modules together)
├── database.py                     # Database engine, seesion setup & ORM Base
├── main.py                         # App Entrypoint
└── settings.py                     # App configuration, env variables
```

## 🚀 Getting Started

### Prerequisites

* **Python:** Version 3.12 or newer.
* **Poetry:** (Dependency Management) Tool for installing and isolating project dependencies.
* **Docker & Docker Compose:** (Local Environment) Required for running the PostgreSQL database and other services locally.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dgucik/fastapi-auth-boilerplate.git
    cd fastapi-auth-boilerplate
    ```

2.  **Install dependencies using Poetry:**
    ```bash
    poetry install
    ```

3.  **Activate the virtual environment:**
    ```bash
    poetry shell
    ```

4.  **Environment Configuration:**
    Create a `.env` file and adjust settings (database URL, secret keys, etc.):
    ```bash
    cp .env.example .env
    ```

### Running the Application

1.  **Start the local database (PostgreSQL):**
    The project uses Docker Compose to run the required PostgreSQL service.
    ```bash
    docker compose up -d
    ```

2.  **Run Database Migrations (Alembic):**
    Apply the database schema changes:
    ```bash
    alembic upgrade head
    ```

3.  **Start the development server with hot-reload:**
    ```bash
    uvicorn src.main:app --reload
    ```

* **API Documentation (Swagger UI):** `http://localhost:8000/docs`

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
