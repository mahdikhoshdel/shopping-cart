# Shopping Cart Project

This is a Django-based shopping cart project that integrates Celery for background tasks. Below you'll find instructions on how to run and test the project.

## Setup

Before running the project, make sure to set up a Python environment and install the necessary dependencies. You can create a virtual environment and install the requirements using the following commands:

```bash
# Create a virtual environment (if not already created)
python -m venv .venv

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
## Redis setup
```bash
sudo apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Run server and Celery worker and Celery beat in independent terminal from each other
## Run the Server

To run the Django development server:

```bash
python manage.py runserver
```

This will start the server on `http://127.0.0.1:8000/` (default). You can access the application in your browser.

## Run Celery Worker

To run the Celery worker, open a terminal and use the following command:

```bash
celery -A shopping_cart worker --loglevel=info
```

This will start the Celery worker, which listens for background tasks like adding items to the cart or processing other tasks asynchronously.

## Run Celery Beat

To run Celery Beat (used for scheduling periodic tasks), use this command:

```bash
celery -A shopping_cart beat --loglevel=info
```

This will start the Celery Beat scheduler that ensures periodic tasks are executed at specified intervals.

## Run Tests

To run the tests for the cart app, use the following command:

```bash
python manage.py test cart
```

This will execute the test suite and display results in the terminal. It ensures that your application works as expected.

---

## Project Structure

- **cart/**: Contains the logic and models for the shopping cart.
- **shopping_cart/**: Contains the main Django settings and configurations.
- **requirements.txt**: The list of required dependencies for the project.

---

This is a light weight project and doesnt use docker cause usage of sqlite and locking database problem
