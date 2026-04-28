from flask_restful import Resource, reqparse
from flask import request
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from auth.auth_service import AuthService
from database import get_db
import asyncio

class RegisterResource(Resource):
    @swag_from({
        'tags': ['Auth'],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'password': {'type': 'string'}
                    },
                    'required': ['username', 'password']
                }
            }
        ],
        'responses': {
            '201': {
                'description': 'User registered successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'user_id': {'type': 'string'},
                        'username': {'type': 'string'}
                    }
                }
            },
            '400': {
                'description': 'User already exists or invalid input'
            }
        }
    })
    def post(self):
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return {'message': 'Username and password are required'}, 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._register_async(data))
            return result
        finally:
            loop.close()

    async def _register_async(self, data):
        db = await get_db()
        auth_service = AuthService(db)
        result = await auth_service.register_user(data['username'], data['password'])
        
        if 'error' in result:
            return {'message': result['error']}, 400
        
        return result, 201


class LoginResource(Resource):
    @swag_from({
        'tags': ['Auth'],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'password': {'type': 'string'}
                    },
                    'required': ['username', 'password']
                }
            }
        ],
        'responses': {
            '200': {
                'description': 'Login successful',
                'schema': {'$ref': '#/definitions/TokenResponse'}
            },
            '401': {
                'description': 'Invalid credentials'
            }
        }
    })
    def post(self):
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return {'message': 'Username and password are required'}, 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(self._login_async(data))
            return result
        finally:
            loop.close()

    async def _login_async(self, data):
        db = await get_db()
        auth_service = AuthService(db)
        user_id = await auth_service.validate_user(data['username'], data['password'])
        
        if not user_id:
            return {'message': 'Invalid credentials'}, 401
        
        tokens = await auth_service.create_tokens(user_id, data['username'])
        return tokens, 200


class RefreshResource(Resource):
    @jwt_required(refresh=True)
    @swag_from({
        'tags': ['Auth'],
        'security': [{'Bearer': []}],
        'responses': {
            '200': {
                'description': 'New access token generated',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'access_token': {'type': 'string'},
                        'token_type': {'type': 'string'}
                    }
                }
            },
            '401': {
                'description': 'Invalid or expired refresh token'
            }
        }
    })
    def post(self):
        current_user = get_jwt_identity()
        
        # Generate new access token using the identity from refresh token
        access_token = create_access_token(identity=current_user)
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }, 200
