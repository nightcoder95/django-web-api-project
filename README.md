# Django Product Management Web API

This is a comprehensive web application and API built with Django and Django REST Framework. It provides a platform for managing products and categories with a sophisticated role-based access control system, a secure token-based API, and a full-featured web interface for administration and user interaction.

## ✨ Features

### Core Features
- **Role-Based Access Control**: Four distinct user roles (**Admin, Staff, Agent, End User**) with granular permissions for every action.
- **Product & Category Management**: Full CRUD (Create, Read, Update, Delete) operations for products and categories, restricted by user roles.
- **Order & Cart System**: A complete shopping cart and order management system for end-users.
- **Asynchronous Video Processing**: Product videos are processed in a background thread to avoid blocking API responses.

### API Features
- **Secure API Endpoints**: Token-based authentication required for all sensitive actions.
- **AES Encryption Middleware**: All API requests and responses are automatically encrypted and decrypted for maximum security.
- **Role-Based API Access**: API endpoints are protected and behave differently based on the user's role.

### Web Portal Features
- **Full-Featured UI**: A complete web interface built with Django Templates and Bootstrap 5 to test and manage the application.
- **Role-Specific Dashboards**: Each user role gets a unique dashboard with relevant actions and information.
- **Video Upload & Status Tracking**: A user-friendly interface to upload multiple videos and track their processing status in real-time.

### Data Management
- **Dummy Data Generator**: A powerful management command to populate the database with thousands of products and categories using multithreading for speed.
- **Data Export**: Functionality to export products and categories to **CSV** and **Excel** formats.

## 🛠️ Technology Stack

- **Backend**: Django, Django REST Framework
- **Database**: SQLite3 (default), easily configurable for PostgreSQL
- **Encryption**: `pycryptodome` for AES-256
- **Data Generation**: `Faker`
- **Excel/CSV Export**: `openpyxl`
- **Environment Variables**: `python-decouple`
- **Frontend**: Django Templates, Bootstrap 5

## 🚀 Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/nightcoder95/django-web-api-project.git](https://github.com/nightcoder95/django-web-api-project.git)
    cd django-web-api-project
    ```

2.  **Create and Activate a Virtual Environment**
    ```bash
    # For Windows
    python -m venv env
    .\env\Scripts\activate

    # For macOS/Linux
    python3 -m venv env
    source env/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    -   Copy the example `.env.example` file to a new `.env` file.
        ```bash
        # For Windows
        copy .env.example .env

        # For macOS/Linux
        cp .env.example .env
        ```
    -   Open the `.env` file and set your own secret keys for `AES_SECRET_KEY` and `AES_SECRET_IV`.

5.  **Run Database Migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser (Admin)**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts. When your user is created, be sure to edit it in the admin panel and set the **role** to `admin`.

7.  **Run the Development Server**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.

## 🧑‍🤝‍🧑 User Roles and Permissions

| Role | Permissions |
| :--- | :--- |
| **Admin** | Full control over the system. Can create/manage users, categories, and all products. Can generate dummy data and export all data. |
| **Staff** | Can view products uploaded by Agents and **approve** or **reject** them. Can export product data. |
| **Agent** | Can **create** new products and upload videos. Can only view and manage their **own** products. |
| **End User**| Can browse and view **approved** products. Can add products to a cart and place orders. |

## ⚙️ API Endpoints

The API is secured with token authentication and AES encryption.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/users/register/` | Register a new user. |
| `POST` | `/api/users/login/` | Log in and receive an auth token. |
| `POST` | `/api/users/logout/` | Log out and invalidate the token. |
| `GET`, `POST` | `/api/products/categories/` | List or create categories (Admin only). |
| `GET`, `PUT`, `DELETE` | `/api/products/categories/<id>/` | Retrieve, update, or delete a category (Admin only). |
| `GET`, `POST` | `/api/products/products/` | List products (role-dependent) or create a new one (Agent/Admin). |
| `GET`, `PUT`, `DELETE`| `/api/products/products/<id>/` | Retrieve, update, or delete a product. |
| `POST`| `/api/products/products/<id>/review/` | Approve or reject a product (Staff/Admin). |

## 🛠️ Management Commands

### Generate Dummy Data

You can easily populate the database with dummy data using a custom management command.

```bash
# Show available options
python manage.py generate_dummy_data --help

# Example: Generate 500 products and 15 categories using 8 threads
python manage.py generate_dummy_data --products 500 --categories 15 --threads 8