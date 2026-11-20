cfg = rs.conf();

cfg.members[0].priority = 1; // mongo1
cfg.members[1].priority = 3; // mongo2
cfg.members[2].priority = 2; // mongo3
cfg.members[3].priority = 0; // arbiter

rs.reconfig(cfg);

print("Replica set priorities updated.");

printjson(
  rs.conf().members.map(member => ({
    host: member.host,
    priority: member.priority,
    arbiter: member.arbiterOnly || false
  }))
);
