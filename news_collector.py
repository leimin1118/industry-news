#!/usr/bin/env python3
"""
多行业新闻收集器
支持AI、电力、电商三个行业
"""

import json
import os
import sys
import time
import logging
from datetime import datetime
import subprocess
import tempfile

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('news_collection.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NewsCollector:
    """新闻收集器"""
    
    def __init__(self, config_path="config.json"):
        """初始化收集器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.industries = self.config['industries']
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 检查tavily CLI是否可用
        self.tavily_available = self._check_tavily_available()
        
    def _check_tavily_available(self):
        """检查tavily CLI是否可用"""
        try:
            result = subprocess.run(['tvly', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"tavily CLI可用: {result.stdout.strip()}")
                return True
        except FileNotFoundError:
            logger.warning("tavily CLI未安装，将使用模拟数据")
        
        return False
    
    def collect_news(self):
        """收集所有行业的新闻"""
        all_news = {}
        today = datetime.now().strftime('%Y-%m-%d')
        
        for industry_id, industry_info in self.industries.items():
            logger.info(f"开始收集 {industry_info['name']} 行业新闻...")
            
            try:
                # 尝试使用tavily收集真实新闻
                if self.tavily_available:
                    news_items = self._collect_with_tavily(industry_info)
                else:
                    news_items = self._generate_mock_news(industry_info)
                
                # 保存行业新闻数据
                industry_data = {
                    'industry_id': industry_id,
                    'industry_name': industry_info['name'],
                    'industry_name_en': industry_info['name_en'],
                    'color': industry_info['color'],
                    'icon': industry_info['icon'],
                    'collected_at': datetime.now().isoformat(),
                    'news_count': len(news_items),
                    'news_items': news_items
                }
                
                # 保存到文件
                output_file = os.path.join(self.data_dir, f"{industry_id}_{today}.json")
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(industry_data, f, ensure_ascii=False, indent=2)
                
                all_news[industry_id] = industry_data
                logger.info(f"  ✓ {industry_info['name']}: 收集到 {len(news_items)} 条新闻")
                
            except Exception as e:
                logger.error(f"收集 {industry_info['name']} 新闻失败: {e}")
                # 生成模拟数据作为降级方案
                mock_news = self._generate_mock_news(industry_info)
                all_news[industry_id] = {
                    'industry_id': industry_id,
                    'industry_name': industry_info['name'],
                    'news_count': len(mock_news),
                    'news_items': mock_news,
                    'is_mock_data': True
                }
                logger.info(f"  ⚠ {industry_info['name']}: 使用模拟数据 ({len(mock_news)} 条)")
        
        # 保存汇总数据
        summary_file = os.path.join(self.data_dir, f"summary_{today}.json")
        summary_data = {
            'date': today,
            'total_news': sum(len(data.get('news_items', [])) for data in all_news.values()),
            'industries': list(self.industries.keys()),
            'collection_time': datetime.now().isoformat(),
            'data': all_news
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"新闻收集完成！总计 {summary_data['total_news']} 条新闻")
        return summary_data
    
    def _collect_with_tavily(self, industry_info):
        """使用tavily CLI收集新闻"""
        news_items = []
        max_items = self.config['data_collection']['max_news_per_industry']
        
        # 对每个关键词进行搜索
        for keyword in industry_info['keywords'][:3]:  # 使用前3个关键词
            try:
                logger.debug(f"搜索关键词: {keyword}")
                
                # 构建tavily命令
                cmd = [
                    'tvly', 'search',
                    f'"{keyword}"',
                    '--topic', 'news',
                    '--time-range', 'day',
                    '--max-results', '5',
                    '--json'
                ]
                
                # 执行命令
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # 解析JSON结果
                    try:
                        search_results = json.loads(result.stdout)
                        if 'results' in search_results:
                            for item in search_results['results'][:3]:  # 每个关键词取前3条
                                news_item = {
                                    'title': item.get('title', ''),
                                    'summary': item.get('content', '')[:200],
                                    'url': item.get('url', '#'),
                                    'source': item.get('source', '未知来源'),
                                    'published_date': item.get('published_date', ''),
                                    'language': 'zh'
                                }
                                news_items.append(news_item)
                                
                                if len(news_items) >= max_items:
                                    break
                    except json.JSONDecodeError:
                        logger.warning(f"解析tavily结果失败: {result.stdout[:100]}")
                
                if len(news_items) >= max_items:
                    break
                    
                # 避免请求过快
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        return news_items[:max_items]
    
    def _generate_mock_news(self, industry_info):
        """生成模拟新闻数据"""
        mock_news = []
        max_items = self.config['data_collection']['max_news_per_industry']
        
        # AI行业模拟数据
        if industry_info['name'] == '人工智能':
            titles = [
                "OpenAI发布新一代推理模型，性能提升30%",
                "中国AI芯片突破7nm工艺，华为海思领先",
                "百度文心一言4.0正式发布，多项能力升级",
                "腾讯混元大模型通过国家备案",
                "字节跳动AI实验室发布多模态模型",
                "谷歌发布Gemini 2.0，比上一代快40%",
                "微软将AI集成到Windows 12系统",
                "Meta发布新的开源语言模型",
                "亚马逊增强AWS AI服务",
                "苹果在iOS 18中展示AI功能"
            ]
        elif industry_info['name'] == '电力能源':
            titles = [
                "国家电网推进智能电网建设",
                "新能源装机容量突破历史新高",
                "电力物联网技术取得重大突破",
                "储能产业发展迎来政策利好",
                "电力市场化改革深入推进",
                "清洁能源占比持续提升",
                "电力设备智能化升级加速",
                "电力行业数字化转型成效显著",
                "电力安全保障能力全面提升",
                "电力科技创新成果丰硕"
            ]
        else:  # 电子商务
            titles = [
                "电商平台618大促即将开启",
                "直播带货新规正式实施",
                "跨境电商迎来政策红利",
                "社交电商发展势头迅猛",
                "物流配送效率大幅提升",
                "数字营销创新模式不断涌现",
                "消费者购物行为变化分析",
                "电商平台竞争格局新变化",
                "农村电商助力乡村振兴",
                "电商行业数字化转型加速"
            ]
        
        for i in range(min(max_items, len(titles))):
            mock_news.append({
                'title': titles[i],
                'summary': f"这是关于{titles[i]}的最新行业动态，涉及{industry_info['name']}领域的重要进展。",
                'url': f"https://example.com/{industry_info['name']}/news{i}",
                'source': industry_info['sources'][i % len(industry_info['sources'])],
                'published_date': datetime.now().strftime('%Y-%m-%d'),
                'language': 'zh',
                'is_mock_data': True
            })
        
        return mock_news

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("多行业新闻收集器启动")
    logger.info("=" * 50)
    
    try:
        collector = NewsCollector()
        summary_data = collector.collect_news()
        
        # 打印统计信息
        logger.info("\n📊 收集统计:")
        for industry_id, data in summary_data['data'].items():
            industry_name = data.get('industry_name', industry_id)
            news_count = len(data.get('news_items', []))
            logger.info(f"  {industry_name}: {news_count} 条新闻")
        
        logger.info(f"\n✅ 新闻收集完成！数据已保存到 data/ 目录")
        logger.info(f"   总计: {summary_data['total_news']} 条新闻")
        logger.info(f"   日期: {summary_data['date']}")
        
    except Exception as e:
        logger.error(f"新闻收集失败: {e}", exc_info=True)
        return 1
    
    logger.info("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())