// Clear all collections in MongoDB indoxrouter database
// Run this with: mongo mongodb://localhost:27018/indoxrouter clear_mongodb.js

// Connect to the indoxrouter database
db = db.getSiblingDB("indoxrouter");

// Get all collections
var collections = db.getCollectionNames();

// Drop each collection
collections.forEach(function (collectionName) {
  // Skip system collections
  if (!collectionName.startsWith("system.")) {
    print("Dropping collection: " + collectionName);
    db[collectionName].drop();
  }
});

print("All MongoDB collections have been cleared from IndoxRouter database.");
