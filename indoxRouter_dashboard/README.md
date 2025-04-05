# IndoxRouter Dashboard

## Quick Setup Steps

1. **Install Dependencies**

   ```
   pip install -r requirements.txt
   ```

2. **Configure Environment**

   - Create `.env` file with:

   ```
   POSTGRES_URI=postgresql://username:password@localhost:5432/indoxrouter
   MONGODB_URI=mongodb://localhost:27017/indoxrouter
   MONGODB_DATABASE=indoxrouter
   SECRET_KEY=your_secret_key_here
   HASH_SALT=your_hash_salt_here
   ```

3. **Start Dashboard**
   ```
   python start_dashboard.py
   ```

## Docker Setup

```
docker build -t indoxrouter-dashboard .
docker run -p 8501:8501 \
  -e POSTGRES_URI=postgresql://username:password@host:5432/indoxrouter \
  -e MONGODB_URI=mongodb://host:27017/indoxrouter \
  -e MONGODB_DATABASE=indoxrouter \
  -e SECRET_KEY=your_secret_key_here \
  -e HASH_SALT=your_hash_salt_here \
  indoxrouter-dashboard
```

## Schema Fix Information

The dashboard automatically fixes the `transaction_type` column issue on startup by:

1. Running `setup_db.setup_database()` to check for missing columns
2. Adding the `transaction_type` column if it doesn't exist

If you encounter schema issues, manually run:

```
python setup_db.py
```
