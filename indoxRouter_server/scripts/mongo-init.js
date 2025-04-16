// MongoDB initialization script
print("MongoDB initialization starting...");
print("###############################################################");
print("This output should be visible in the logs");
print("###############################################################");

try {
  // Debug prints for troubleshooting
  print("Attempting to get environment variables");

  // Get environment variables directly from the container environment
  const MONGO_USER = process.env.MONGO_APP_USER || "appuser";
  const MONGO_PASS = process.env.MONGO_APP_PASSWORD || "password";

  print("Using credentials: User=" + MONGO_USER);
  print("###############################################################");

  // Create app user in admin database
  db.getSiblingDB("admin").createUser({
    user: MONGO_USER,
    pwd: MONGO_PASS,
    roles: [
      { role: "readWrite", db: "indoxrouter" },
      { role: "dbAdmin", db: "indoxrouter" },
    ],
  });

  print("###############################################################");
  print("User " + MONGO_USER + " created successfully in admin database");
  print("###############################################################");

  // Switch to application database and create collections/indexes
  db = db.getSiblingDB("indoxrouter");
  db.createCollection("conversations");
  db.createCollection("model_usage");
  db.createCollection("embeddings");
  db.model_usage.createIndex({ timestamp: -1 });
  db.conversations.createIndex({ user_id: 1 });
  db.embeddings.createIndex({ vector: "2dsphere" });

  print("###############################################################");
  print("MongoDB initialization completed successfully.");
  print("###############################################################");
} catch (error) {
  print("###############################################################");
  print("Error during MongoDB initialization:");
  printjson(error);
  print("###############################################################");
}
