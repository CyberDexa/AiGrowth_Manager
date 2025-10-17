from sqlalchemy import text
from app.db.database import engine

conn = engine.connect()
result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
tables = [r[0] for r in result]
print("Created tables:", tables)
print(f"\nTotal tables: {len(tables)}")
