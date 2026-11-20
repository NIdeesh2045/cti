// Lab 12.1: MongoDB Authentication and RBAC
// Run as lab12_admin using mongosh with authentication.

const analytics = db.getSiblingDB("analytics");

analytics.createCollection("employees");
analytics.createCollection("reports");

analytics.employees.insertMany([
  { name: "Alice", department: "IT", salary: 80000 },
  { name: "Bob", department: "HR", salary: 65000 },
  { name: "Charlie", department: "Finance", salary: 75000 }
]);

analytics.reports.insertOne({
  title: "Quarterly Report",
  status: "Approved"
});

// Public view excludes salary.
analytics.createView("employee_public", "employees", [
  { $project: { _id: 0, name: 1, department: 1 } }
]);

analytics.createRole({
  role: "analyticsReader",
  privileges: [
    {
      resource: { db: "analytics", collection: "employee_public" },
      actions: ["find"]
    },
    {
      resource: { db: "analytics", collection: "reports" },
      actions: ["find"]
    }
  ],
  roles: []
});

analytics.createRole({
  role: "analyticsWriter",
  privileges: [
    {
      resource: { db: "analytics", collection: "reports" },
      actions: ["find", "insert", "update", "remove"]
    }
  ],
  roles: []
});

print("RBAC setup definitions completed.");
print("Create users separately using passwordPrompt() as documented.");
