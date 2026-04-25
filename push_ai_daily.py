#!/usr/bin/env python3
"""
AI新闻日报 → 行业网站 推送脚本
把每日AI新闻日报的数据格式化为网站需要的JSON格式，并重新生成网站
"""

import json
import os
import sys
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def push_ai_daily(news_items):
    """
    把AI新闻日报条目推送到网站数据
    news_items: 字典列表，每条包含 title, summary, source, url
    """
    today = datetime.now().strftime('%Y-%m-%d')
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    logger.info(f"📡 推送 {len(news_items)} 条AI新闻到网站数据...")
    
    # 构造成 industry JSON 格式
    industry_data = {
        'industry_id': 'ai',
        'industry_name': '人工智能',
        'industry_name_en': 'Artificial Intelligence',
        'color': '#4CAF50',
        'icon': '🤖',
        'collected_at': datetime.now().isoformat(),
        'news_count': len(news_items),
        'news_items': []
    }
    
    for i, item in enumerate(news_items):
        news_entry = {
            'title': item.get('title', ''),
            'summary': item.get('summary', '')[:200],
            'url': item.get('url', '#'),
            'source': item.get('source', 'AI新闻日报'),
            'published_date': today,
            'language': 'zh',
            'is_mock_data': False
        }
        industry_data['news_items'].append(news_entry)
    
    # 保存行业数据文件
    industry_file = os.path.join(data_dir, f'ai_{today}.json')
    with open(industry_file, 'w', encoding='utf-8') as f:
        json.dump(industry_data, f, ensure_ascii=False, indent=2)
    logger.info(f"  ✓ AI行业数据保存: {industry_file}")
    
    # 创建 summary 汇总文件（只包含AI行业）
    summary_data = {
        'date': today,
        'total_news': len(news_items),
        'industries': ['ai'],
        'collection_time': datetime.now().isoformat(),
        'data': {
            'ai': industry_data
        }
    }
    
    summary_file = os.path.join(data_dir, f'summary_{today}.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=2)
    logger.info(f"  ✓ 汇总文件保存: {summary_file}")
    
    logger.info(f"✅ 推送完成！共 {len(news_items)} 条新闻已写入数据文件")
    return summary_data


if __name__ == '__main__':
    # 测试运行
    test_items = [
        {
            'title': '测试新闻',
            'summary': '这是一条测试新闻',
            'source': '测试来源',
            'url': 'https://example.com/test'
        }
    ]
    push_ai_daily(test_items)
    print("测试完成")
