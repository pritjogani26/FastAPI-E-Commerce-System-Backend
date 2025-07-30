<!DOCTYPE html>
<html lang="en">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FastAPI E-Commerce System Backend</title>
</head>

<body>
<h1>FastAPI E-Commerce System Backend</h1>

<p>
This <b>FastAPI-based E-Commerce system backend</b> is designed to handle the core functionalities of an online shopping platform,
built with modern technologies for fast performance, security, and scalability. The system covers a wide range of features, including
user authentication, product management, cart operations, order processing, and payment integration, all structured for smooth and
efficient operations.
</p>

<h2>Key Components:</h2>

<h3>User Authentication & Authorization</h3>
<ul>
<li>Utilizing <b>OAuth2</b> and <b>JWT tokens</b> for secure user authentication and session management.</li>
<li>Provides secure access to protected routes by verifying user credentials using JWT tokens.</li>
<li>Enables user registration and login processes, ensuring that sensitive data (like passwords) is securely stored and transmitted.</li>
</ul>

<h3>Product Management</h3>
<ul>
<li>CRUD operations for product listings, categories, and related data.</li>
<li>Admin users can add, edit, and delete products from the catalog, including assigning products to categories for better organization.</li>
<li>Each product has attributes such as price, description, stock quantity, and images to ensure complete product details.</li>
<li>Support for searching and filtering products based on various attributes like category, price range, and availability.</li>
</ul>

<h3>Shopping Cart</h3>
<ul>
<li>Adding, editing, and viewing items in the cart, along with order history.</li>
<li>Users can add multiple products to their cart and modify the quantity or remove items as needed.</li>
<li>Cart data is stored temporarily and linked to user accounts, allowing users to save their cart for future purchases.</li>
<li>Order history functionality allows users to view previous orders with complete details (items, price, status, etc.).</li>
</ul>

<h3>Email Integration</h3>
<ul>
<li>Email functionality for order confirmations, password resets, and user verification, utilizing <b>Redis</b> for optimized email processing.</li>
<li>Redis is used to queue email tasks for efficient handling of asynchronous tasks, ensuring that email notifications are sent reliably and quickly.</li>
<li>Supports templated email formats (HTML emails) for a more professional and consistent user experience during order placement and verification.</li>
<li>Users receive immediate confirmation emails after placing an order or resetting a password.</li>
</ul>

<h3>Payment Integration</h3>
<ul>
<li>Integrated with payment gateways for handling order payments and generating invoices.</li>
<li>Support for multiple payment methods, including credit/debit cards, digital wallets, and other third-party payment providers.</li>
<li>Ensures secure processing of payment transactions and confirmation of payments through integrated payment gateway APIs (e.g., Razorpay).</li>
</ul>

<h3>Database Interaction</h3>
<ul>
<li>Uses <b>SQLAlchemy ORM</b> to interact with <b>PostgreSQL</b>, handling data operations for users, products, orders, and more.</li>
<li>The database schema includes tables for storing user information, product details, cart data, orders, and payment status.</li>
<li>Supports advanced querying and filtering for product listings, order histories, and user data, ensuring smooth interactions with the backend.</li>
</ul>

<h2>Setup & Installation:</h2>

<h3>1. Run Redis in Docker</h3>
<pre><code>
docker run -d -p 6379:6379 redis
</code></pre>
<p>This command runs a Redis container in the background and maps port <b>6379</b> on the host machine to port <b>6379</b> inside the container.</p>

<h3>2. Create a Virtual Environment</h3>
<pre><code>
python -m venv venv
</code></pre>
<p>This command creates a virtual environment in the <b>venv</b> directory. A virtual environment ensures that your project dependencies are isolated and won’t interfere with other projects.</p>

<h3>3. Activate the Virtual Environment</h3>
<pre><code>
.\venv\Scripts\activate
</code></pre>
<p>This command activates the virtual environment on Windows. After activation, you can install packages specifically for this project.</p>

<h3>4. Install Dependencies</h3>
<pre><code>
pip install -r .\requirements.txt
</code></pre>
<p>This command installs all the dependencies listed in your <b>requirements.txt</b> file, including FastAPI, Celery, Redis, SQLAlchemy, and other required libraries.</p>

<h3>5. Run Celery Worker</h3>
<pre><code>
celery -A email_file.email_with_html.celery_app worker --pool=solo --loglevel=info
</code></pre>
<p>This starts a Celery worker that processes tasks asynchronously, such as sending emails or handling other background tasks.</p>

<h3>6. Run Uvicorn Server</h3>
<pre><code>
uvicorn main:app --reload
</code></pre>
<p>This command runs the FastAPI application using Uvicorn as the ASGI server with the <b>--reload</b> flag to automatically reload the server when code changes.</p>

<h2>Project Structure:</h2>
<table border="1" cellpadding="5" cellspacing="0">
<tr>
<th>Folder/File</th>
<th>Description</th>
</tr>
<tr>
<td><b>.env</b></td>
<td>Environment variables for the project (e.g., database URLs, secret keys).</td>
</tr>
<tr>
<td><b>main.py</b></td>
<td>Entry point for the FastAPI application. Contains app initialization and routes.</td>
</tr>
<tr>
<td><b>requirements.txt</b></td>
<td>List of dependencies for the project.</td>
</tr>
<tr>
<td><b>authentication_file/</b></td>
<td>Handles user authentication, hashing, and OAuth2 token operations.</td>
</tr>
<tr>
<td><b>database_file/</b></td>
<td>Contains database models, schemas, and other related functionality for PostgreSQL interaction.</td>
</tr>
<tr>
<td><b>email_file/</b></td>
<td>Handles email functions for user verification, order confirmation, etc.</td>
</tr>
<tr>
<td><b>payment_file/</b></td>
<td>Manages payment operations like handling payment gateways.</td>
</tr>
<tr>
<td><b>redis_file/</b></td>
<td>Contains Redis client and email task storage logic, optimizing email processing.</td>
</tr>
<tr>
<td><b>repository/</b></td>
<td>Repository layer handling all database queries for users, orders, products, etc.</td>
</tr>
<tr>
<td><b>routers/</b></td>
<td>Handles FastAPI routing for different functionalities like authentication, products, and orders.</td>
</tr>
<tr>
<td><b>static/</b></td>
<td>Contains static files like CSS, images, etc., used for frontend styling.</td>
</tr>
<tr>
<td><b>templates/</b></td>
<td>Contains HTML templates for rendering email content and other UI components.</td>
</tr>
</table>

<h2>Contributions</h2>
<p>
Contributions to this project are welcome! Please feel free to submit pull requests, report issues, or suggest improvements.
</p>

<h2>License</h2>
<p>
This project is licensed under the MIT License.
</p>
</body>

</html>
