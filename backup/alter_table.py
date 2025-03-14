import sys
sys.path.append('.')
from src.config.database import engine
from sqlalchemy import text
from src.core.models import Base, AnalyticsTemplate

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE dashboards MODIFY user_id VARCHAR(36) NULL'))
    conn.commit()
    print("Table altered successfully")

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("数据库表已更新，包括新增的analytics_templates表")
