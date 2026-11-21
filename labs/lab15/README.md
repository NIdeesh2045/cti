# Lab 15 – Multi-Tenant Architecture and Data Migration

## 1. Overview

This experiment focuses on implementing a multi-tenant application using MongoDB and FastAPI, followed by migrating data between different tenant isolation strategies.

It consists of two activities:

- **Activity 15.1:** Multi-Tenant API with tenant isolation, authentication, authorization, and rate limiting.
- **Activity 15.2:** Data migration from document-level isolation to collection-per-tenant isolation, followed by performance benchmarking.

## 2. Objectives

- Implement a multi-tenant architecture using MongoDB.
- Ensure tenant-level data isolation.
- Develop CRUD operations using FastAPI.
- Implement JWT-based authentication.
- Implement role-based access control (RBAC).
- Implement rate limiting using MongoDB.
- Migrate data between tenant isolation strategies.
- Validate migration accuracy and prevent cross-tenant data leakage.
- Compare performance between isolation strategies.

## 3. Technologies Used

- Python
- FastAPI
- MongoDB
- PyMongo
- JWT Authentication
- Pydantic
- Uvicorn

---

# Activity 15.1 – Multi-Tenant API

## 4. Objective

To develop a secure multi-tenant Task Management API where multiple tenants can use the same application while maintaining independent data access.

## 5. Implementation

### 5.1 Database Design

Created a MongoDB database named `tasktracker` with the following collections:

- `users`
- `tasks`
- `rate_limits`

Each task contains a `tenant_id` field to identify its tenant.

A compound index was created using `tenant_id` and `created_at` to support tenant-specific queries.

### 5.2 Authentication

Implemented JWT-based authentication.

Users authenticate using:

- Tenant ID
- Username
- Password

After successful authentication, the API generates a JWT containing user identity, tenant ID, and role.

### 5.3 Role-Based Access Control

Two user roles were implemented:

- **Admin:** Can manage and view all tasks belonging to their own tenant.
- **Regular User:** Can access and manage only their own tasks.

### 5.4 CRUD Operations

Implemented the following task endpoints:

- `POST /tasks/` – Create a task.
- `GET /tasks/` – List accessible tasks.
- `GET /tasks/{task_id}` – Retrieve a task.
- `PUT /tasks/{task_id}` – Update a task.
- `DELETE /tasks/{task_id}` – Delete a task.

All task queries enforce tenant-level filtering.

### 5.5 Rate Limiting

Implemented MongoDB-backed rate limiting using atomic counter updates.

The configured limit is 100 requests per minute per authenticated user.

A TTL index is used to automatically expire old rate-limit records.

## 6. Testing and Verification

The following tests were performed:

| Test | Result |
|---|---|
| MongoDB connection | PASSED |
| API health check | PASSED |
| JWT authentication | PASSED |
| Alice task creation | PASSED |
| Bob user-level isolation | PASSED |
| Bob task creation and retrieval | PASSED |
| Charlie cross-tenant isolation | PASSED |
| Tenant-scoped admin user listing | PASSED |

### Key Results

- Alice, an admin in `tenant_a`, successfully created a task.
- Bob, a regular user in `tenant_a`, could not view Alice's task.
- Bob successfully created and viewed his own task.
- Charlie, an admin in `tenant_b`, could not access tasks belonging to `tenant_a`.
- Charlie could view only users belonging to `tenant_b`.

**Activity 15.1 Result: Successfully implemented and tested.**

---

# Activity 15.2 – Data Migration Between Tenant Isolation Strategies

## 7. Objective

To migrate data from document-level tenant isolation to collection-per-tenant isolation, validate the migration, and compare the performance of both strategies.

## 8. Dataset Creation

Created a dataset containing five tenants with 100 tasks each.

| Tenant | Number of Tasks |
|---|---:|
| tenant_a | 100 |
| tenant_b | 100 |
| tenant_c | 100 |
| tenant_d | 100 |
| tenant_e | 100 |
| **Total** | **500** |

Database: `tenant_migration`

Source collection: `tasks`

## 9. Tenant Isolation Strategies

### 9.1 Document-Level Isolation

All tenant documents are stored in one shared collection. Each document contains a `tenant_id` field to identify its tenant.

### 9.2 Collection-Per-Tenant Isolation

Each tenant receives a separate MongoDB collection:

- `tasks_tenant_a`
- `tasks_tenant_b`
- `tasks_tenant_c`
- `tasks_tenant_d`
- `tasks_tenant_e`

## 10. Data Migration

The `migrate.py` script performs the following operations:

1. Reads documents from the shared tasks collection.
2. Filters documents using `tenant_id`.
3. Creates a separate collection for each tenant.
4. Copies the tenant's documents into its collection.
5. Validates source and destination document counts.
6. Checks for cross-tenant data leakage.

### Migration Results

| Tenant | Source | Migrated | Leakage | Status |
|---|---:|---:|---:|---|
| tenant_a | 100 | 100 | 0 | PASS |
| tenant_b | 100 | 100 | 0 | PASS |
| tenant_c | 100 | 100 | 0 | PASS |
| tenant_d | 100 | 100 | 0 | PASS |
| tenant_e | 100 | 100 | 0 | PASS |
| **Total** | **500** | **500** | **0** | **PASS** |

**Migration Result: SUCCESS**

## 11. Performance Benchmarking

The `benchmark.py` script compares both isolation strategies using three operations:

- Listing 100 tasks.
- Creating a task.
- Cross-tenant analytics.

Each operation was measured over 100 iterations.

### Benchmark Results

| Operation | Document-Level (ms) | Collection-Per-Tenant (ms) |
|---|---:|---:|
| Listing 100 tasks | 0.6084 | 0.3759 |
| Creating a task | 2.1632 | 1.8230 |
| Cross-tenant analytics | 0.4361 | 1.2915 |

### Observations

- Collection-per-tenant performed faster for listing tasks.
- Collection-per-tenant performed faster for task creation.
- Document-level isolation performed faster for cross-tenant analytics.

These measurements represent the local test environment and dataset used in this experiment.

## 12. Comparison of Isolation Strategies

| Feature | Document-Level | Collection-Per-Tenant |
|---|---|---|
| Data storage | Shared collection | Separate collections |
| Tenant identification | `tenant_id` field | Collection name |
| Data management | Simpler | Tenant-specific |
| Listing performance in test | 0.6084 ms | 0.3759 ms |
| Creation performance in test | 2.1632 ms | 1.8230 ms |
| Analytics performance in test | 0.4361 ms | 1.2915 ms |

## 13. Conclusion

The experiment successfully implemented a multi-tenant Task Management API with JWT authentication, role-based access control, tenant-level isolation, and MongoDB-backed rate limiting.

The second activity successfully migrated 500 documents belonging to five tenants from a shared collection into separate tenant collections. All five tenant collections passed validation with zero cross-tenant data leakage.

Performance benchmarking showed that collection-per-tenant isolation performed better for individual tenant listing and task creation in this test, whereas document-level isolation performed better for cross-tenant analytics.

Document-level isolation is suitable for applications requiring simpler database management and shared analytics. Collection-per-tenant isolation is useful when stronger physical separation and tenant-specific data management are required.

**Overall Lab 15 completed successfully.**