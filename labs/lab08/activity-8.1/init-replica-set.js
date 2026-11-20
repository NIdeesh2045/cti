rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "lab08-mongo1:27017" },
    { _id: 1, host: "lab08-mongo2:27017" },
    { _id: 2, host: "lab08-mongo3:27017" }
  ]
});

use("lab08_replication");

db.replication_test.insertOne({
  message: "MongoDB replica set replication test",
  lab: "Lab 08.1",
  createdAt: new Date()
});

print("Replica set initialization and test document insertion completed.");
