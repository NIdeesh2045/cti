db.adminCommand({
  setDefaultRWConcern: 1,
  defaultWriteConcern: { w: "majority" }
});

rs.addArb("lab08-arbiter:27017");

print("Arbiter added successfully.");

printjson(
  rs.status().members.map(member => ({
    host: member.name,
    state: member.stateStr,
    health: member.health
  }))
);
