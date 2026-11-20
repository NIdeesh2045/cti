from pymongo import MongoClient
from urllib.parse import quote_plus
from getpass import getpass

password = quote_plus(getpass("Enter app_user_read password: "))

client = MongoClient(
    f"mongodb://app_user_read:{password}@localhost:27221/analytics?authSource=analytics",
    tls=True,
    tlsCAFile="lab12/activity-12.2/certs/ca.crt",
    tlsCertificateKeyFile="lab12/activity-12.2/certs/client.pem",
    serverSelectionTimeoutMS=5000
)

try:
    print("MongoDB connection:", client.admin.command("ping"))
    print("Employee records:")
    for employee in client.analytics.employee_public.find():
        print(employee)
    print("TLS verification successful!")
finally:
    client.close()
