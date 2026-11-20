
# Activity 2.1 – MongoDB Atlas and Docker Comparison

## Objective
To connect Python to two MongoDB environments:
1. MongoDB running locally through Docker.
2. MongoDB Atlas cloud database.

The objective is to retrieve and compare their server version information using PyMongo's `server_info()` method.

## Technologies Used
- Python 3.13.5
- PyMongo 4.18.2
- MongoDB Docker 7.0
- MongoDB Atlas 8.0
- python-dotenv

## Implementation
The Python script uses MongoClient to establish connections to both MongoDB environments.

Connection details are stored securely in a `.env` file.

The `server_info()` method retrieves server information, including:
- MongoDB version
- Git version

The results are displayed in the terminal and saved to a JSON file.

## Execution Results

| Environment | MongoDB Version | Connection |
|---|---|---|
| Docker MongoDB | 7.0.45 | Successful |
| MongoDB Atlas | 8.0.39 | Successful |

## Observation
The local Docker MongoDB server runs version 7.0.45, while MongoDB Atlas runs version 8.0.39.

Therefore, the two MongoDB environments are running different server versions.

## Files
- `compare_mongodb.py` – Python implementation.
- `mongodb_info.json` – Retrieved server information.
- `output.txt` – Actual terminal execution output.

## Conclusion
Successfully connected Python to both local Docker MongoDB and MongoDB Atlas. Retrieved their server version information using `server_info()` and compared the results.

