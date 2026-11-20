// Lab 12.1: RBAC verification
// Run with app_user_read or app_user_write.

const analytics = db.getSiblingDB("analytics");

print("\n--- RBAC TEST ---");
print("Connected user:");
print(db.runCommand({ connectionStatus: 1 }).authInfo.authenticatedUsers);

function test(label, operation) {
  try {
    print("\n" + label);
    printjson(operation());
    print("RESULT: ALLOWED");
  } catch (error) {
    print("RESULT: DENIED");
    print(error.message);
  }
}

test("Read public employee view", () =>
  analytics.employee_public.find().toArray()
);

test("Read original employee collection", () =>
  analytics.employees.find().toArray()
);

test("Read reports", () =>
  analytics.reports.find().toArray()
);

test("Insert report", () =>
  analytics.reports.insertOne({
    title: "RBAC Test Report",
    status: "Test"
  })
);

print("\n--- TEST COMPLETE ---");
