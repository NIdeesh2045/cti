# Activity 12.1: Configure Authentication and RBAC

## Objective
Configure MongoDB authentication and role-based access control to restrict database operations based on user permissions.

## Implementation
1. Enabled MongoDB authentication using `--auth`.
2. Created an administrator user with the root role.
3. Created the `analytics` database with `employees` and `reports` collections.
4. Created two custom roles:
   - `analyticsReader`: read access to `employee_public` and `reports`.
   - `analyticsWriter`: read, insert, update, and remove access to `reports`.
5. Created `app_user_read` and `app_user_write`.
6. Created the `employee_public` view excluding the salary field.

## Verification
- Read user successfully queried the public employee view.
- Read user was denied access to the original employees collection.
- Write user successfully inserted and queried reports.
- Write user was denied access to the employees collection.

## Files
- `setup_rbac.js` – RBAC setup definitions.
- `test_rbac.js` – Permission verification script.
- `output.txt` – Recorded test results.

## Result
Authentication, collection-level RBAC, and field-level redaction were successfully demonstrated.
