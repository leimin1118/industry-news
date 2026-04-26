#!/usr/bin/env python3
"""
行业信息网站主程序
整合新闻收集和网站生成
"""

import os
import sys
import json
import glob
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('industry_website.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("行业信息聚合网站系统启动")
    logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    try:
        # 1. 检查是否有手动推送的AI新闻数据
        logger.info("\n📰 步骤1: 检查已有新闻数据")
        logger.info("-" * 40)
        
        import glob
        data_dir = "data"
        summary_files = sorted(glob.glob(os.path.join(data_dir, "summary_*.json")), reverse=True)
        
        if summary_files:
            # 读取最新的汇总文件
            latest_file = summary_files[0]
            with open(latest_file, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            logger.info(f"找到已有数据: {os.path.basename(latest_file)}, 共 {news_data.get('total_news', 0)} 条新闻")
        else:
            # 没有数据时收集新闻
            logger.info("未找到已有数据，开始收集新闻...")
            from news_collector import NewsCollector
            collector = NewsCollector()
            news_data = collector.collect_news()
            
            if not news_data or news_data['total_news'] == 0:
                logger.warning("新闻收集结果为空")
        
        # 2. 生成网站
        logger.info("\n🌐 步骤2: 生成静态网站")
        logger.info("-" * 40)
        
        from website_generator import WebsiteGenerator
        generator = WebsiteGenerator()
        success = generator.generate_website()
        
        if not success:
            logger.error("网站生成失败")
            return 1
        
        # 2.5 更新世界地图版首页的新闻数据
        logger.info("\n🗺️  步骤2.5: 更新世界地图首页动态数据")
        logger.info("-" * 40)
        
        try:
            from update_worldmap_data import update_html
            if news_data:
                update_html(news_data)
                logger.info("世界地图首页数据已同步！")
            else:
                logger.warning("没有新闻数据可同步到世界地图")
        except Exception as e:
            logger.warning(f"世界地图首页更新跳过: {e}")
        
        # 3. 输出统计信息
        logger.info("\n📊 步骤3: 生成统计报告")
        logger.info("-" * 40)
        
        if news_data:
            _print_statistics(news_data)
        
        # 4. 下一步建议
        logger.info("\n🚀 步骤4: 后续操作建议")
        logger.info("-" * 40)
        
        _print_next_steps()
        
    except Exception as e:
        logger.error(f"系统执行失败: {e}", exc_info=True)
        return 1
    
    logger.info("=" * 60)
    logger.info("✅ 系统执行完成！")
    logger.info("=" * 60)
    return 0

def _print_statistics(data):
    """打印统计信息"""
    if not data:
        logger.info("无有效数据")
        return
    
    logger.info("📈 今日数据统计:")
    logger.info(f"   更新日期: {data.get('date', '未知')}")
    logger.info(f"   新闻总数: {data.get('total_news', 0)} 条")
    logger.info(f"   覆盖行业: {len(data.get('industries', []))} 个")
    
    logger.info("\n🏭 各行业详情:")
    for industry_id in data.get('industries', []):
        industry_data = data['data'].get(industry_id, {})
        industry_name = industry_data.get('industry_name', industry_id)
        news_count = len(industry_data.get('news_items', []))
        is_mock = industry_data.get('is_mock_data', False)
        
        mock_tag = " (模拟数据)" if is_mock else ""
        logger.info(f"   • {industry_name}: {news_count} 条新闻{mock_tag}")
    
    # 检查数据质量
    mock_count = sum(1 for industry_data in data['data'].values() 
                    if industry_data.get('is_mock_data', False))
    
    if mock_count > 0:
        logger.info(f"\n⚠️  注意: {mock_count} 个行业使用了模拟数据")
        logger.info("     建议安装tavily CLI以获得真实新闻")
        logger.info("     命令: curl -fsSL https://cli.tavily.com/install.sh | bash")

def _print_next_steps():
    """打印后续步骤建议"""
    logger.info("1. 🖥️  本地预览网站:")
    logger.info("   打开 docs/index.html 文件")
    
    logger.info("\n2. 🚀 部署到 GitHub Pages (推荐):")
    logger.info("   a. 在GitHub创建新仓库")
    logger.info("   b. 将 docs/ 目录内容推送到仓库")
    logger.info("   c. 在仓库设置中启用 GitHub Pages")
    logger.info("   d. 访问: https://<用户名>.github.io/<仓库名>/")
    
    logger.info("\n3. ⚡ 部署到 Vercel (最快速):")
    logger.info("   a. 访问 https://vercel.com")
    logger.info("   b. 导入GitHub仓库")
    logger.info("   c. 自动部署，获得专业域名")
    
    logger.info("\n4. 🔄 设置自动更新:")
    logger.info("   使用GitHub Actions或定时任务自动运行本脚本")
    
    logger.info("\n5. 🛠️  自定义配置:")
    logger.info("   编辑 config.json 调整行业、关键词等")

def run_test():
    """测试运行"""
    print("🧪 行业信息网站系统测试")
    print("=" * 50)
    
    # 测试配置加载
    try:
        import json
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"✅ 配置加载成功")
        print(f"   网站名称: {config['website']['name']}")
        print(f"   覆盖行业: {len(config['industries'])} 个")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return 1
    
    # 测试模块导入
    try:
        from news_collector import NewsCollector
        from website_generator import WebsiteGenerator
        print("✅ 模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return 1
    
    print("\n🎯 系统就绪，可以运行:")
    print("   python main.py          # 完整运行")
    print("   python news_collector.py # 只收集新闻")
    print("   python website_generator.py # 只生成网站")
    
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        sys.exit(run_test())
    else:
        sys.exit(main())