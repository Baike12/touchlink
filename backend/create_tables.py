#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.src.config.database import engine
from backend.src.core.models import Base, AnalyticsTemplate

# 创建所有表
def create_tables():
    # 只创建不存在的表
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建/更新")

if __name__ == "__main__":
    create_tables()
    print("数据库表已更新，包括新增的analytics_templates表") 