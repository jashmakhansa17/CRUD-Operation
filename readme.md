# FastAPI CRUD App - Product & Category

A FastAPI CRUD application using PostgreSQL, SQLModel, and Alembic to manage **Products** and **Categories**. This app features:

- UUID-based primary keys
- Support for nested categories via `parent_id`
- Unique product names within a category
- Check constraints (e.g. product price must be positive)

## Tech Stack

- **FastAPI** - Web framework
- **PostgreSQL** - Relational database
- **SQLModel** - ORM (built on top of SQLAlchemy)
- **Alembic** - Database migrations

## Project Structure

project_root/
│
├── alembic/ # Alembic migrations
├── routes/ # API route handlers
│ ├── product.py
│ └── category.py
├── database.py # DB connection & session
├── main.py # Entry point
└── requirements.txt # Dependencies


## 🧱 Database Models

### 📂 Category

- `id: UUID` – Primary key
- `name: str` – Unique, not null
- `parent_id: UUID (nullable)` – For nested categories (self-referencing FK)
- `subcategories: list[Category]` – Relationship to children
- `products: list[Product]` – Relationship to products

### 📦 Product

- `id: UUID` – Primary key
- `name: str` – Required
- `description: str` – Required
- `price: float` – Must be greater than 0 (Check Constraint)
- `category_id: UUID` – Foreign key to `Category`
- `category: Category` – Relationship to parent category

**Constraints:**

- A product name must be unique within its category.
- Product price must be greater than 0.

## 📦 Installation & Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up your database URL (update .env or use directly)
# Example: postgresql://user:password@localhost:5432/mydb

# Run Alembic migrations
alembic upgrade head

# Run the app
uvicorn main:app --reload
```

# API Endpoints

## Category API

| Method | Endpoint                  | Description                                    |
| ------ | ------------------------- | ---------------------------------------------- |
| POST   | `/categories/`            | Create a new category                          |
| GET    | `/categories/`            | List all categories                            |
| GET    | `/categories/pagination`  | Get categories with pagination & parent filter |
| GET    | `/categories/nested/{id}` | Get nested category hierarchy                  |
| GET    | `/categories/{id}`        | Get a category by ID                           |
| PUT    | `/categories/{id}`        | Update a category by ID                        |
| DELETE | `/categories/{id}`        | Delete a category by ID                        |

## Product API

| Method | Endpoint               | Description                              |
| ------ | ---------------------- | ---------------------------------------- |
| POST   | `/products/`           | Create a new product                     |
| GET    | `/products/`           | List all products                        |
| GET    | `/products/pagination` | Get products with filters and pagination |
| GET    | `/products/{id}`       | Get a product by ID                      |
| PUT    | `/products/{id}`       | Update a product by ID                   |
| DELETE | `/products/{id}`       | Delete a product by ID                   |
