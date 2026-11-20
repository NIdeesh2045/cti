# Lab 12: MongoDB RBAC and TLS Security

## Objective
To implement MongoDB authentication, role-based access control (RBAC), field-level redaction, and TLS encryption for secure database communication.

## Activities

### Activity 12.1: Authentication and RBAC
- Enabled MongoDB authentication using `--auth`.
- Created an administrator account.
- Created application users with separate read and write roles.
- Restricted permissions to specific collections.
- Created an employee view excluding the salary field.
- Tested authorized and unauthorized database operations.

**Result:** Authentication, RBAC, and field-level redaction were successfully verified.

### Activity 12.2: TLS Encryption
- Generated a Certificate Authority (CA).
- Generated server and client certificates.
- Configured MongoDB with `--tlsMode requireTLS`.
- Verified that unencrypted connections were rejected.
- Tested secure connections using mongosh and Python PyMongo.

**Result:** TLS connections and certificate verification were successfully tested.

## Project Structure

- `docker-compose.yml` – MongoDB authentication and TLS configuration.
- `activity-12.1/` – RBAC scripts, test results, and documentation.
- `activity-12.2/` – TLS test script, certificate setup, results, and documentation.

## Conclusion
MongoDB authentication, collection-level authorization, field-level redaction, and encryption in transit were implemented and tested successfully.
