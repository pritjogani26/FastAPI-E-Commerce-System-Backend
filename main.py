#main.py

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from database_file import models
from database_file.database import engine
from routers import admin, authentication, cart, category, order, payment, product,user, user_details
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret123")

# Allow all origins for testing
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory="static"), name="static")
models.Base.metadata.create_all(engine)

@app.get('/')
def Redirect() :
    html_content = """
    <html>
        <head>
            <title>Redirecting...</title>
            <script type="text/javascript">
                setTimeout(function() {
                    window.location.href = "http://127.0.0.1:8000/docs";
                }, 5000); // Wait for 5 seconds and then redirect
            </script>
        </head>
        <body>
            <h3>You will be redirected to the documentation in 5 seconds...</h3>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(product.router)
app.include_router(category.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(payment.router)
app.include_router(user_details.router)
app.include_router(admin.router)
