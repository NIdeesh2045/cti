
CREATE KEYSPACE IF NOT EXISTS fraud_detection
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE fraud_detection;

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id TEXT,
    event_time TIMESTAMP,
    event_type TEXT,
    amount DOUBLE,
    description TEXT,
    PRIMARY KEY (user_id, event_time)
) WITH CLUSTERING ORDER BY (event_time DESC);

INSERT INTO user_profiles
(user_id, event_time, event_type, amount, description)
VALUES ('U001', '2026-11-20 10:00:00', 'LOGIN', 0, 'Normal login');

INSERT INTO user_profiles
(user_id, event_time, event_type, amount, description)
VALUES ('U001', '2026-11-20 10:05:00', 'TRANSFER', 5000, 'Transfer to U002');

INSERT INTO user_profiles
(user_id, event_time, event_type, amount, description)
VALUES ('U001', '2026-11-20 10:10:00', 'TRANSFER', 7500, 'Transfer to U003');

INSERT INTO user_profiles
(user_id, event_time, event_type, amount, description)
VALUES ('U002', '2026-11-20 10:06:00', 'RECEIVED', 5000, 'Received from U001');

INSERT INTO user_profiles
(user_id, event_time, event_type, amount, description)
VALUES ('U003', '2026-11-20 10:11:00', 'RECEIVED', 7500, 'Received from U001');
