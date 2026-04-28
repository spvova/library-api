from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from flask_jwt_extended import JWTManager
from api.books import BooksResource, BookResource
from api.auth import LoginResource, RefreshResource, RegisterResource
from database import client
from schemas.book import BookCreate, Book
import os

app = Flask(__name__)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 900  # 15 хвилин 
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 7 днів

jwt = JWTManager(app)

api = Api(app)

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, config=swagger_config, template={
    "swagger": "2.0",
    "info": {
        "title": "Library API",
        "description": "A simple library API with Flask and MongoDB with JWT authentication",
        "version": "1.0.0"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "definitions": {
        "Book": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "author": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["available", "issued"]},
                "year": {"type": "integer"}
            },
            "required": ["id", "title", "author", "status", "year"]
        },
        "BookCreate": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "author": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["available", "issued"]},
                "year": {"type": "integer"}
            },
            "required": ["title", "author", "status", "year"]
        },
        "TokenResponse": {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "refresh_token": {"type": "string"},
                "token_type": {"type": "string"}
            }
        }
    }
})

# Add authentication resources
api.add_resource(RegisterResource, '/auth/register')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(RefreshResource, '/auth/refresh')

# Add protected book resources
api.add_resource(BooksResource, '/books')
api.add_resource(BookResource, '/books/<book_id>')

@app.teardown_appcontext
def shutdown_session(exception=None):
    client.close()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
