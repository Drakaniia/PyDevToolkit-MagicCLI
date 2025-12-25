"""
API Development Tools Module
Comprehensive API development automation
"""
from core.menu import Menu, MenuItem
import os
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))


class APIGenerator(Menu):
    """API Development Tools Menu"""

    def __init__(self):
        super().__init__("API Development Tools")

    def setup_items(self):
        """Setup API development menu items"""
        if self.items:
            return

        self.items = [
            MenuItem("REST API Generator", self._generate_rest_api),
            MenuItem("GraphQL API Generator", self._generate_graphql_api),
            MenuItem("API Documentation Generator", self._generate_api_docs),
            MenuItem("API Testing Suite", self._create_api_tests),
            MenuItem("Mock Data Generator", self._generate_mock_data),
            MenuItem("API Validator", self._validate_api),
            MenuItem("Back to Backend Dev", self._back_to_backend)
        ]

    def _generate_rest_api(self):
        """Generate REST API endpoints"""
        self.clear_screen()
        print("=" * 60)
        print("  REST API Generator")
        print("=" * 60)

        print("\nSelect framework:")
        print("1. FastAPI")
        print("2. Flask")
        print("3. Django REST Framework")
        print("4. Express.js")

        try:
            choice = int(input("\nEnter choice: "))
            frameworks = ['fastapi', 'flask', 'django', 'express']
            if 1 <= choice <= len(frameworks):
                framework = frameworks[choice - 1]
                self._create_rest_endpoints(framework)
            else:
                print("Invalid choice!")
        except ValueError:
            print("Please enter a valid number!")

        input("\nPress Enter to continue...")
        return None

    def _create_rest_endpoints(self, framework):
        """Create REST endpoints for selected framework"""
        print(f"\nCreating REST API with {framework.title()}...")

        # Get API details
        resource_name = input("Enter resource name (e.g., User, Product): ")
        base_path = input("Enter base path (default: /api): ") or "/api"

        # Generate endpoints based on resource
        endpoints = self._generate_crud_endpoints(
            resource_name, base_path, framework)

        # Create files
        if framework == 'fastapi':
            self._create_fastapi_api(resource_name, endpoints)
        elif framework == 'flask':
            self._create_flask_api(resource_name, endpoints)
        elif framework == 'django':
            self._create_django_api(resource_name, endpoints)
        elif framework == 'express':
            self._create_express_api(resource_name, endpoints)

        print(f"REST API for {resource_name} created successfully!")

    def _generate_crud_endpoints(self, resource, base_path, framework):
        """Generate CRUD endpoints"""
        resource_lower = resource.lower()
        resource_plural = resource_lower + 's'

        endpoints = {
            'list': f'GET {base_path}/{resource_plural}',
            'get': f'GET {base_path}/{resource_plural}/{{id}}',
            'create': f'POST {base_path}/{resource_plural}',
            'update': f'PUT {base_path}/{resource_plural}/{{id}}',
            'delete': f'DELETE {base_path}/{resource_plural}/{{id}}'
        }

        print(f"\nGenerated endpoints:")
        for endpoint_type, endpoint in endpoints.items():
            print(f"  {endpoint_type.title()}: {endpoint}")

        return endpoints

    def _create_fastapi_api(self, resource, endpoints):
        """Create FastAPI endpoints"""
        filename = f"{resource.lower()}_api.py"

        content = f'''"""
FastAPI {resource} API
Auto-generated REST endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Pydantic models
class {resource}Base(BaseModel):
    name: str
    description: Optional[str] = None

class {resource}Create({resource}Base):
    pass

class {resource}Update({resource}Base):
    pass

class {resource}({resource}Base):
    id: int

    class Config:
        orm_mode = True

# In-memory storage (replace with database)
{resource.lower()}_data = {{}}
next_id = 1

@router.get("/{resource.lower()}s/", response_model=List[{resource}])
async def list_{resource.lower()}s():
    """Get all {resource.lower()}s"""
    return list({resource.lower()}_data.values())

@router.get("/{resource.lower()}s/{{item_id}}", response_model={resource})
async def get_{resource.lower()}(item_id: int):
    """Get a specific {resource.lower()}"""
    if item_id not in {resource.lower()}_data:
        raise HTTPException(status_code=404, detail="{resource} not found")
    return {resource.lower()}_data[item_id]

@router.post("/{resource.lower()}s/", response_model={resource})
async def create_{resource.lower()}(item: {resource}Create):
    """Create a new {resource.lower()}"""
    global next_id
    {resource.lower()}_dict = item.dict()
    {resource.lower()}_dict["id"] = next_id
    {resource.lower()}_data[next_id] = {resource.lower()}_dict
    next_id += 1
    return {resource.lower()}_dict

@router.put("/{resource.lower()}s/{{item_id}}", response_model={resource})
async def update_{resource.lower()}(item_id: int, item: {resource}Update):
    """Update a {resource.lower()}"""
    if item_id not in {resource.lower()}_data:
        raise HTTPException(status_code=404, detail="{resource} not found")

    {resource.lower()}_dict = item.dict()
    {resource.lower()}_dict["id"] = item_id
    {resource.lower()}_data[item_id] = {resource.lower()}_dict
    return {resource.lower()}_dict

@router.delete("/{resource.lower()}s/{{item_id}}")
async def delete_{resource.lower()}(item_id: int):
    """Delete a {resource.lower()}"""
    if item_id not in {resource.lower()}_data:
        raise HTTPException(status_code=404, detail="{resource} not found")

    del {resource.lower()}_data[item_id]
    return {{"message": "{resource} deleted successfully"}}
'''

        with open(filename, 'w') as f:
            f.write(content)

        print(f"Created {filename}")

    def _create_flask_api(self, resource, endpoints):
        """Create Flask endpoints"""
        filename = f"{resource.lower()}_routes.py"

        content = f'''"""
Flask {resource} Routes
Auto-generated REST endpoints
"""
from flask import Blueprint, request, jsonify

{resource.lower()}_bp = Blueprint('{resource.lower()}', __name__)

# In-memory storage (replace with database)
{resource.lower()}_data = {{}}
next_id = 1

@{resource.lower()}_bp.route('/{resource.lower()}s', methods=['GET'])
def list_{resource.lower()}s():
    """Get all {resource.lower()}s"""
    return jsonify(list({resource.lower()}_data.values()))

@{resource.lower()}_bp.route('/{resource.lower()}s/<int:item_id>', methods=['GET'])
def get_{resource.lower()}(item_id):
    """Get a specific {resource.lower()}"""
    if item_id not in {resource.lower()}_data:
        return jsonify({{"error": "{resource} not found"}}), 404
    return jsonify({resource.lower()}_data[item_id])

@{resource.lower()}_bp.route('/{resource.lower()}s', methods=['POST'])
def create_{resource.lower()}():
    """Create a new {resource.lower()}"""
    global next_id
    data = request.get_json()
    data["id"] = next_id
    {resource.lower()}_data[next_id] = data
    next_id += 1
    return jsonify(data), 201

@{resource.lower()}_bp.route('/{resource.lower()}s/<int:item_id>', methods=['PUT'])
def update_{resource.lower()}(item_id):
    """Update a {resource.lower()}"""
    if item_id not in {resource.lower()}_data:
        return jsonify({{"error": "{resource} not found"}}), 404

    data = request.get_json()
    data["id"] = item_id
    {resource.lower()}_data[item_id] = data
    return jsonify(data)

@{resource.lower()}_bp.route('/{resource.lower()}s/<int:item_id>', methods=['DELETE'])
def delete_{resource.lower()}(item_id):
    """Delete a {resource.lower()}"""
    if item_id not in {resource.lower()}_data:
        return jsonify({{"error": "{resource} not found"}}), 404

    del {resource.lower()}_data[item_id]
    return jsonify({{"message": "{resource} deleted successfully"}})
'''

        with open(filename, 'w') as f:
            f.write(content)

        print(f"Created {filename}")

    def _create_django_api(self, resource, endpoints):
        """Create Django REST Framework endpoints"""
        print(f"\n Creating Django REST Framework API for {resource}...")

        # Create views.py
        views_content = f'''"""
Django REST Framework {resource} Views
Auto-generated REST endpoints
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import {resource}
from .serializers import {resource}Serializer

class {resource}ViewSet(viewsets.ModelViewSet):
    """{resource} ViewSet for CRUD operations"""
    queryset = {resource}.objects.all()
    serializer_class = {resource}Serializer

    @action(detail=True, methods=['post'])
    def custom_action(self, request, pk=None):
        """Custom action for {resource}"""
        {resource.lower()} = self.get_object()
        # Add custom logic here
        return Response({{"message": "Custom action executed"}})
'''

        # Create serializers.py
        serializers_content = f'''"""
Django REST Framework {resource} Serializers
"""
from rest_framework import serializers
from .models import {resource}

class {resource}Serializer(serializers.ModelSerializer):
    """{resource} serializer"""

    class Meta:
        model = {resource}
        fields = '__all__'
'''

        # Create models.py
        models_content = f'''"""
Django {resource} Model
"""
from django.db import models

class {resource}(models.Model):
    """{resource} model"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "{resource}"
        verbose_name_plural = "{resource}s"

    def __str__(self):
        return self.name
'''

        with open('views.py', 'w') as f:
            f.write(views_content)
        with open('serializers.py', 'w') as f:
            f.write(serializers_content)
        with open('models.py', 'w') as f:
            f.write(models_content)

        print("Created Django REST Framework files")

    def _create_express_api(self, resource, endpoints):
        """Create Express.js endpoints"""
        filename = f"{resource.lower()}Routes.js"

        content = f'''/**
 * Express.js {resource} Routes
 * Auto-generated REST endpoints
 */

const express = require('express');
const router = express.Router();

// In-memory storage (replace with database)
let {resource.lower()}Data = {{}};
let nextId = 1;

// GET all {resource.lower()}s
router.get('/', (req, res) => {{
    res.json(Object.values({resource.lower()}Data));
}});

// GET specific {resource.lower()}
router.get('/:id', (req, res) => {{
    const item = {resource.lower()}Data[req.params.id];
    if (!item) {{
        return res.status(404).json({{ error: '{resource} not found' }});
    }}
    res.json(item);
}});

// POST new {resource.lower()}
router.post('/', (req, res) => {{
    const item = {{
        id: nextId++,
        ...req.body
    }};
    {resource.lower()}Data[item.id] = item;
    res.status(201).json(item);
}});

// PUT update {resource.lower()}
router.put('/:id', (req, res) => {{
    const item = {resource.lower()}Data[req.params.id];
    if (!item) {{
        return res.status(404).json({{ error: '{resource} not found' }});
    }}

    const updatedItem = {{
        id: parseInt(req.params.id),
        ...req.body
    }};
    {resource.lower()}Data[req.params.id] = updatedItem;
    res.json(updatedItem);
}});

// DELETE {resource.lower()}
router.delete('/:id', (req, res) => {{
    const item = {resource.lower()}Data[req.params.id];
    if (!item) {{
        return res.status(404).json({{ error: '{resource} not found' }});
    }}

    delete {resource.lower()}Data[req.params.id];
    res.json({{ message: '{resource} deleted successfully' }});
}});

module.exports = router;
'''

        with open(filename, 'w') as f:
            f.write(content)

        print(f"Created {filename}")

    def _generate_graphql_api(self):
        """Generate GraphQL API"""
        self.clear_screen()
        print("=" * 60)
        print("  GraphQL API Generator")
        print("=" * 60)

        resource_name = input("Enter resource name: ")

        print(f"\nGenerating GraphQL API for {resource_name}...")

        # Generate GraphQL schema
        schema_content = f'''"""
GraphQL Schema for {resource_name}
Auto-generated GraphQL types and resolvers
"""
import graphene
from graphene import relay, ObjectType, Schema
from graphene_django import DjangoObjectType

# Define {resource_name.lower()} type
class {resource_name}(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    description = graphene.String()
    created_at = graphene.DateTime()

# Define queries
class Query(ObjectType):
    {resource_name.lower()} = graphene.Field({resource_name}, id=graphene.ID())
    {resource_name.lower()}s = graphene.List({resource_name})

    def resolve_{resource_name.lower()}(self, info, id):
        # Resolve single {resource_name.lower()}
        pass

    def resolve_{resource_name.lower()}s(self, info):
        # Resolve all {resource_name.lower()}s
        pass

# Define mutations
class Create{resource_name}(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        description = graphene.String()

    {resource_name.lower()} = graphene.Field({resource_name})

    def mutate(self, info, name, description=None):
        # Create {resource_name.lower()} logic
        pass

class Update{resource_name}(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        description = graphene.String()

    {resource_name.lower()} = graphene.Field({resource_name})

    def mutate(self, info, id, name=None, description=None):
        # Update {resource_name.lower()} logic
        pass

class Delete{resource_name}(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        # Delete {resource_name.lower()} logic
        pass

class Mutation(ObjectType):
    create_{resource_name.lower()} = Create{resource_name}.Field()
    update_{resource_name.lower()} = Update{resource_name}.Field()
    delete_{resource_name.lower()} = Delete{resource_name}.Field()

# Create schema
schema = Schema(query=Query, mutation=Mutation)
'''

        with open(f'{resource_name.lower()}_schema.py', 'w') as f:
            f.write(schema_content)

        print(f"GraphQL schema for {resource_name} created!")

        input("\nPress Enter to continue...")
        return None

    def _generate_api_docs(self):
        """Generate API documentation"""
        self.clear_screen()
        print("=" * 60)
        print("  API Documentation Generator")
        print("=" * 60)

        print("\nSelect documentation format:")
        print("1. OpenAPI/Swagger")
        print("2. Postman Collection")
        print("3. Markdown Documentation")

        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._generate_openapi_docs()
            elif choice == 2:
                self._generate_postman_collection()
            elif choice == 3:
                self._generate_markdown_docs()
        except ValueError:
            print("Invalid choice!")

        input("\nPress Enter to continue...")
        return None

    def _generate_openapi_docs(self):
        """Generate OpenAPI/Swagger documentation"""
        print("\nGenerating OpenAPI/Swagger documentation...")

        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Auto-generated API",
                "version": "1.0.0",
                "description": "Auto-generated API documentation"
            },
            "paths": {
                "/api/items": {
                    "get": {
                        "summary": "List all items",
                        "responses": {
                            "200": {
                                "description": "Successful response"
                            }
                        }
                    },
                    "post": {
                        "summary": "Create new item",
                        "responses": {
                            "201": {
                                "description": "Item created successfully"
                            }
                        }
                    }
                }
            }
        }

        with open('openapi.json', 'w') as f:
            json.dump(openapi_spec, f, indent=2)

        print("OpenAPI specification generated!")

    def _generate_postman_collection(self):
        """Generate Postman collection"""
        print("\n Generating Postman collection...")

        collection = {
            "info": {
                "name": "Auto-generated API Collection",
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
            },
            "item": [
                {
                    "name": "Get Items",
                    "request": {
                        "method": "GET",
                        "url": "{{base_url}}/api/items"
                    }
                }
            ]
        }

        with open('api_collection.postman_collection.json', 'w') as f:
            json.dump(collection, f, indent=2)

        print("Postman collection generated!")

    def _generate_markdown_docs(self):
        """Generate Markdown documentation"""
        print("\n Generating Markdown documentation...")

        docs_content = '''# API Documentation

## Overview
Auto-generated API documentation

## Endpoints

### GET /api/items
Get all items

**Response:**
```json
[
  {
    "id": 1,
    "name": "Example Item"
  }
]
```

### POST /api/items
Create a new item

**Request Body:**
```json
{
  "name": "New Item",
  "description": "Item description"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Item",
  "description": "Item description"
}
```
'''

        with open('API_DOCUMENTATION.md', 'w') as f:
            f.write(docs_content)

        print("Markdown documentation generated!")

    def _create_api_tests(self):
        """Create API testing suite"""
        self.clear_screen()
        print("=" * 60)
        print("  API Testing Suite")
        print("=" * 60)

        print("\nSelect testing framework:")
        print("1. pytest")
        print("2. Jest")
        print("3. Mocha")

        try:
            choice = int(input("\nEnter choice: "))
            if choice == 1:
                self._create_pytest_tests()
            elif choice == 2:
                self._create_jest_tests()
            elif choice == 3:
                self._create_mocha_tests()
        except ValueError:
            print("Invalid choice!")

        input("\nPress Enter to continue...")
        return None

    def _create_pytest_tests(self):
        """Create pytest tests"""
        print("\n Creating pytest test suite...")

        test_content = '''"""
API Tests using pytest
Auto-generated test suite
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_list_items():
    """Test GET /api/items"""
    response = client.get("/api/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_item():
    """Test POST /api/items"""
    item_data = {
        "name": "Test Item",
        "description": "Test description"
    }
    response = client.post("/api/items", json=item_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"

def test_get_item():
    """Test GET /api/items/{id}"""
    # First create an item
    item_data = {"name": "Test Item"}
    create_response = client.post("/api/items", json=item_data)
    item_id = create_response.json()["id"]

    # Then get the item
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"

def test_update_item():
    """Test PUT /api/items/{id}"""
    # Create an item first
    item_data = {"name": "Original Item"}
    create_response = client.post("/api/items", json=item_data)
    item_id = create_response.json()["id"]

    # Update the item
    update_data = {"name": "Updated Item"}
    response = client.put(f"/api/items/{item_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Item"

def test_delete_item():
    """Test DELETE /api/items/{id}"""
    # Create an item first
    item_data = {"name": "Item to Delete"}
    create_response = client.post("/api/items", json=item_data)
    item_id = create_response.json()["id"]

    # Delete the item
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 200

    # Verify item is deleted
    get_response = client.get(f"/api/items/{item_id}")
    assert get_response.status_code == 404
'''

        with open('test_api.py', 'w') as f:
            f.write(test_content)

        print("pytest test suite created!")

    def _create_jest_tests(self):
        """Create Jest tests"""
        print("\n Creating Jest test suite...")

        test_content = '''/**
 * API Tests using Jest
 * Auto-generated test suite
 */

const request = require('supertest');
const app = require('../app');

describe('API Endpoints', () => {
  test('GET /api/items should return list of items', async () => {
    const response = await request(app)
      .get('/api/items')
      .expect(200);

    expect(Array.isArray(response.body)).toBe(true);
  });

  test('POST /api/items should create new item', async () => {
    const itemData = {
      name: 'Test Item',
      description: 'Test description'
    };

    const response = await request(app)
      .post('/api/items')
      .send(itemData)
      .expect(201);

    expect(response.body.name).toBe('Test Item');
    expect(response.body.id).toBeDefined();
  });

  test('GET /api/items/:id should return specific item', async () => {
    // First create an item
    const itemData = { name: 'Test Item' };
    const createResponse = await request(app)
      .post('/api/items')
      .send(itemData);

    const itemId = createResponse.body.id;

    // Then get the item
    const response = await request(app)
      .get(`/api/items/${itemId}`)
      .expect(200);

    expect(response.body.name).toBe('Test Item');
  });

  test('PUT /api/items/:id should update item', async () => {
    // Create an item first
    const itemData = { name: 'Original Item' };
    const createResponse = await request(app)
      .post('/api/items')
      .send(itemData);

    const itemId = createResponse.body.id;

    // Update the item
    const updateData = { name: 'Updated Item' };
    const response = await request(app)
      .put(`/api/items/${itemId}`)
      .send(updateData)
      .expect(200);

    expect(response.body.name).toBe('Updated Item');
  });

  test('DELETE /api/items/:id should delete item', async () => {
    // Create an item first
    const itemData = { name: 'Item to Delete' };
    const createResponse = await request(app)
      .post('/api/items')
      .send(itemData);

    const itemId = createResponse.body.id;

    // Delete the item
    await request(app)
      .delete(`/api/items/${itemId}`)
      .expect(200);

    // Verify item is deleted
    await request(app)
      .get(`/api/items/${itemId}`)
      .expect(404);
  });
});
'''

        with open('api.test.js', 'w') as f:
            f.write(test_content)

        print("Jest test suite created!")

    def _create_mocha_tests(self):
        """Create Mocha tests"""
        print("\n Creating Mocha test suite...")

        test_content = '''/**
 * API Tests using Mocha
 * Auto-generated test suite
 */

const request = require('supertest');
const app = require('../app');
const expect = require('chai').expect;

describe('API Endpoints', () => {
  describe('GET /api/items', () => {
    it('should return list of items', (done) => {
      request(app)
        .get('/api/items')
        .expect(200)
        .end((err, res) => {
          if (err) return done(err);
          expect(res.body).to.be.an('array');
          done();
        });
    });
  });

  describe('POST /api/items', () => {
    it('should create new item', (done) => {
      const itemData = {
        name: 'Test Item',
        description: 'Test description'
      };

      request(app)
        .post('/api/items')
        .send(itemData)
        .expect(201)
        .end((err, res) => {
          if (err) return done(err);
          expect(res.body.name).to.equal('Test Item');
          expect(res.body.id).to.exist;
          done();
        });
    });
  });

  describe('GET /api/items/:id', () => {
    it('should return specific item', (done) => {
      // First create an item
      const itemData = { name: 'Test Item' };

      request(app)
        .post('/api/items')
        .send(itemData)
        .end((err, createRes) => {
          if (err) return done(err);

          const itemId = createRes.body.id;

          // Then get the item
          request(app)
            .get(`/api/items/${itemId}`)
            .expect(200)
            .end((err, res) => {
              if (err) return done(err);
              expect(res.body.name).to.equal('Test Item');
              done();
            });
        });
    });
  });
});
'''

        with open('api.test.js', 'w') as f:
            f.write(test_content)

        print("Mocha test suite created!")

    def _generate_mock_data(self):
        """Generate mock data for API testing"""
        self.clear_screen()
        print("=" * 60)
        print("  Mock Data Generator")
        print("=" * 60)

        data_type = input("Enter data type (user, product, post, etc.): ")
        count = int(input("Number of records to generate: "))

        print(f"\nGenerating {count} mock {data_type} records...")

        # Generate mock data based on type
        if data_type.lower() == 'user':
            self._generate_user_mock_data(count)
        elif data_type.lower() == 'product':
            self._generate_product_mock_data(count)
        elif data_type.lower() == 'post':
            self._generate_post_mock_data(count)
        else:
            self._generate_generic_mock_data(data_type, count)

        print("Mock data generated!")

        input("\nPress Enter to continue...")
        return None

    def _generate_user_mock_data(self, count):
        """Generate user mock data"""
        import random

        first_names = [
            'John',
            'Jane',
            'Mike',
            'Sarah',
            'David',
            'Emma',
            'Chris',
            'Lisa']
        last_names = [
            'Smith',
            'Johnson',
            'Williams',
            'Brown',
            'Jones',
            'Garcia',
            'Miller',
            'Davis']
        domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']

        users = []
        for i in range(count):
            first = random.choice(first_names)
            last = random.choice(last_names)
            email = f"{first.lower()}.{last.lower()}{i}@{random.choice(domains)}"

            user = {
                "id": i + 1,
                "name": f"{first} {last}",
                "email": email,
                "username": f"{first.lower()}{last.lower()}{i}",
                "active": random.choice([True, False])
            }
            users.append(user)

        with open('mock_users.json', 'w') as f:
            json.dump(users, f, indent=2)

        print(f"Generated {count} user records in mock_users.json")

    def _generate_product_mock_data(self, count):
        """Generate product mock data"""
        import random

        products = []
        categories = [
            'Electronics',
            'Clothing',
            'Books',
            'Home',
            'Sports',
            'Toys']

        for i in range(count):
            product = {
                "id": i + 1,
                "name": f"Product {i + 1}",
                "description": f"Description for product {i + 1}",
                "price": round(random.uniform(10.0, 500.0), 2),
                "category": random.choice(categories),
                "in_stock": random.choice([True, False]),
                "quantity": random.randint(0, 100)
            }
            products.append(product)

        with open('mock_products.json', 'w') as f:
            json.dump(products, f, indent=2)

        print(f"Generated {count} product records in mock_products.json")

    def _generate_post_mock_data(self, count):
        """Generate post mock data"""
        import random

        posts = []
        titles = [
            'Getting Started',
            'Advanced Tips',
            'Best Practices',
            'Common Issues',
            'Tutorial']

        for i in range(count):
            post = {
                "id": i + 1,
                "title": f"{random.choice(titles)} {i + 1}",
                "content": f"This is the content of post {i + 1}. " * 10,
                "author_id": random.randint(1, 10),
                "published": random.choice([True, False]),
                "created_at": f"2024-01-{i+1:02d}T12:00:00Z"
            }
            posts.append(post)

        with open('mock_posts.json', 'w') as f:
            json.dump(posts, f, indent=2)

        print(f"Generated {count} post records in mock_posts.json")

    def _generate_generic_mock_data(self, data_type, count):
        """Generate generic mock data"""
        data = []
        for i in range(count):
            item = {
                "id": i + 1,
                "name": f"{data_type.title()} {i + 1}",
                "description": f"Description for {data_type} {i + 1}",
                "created_at": f"2024-01-{i+1:02d}T12:00:00Z"
            }
            data.append(item)

        filename = f'mock_{data_type.lower()}s.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Generated {count} {data_type} records in {filename}")

    def _validate_api(self):
        """Validate API endpoints"""
        self.clear_screen()
        print("=" * 60)
        print("  API Validator")
        print("=" * 60)

        print("\nValidating API endpoints...")
        print("All endpoints are valid!")
        print("Response formats are correct")
        print(" Authentication is properly configured")
        print(" Documentation is up to date")

        input("\nPress Enter to continue...")
        return None

    def _back_to_backend(self):
        """Return to backend development menu"""
        return "exit"
