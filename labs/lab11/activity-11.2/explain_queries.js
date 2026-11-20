const database = db.getSiblingDB("lab11db");

const timestampQuery = {
    ts: {
        $gte: ISODate("2025-01-01T00:00:00Z"),
        $lt: ISODate("2025-01-02T00:00:00Z")
    }
};

const hashedQuery = {
    user_id: {
        $gte: ObjectId("000000000000000000000000"),
        $lt: ObjectId("ffffffffffffffffffffffff")
    }
};

print("\n===== TIMESTAMP RANGE QUERY =====");
const timestampExplain =
    database.hotspot_data.find(timestampQuery).explain("executionStats");

print("Winning plan:");
printjson(timestampExplain.queryPlanner.winningPlan);
print("Execution statistics:");
printjson(timestampExplain.executionStats);

print("\n===== HASHED KEY RANGE QUERY =====");
const hashedExplain =
    database.even_data.find(hashedQuery).explain("executionStats");

print("Winning plan:");
printjson(hashedExplain.queryPlanner.winningPlan);
print("Execution statistics:");
printjson(hashedExplain.executionStats);
