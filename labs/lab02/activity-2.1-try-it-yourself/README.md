
# Activity 2.1 – Try It Yourself
## MongoDB Server Details Comparison

### Objective
To compare additional configuration and server information between Docker MongoDB and MongoDB Atlas using PyMongo's server_info() method.

### Implementation
The Python script connects to both MongoDB servers and retrieves:
- MongoDB version
- Git version
- Architecture
- Memory allocator
- JavaScript engine
- Maximum BSON object size
- Supported storage engines
- Server modules

### Results

| Property | Docker MongoDB | MongoDB Atlas |
|---|---|---|
| Version | 7.0.45 | 8.0.39 |
| Bits | 64 | 64 |
| Allocator | tcmalloc | tcmalloc-google |
| JavaScript Engine | mozjs | mozjs |
| Storage Engines | devnull, wiredTiger | devnull, inMemory, queryable_wt, wiredTiger |
| Modules | None | enterprise |

### Observation
Both servers use a 64-bit architecture and the mozjs JavaScript engine. Their allocators, supported storage engines, and modules differ.

### Conclusion
Successfully retrieved and compared additional server configuration information from Docker MongoDB and MongoDB Atlas.

