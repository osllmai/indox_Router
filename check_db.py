import os
import sys

# Add server directory to path
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "indoxrouter_server")
)

try:
    from app.db.database import init_db, get_pg_connection, release_pg_connection
    from app.core.config import settings

    print("Successfully imported modules")

    def check_db():
        print("Initializing DB connection...")
        success = init_db()
        print(f"DB initialization: {success}")

        if not success:
            return

        try:
            # Check PostgreSQL
            conn = get_pg_connection()
            try:
                with conn.cursor() as cur:
                    # Check usage_daily_summary table
                    cur.execute("SELECT COUNT(*) FROM usage_daily_summary")
                    count = cur.fetchone()[0]
                    print(f"Usage daily summary records: {count}")

                    # Check users table
                    cur.execute("SELECT COUNT(*) FROM users")
                    count = cur.fetchone()[0]
                    print(f"Users: {count}")

                    # Check api_requests table
                    cur.execute("SELECT COUNT(*) FROM api_requests")
                    count = cur.fetchone()[0]
                    print(f"API requests: {count}")
            finally:
                release_pg_connection(conn)

            # Check MongoDB
            from pymongo import MongoClient

            mongo_client = MongoClient(settings.MONGODB_URI)
            mongo_db = mongo_client[settings.MONGODB_DATABASE]

            # Check model_usage collection
            count = mongo_db.model_usage.count_documents({})
            print(f"MongoDB model_usage documents: {count}")

            # Check conversations collection
            count = mongo_db.conversations.count_documents({})
            print(f"MongoDB conversations documents: {count}")

        except Exception as e:
            print(f"Error checking database: {e}")

    if __name__ == "__main__":
        check_db()
except Exception as e:
    print(f"Import error: {e}")
