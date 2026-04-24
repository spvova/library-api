from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from api.books import BooksResource, BookResource
from database import client
from schemas.book import BookCreate, Book

app = Flask(__name__)
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
        "description": "A simple library API with Flask and MongoDB",
        "version": "1.0.0"
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
        }
    }
})

# Add resources
api.add_resource(BooksResource, '/books')
api.add_resource(BookResource, '/books/<book_id>')

@app.teardown_appcontext
def shutdown_session(exception=None):
    client.close()

if __name__ == '__main__':
    app.run(debug=True)