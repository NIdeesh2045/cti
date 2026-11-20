
# Experiment 13 – MongoDB Replica Set Deployment Using Docker Compose and Kubernetes

## Objective

To deploy and manage a three-node MongoDB replica set using Docker Compose and Kubernetes. The experiment covers keyfile authentication, data replication, automatic failover, persistent storage, pod recovery, and MongoDB monitoring.

## Technologies Used

- MongoDB 7.0
- Docker and Docker Compose
- Kubernetes (Docker Desktop)
- Python 3.12
- PyMongo 4.18.2
- Percona MongoDB Exporter 0.40
- OpenSSL

---

# Activity 13.1 – Deploy a Replica Set with Docker Compose

## 1. Objective

Deploy a three-node MongoDB replica set using Docker Compose with keyfile authentication. Verify replica set health, replication, automatic failover, and monitoring using a Prometheus exporter.

## 2. Architecture

Three MongoDB containers were deployed on a Docker bridge network.

| Container | Host Port | Initial Role |
|---|---:|---|
| lab13-mongo1 | 27317 | Primary |
| lab13-mongo2 | 27318 | Secondary |
| lab13-mongo3 | 27319 | Secondary |

Percona MongoDB exporter metrics were exposed on port 29215.

## 3. Keyfile Authentication

Generated a shared authentication key using OpenSSL:

```bash
openssl rand -base64 756 > keyfile
chmod 400 keyfile
```

The keyfile was mounted read-only into all three MongoDB containers and excluded from Git using `.gitignore`.

## 4. Replica Set Deployment

Started the MongoDB containers:

```bash
docker compose up -d mongo1 mongo2 mongo3
```

Initialized the replica set:

```javascript
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017" },
    { _id: 1, host: "mongo2:27017" },
    { _id: 2, host: "mongo3:27017" }
  ]
})
```

Created the `lab13_admin` user with the root role in the admin database and verified authenticated access.

## 5. Replication Verification

Inserted a test document into the `lab13_test` database on the primary node and successfully retrieved the same document from a secondary node.

## 6. Failover Verification

Executed:

```javascript
rs.stepDown(30)
```

MongoDB automatically elected another healthy member as the new primary.

A Python script (`failover_test.py`) using PyMongo was also executed inside the Docker network. It verified:

- Initial primary detection.
- Document insertion.
- Primary stepdown.
- New primary election.
- Successful write after failover.

### Observed PyMongo Results

- Initial primary: `mongo2:27017`
- New primary: `mongo3:27017`
- Write after failover: SUCCESS

## 7. Prometheus Exporter

Started the exporter:

```bash
docker compose up -d prometheus-exporter
```

Verified the metrics endpoint:

```bash
curl -s http://localhost:29215/metrics | grep -E "mongodb_up|mongodb_exporter"
```

Verified metric:

```text
mongodb_up 1
```

## 8. Result

Successfully deployed a three-node MongoDB replica set with keyfile authentication. Data replication, manual failover, PyMongo failover, and Prometheus exporter metrics were verified.

---

# Activity 13.2 – Kubernetes StatefulSet for MongoDB

## 1. Objective

Deploy a three-node MongoDB replica set using Kubernetes StatefulSet, persistent volume claims, a headless Service, and an InitContainer for keyfile preparation. Verify replica set health and automatic pod recovery.

## 2. Kubernetes Environment

- Kubernetes context: `docker-desktop`
- MongoDB image: `mongo:7.0`
- StatefulSet: `mongo`
- Replicas: 3
- Headless Service: `mongo`

## 3. Keyfile Configuration

Created a Kubernetes Secret from the shared keyfile:

```bash
kubectl create secret generic mongo-keyfile --from-file=keyfile=./keyfile
```

An InitContainer copied the keyfile from the Secret volume into a shared `emptyDir` volume, configured ownership and permissions, and made it available to the MongoDB container.

## 4. StatefulSet Deployment

Applied the Kubernetes manifest:

```bash
kubectl apply -f mongo-statefulset.yaml
```

Verified deployment:

```bash
kubectl get pods -o wide
kubectl get pvc
```

Three MongoDB pods were created:

- `mongo-0`
- `mongo-1`
- `mongo-2`

Each pod received a 1 GiB Persistent Volume Claim.

## 5. Replica Set Initialization

Connected to the first pod:

```bash
kubectl exec -it mongo-0 -- mongosh
```

Initialized the replica set:

```javascript
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo-0.mongo:27017" },
    { _id: 1, host: "mongo-1.mongo:27017" },
    { _id: 2, host: "mongo-2.mongo:27017" }
  ]
})
```

Created the `lab13_admin` user with the root role in the admin database.

## 6. Replica Set Health Verification

Verified all three members:

| Pod | Role | Health |
|---|---|---:|
| mongo-0 | Primary | 1 |
| mongo-1 | Secondary | 1 |
| mongo-2 | Secondary | 1 |

All members were healthy.

## 7. Pod Recovery Verification

Deleted one secondary pod:

```bash
kubectl delete pod mongo-2
```

Kubernetes automatically recreated the pod through the StatefulSet controller.

Verified recovery:

```bash
kubectl get pods -w
```

The recreated `mongo-2` pod successfully rejoined the replica set as a SECONDARY member.

## 8. Result

Successfully deployed a three-node MongoDB replica set using Kubernetes StatefulSet. Persistent storage, keyfile authentication, replica set initialization, pod recreation, and replica set recovery were verified.

---

# Comparison: Docker Compose vs Kubernetes

| Feature | Docker Compose | Kubernetes |
|---|---|---|
| Deployment | Docker Compose services | StatefulSet |
| Networking | Docker bridge network | Headless Service |
| Persistent Storage | Docker named volumes | Persistent Volume Claims |
| Authentication | Shared keyfile | Kubernetes Secret |
| Scaling | Manual service configuration | StatefulSet replicas |
| Recovery | Container restart policies | StatefulSet controller |
| Monitoring | Percona MongoDB Exporter | Not configured in this activity |
| Failover | MongoDB replica set election | MongoDB replica set election |

## Overall Conclusion

Experiment 13 successfully demonstrated MongoDB replica set deployment using two container orchestration approaches: Docker Compose and Kubernetes.

In Activity 13.1, a three-node replica set was deployed with keyfile authentication. Replication, automatic primary election, PyMongo failover, and Prometheus exporter metrics were verified.

In Activity 13.2, a three-node MongoDB StatefulSet was deployed with persistent storage, a headless Service, and shared keyfile authentication. Pod deletion and automatic recovery were successfully tested.

Both activities demonstrated high availability, replication, fault recovery, and deployment management for MongoDB.

## Project Structure

```text
labs/lab13/
├── README.md
├── activity-13.1/
│   ├── docker-compose.yml
│   ├── failover_test.py
│   ├── output.txt
│   └── .gitignore
└── activity-13.2/
    ├── mongo-statefulset.yaml
    ├── output.txt
    └── keyfile
```

**Note:** Authentication keyfiles and credentials must not be committed to Git.
