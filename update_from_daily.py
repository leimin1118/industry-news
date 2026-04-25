#!/usr/bin/env python3
"""
一键更新脚本：把AI新闻日报推送到行业网站并重新生成HTML
使用方式：python update_from_daily.py
"""

import json
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_website(news_items):
    """
    完整的网站更新流程：
    1. 将新闻数据格式化为网站JSON
    2. 重新生成网站HTML
    """
    # 切换到项目目录
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    sys.path.insert(0, project_dir)
    
    # 步骤1: 推送数据
    logger.info("📡 步骤1: 推送新闻数据...")
    from push_ai_daily import push_ai_daily
    summary_data = push_ai_daily(news_items)
    
    # 步骤2: 仅生成AI行业的网站（不收集其他行业避免覆盖）
    logger.info("🌐 步骤2: 生成网站...")
    from website_generator import WebsiteGenerator
    gen = WebsiteGenerator()
    
    # 加载推送后的数据
    today = datetime.now().strftime('%Y-%m-%d')
    summary_path = os.path.join('data', f'summary_{today}.json')
    with open(summary_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 直接生成HTML（跳过collector）
    gen._generate_html_files(data)
    gen._copy_static_resources()
    gen._generate_seo_files()
    
    logger.info("✅ 网站更新完成！")
    logger.info(f"   共 {len(news_items)} 条AI新闻已发布")
    logger.info(f"   查看: {os.path.join(project_dir, 'docs', 'index.html')}")
    
    return True


if __name__ == '__main__':
    # 从 stdin 或参数接收新闻
    if len(sys.argv) > 1 and sys.argv[1] == '--stdin':
        import json
        news_items = json.loads(sys.stdin.read())
        update_website(news_items)
    else:
        print("用法: python update_from_daily.py --stdin < news.json")
        print("或者直接导入使用")
