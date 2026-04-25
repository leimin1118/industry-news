#!/usr/bin/env python3
"""
静态网站生成器
生成包含AI、电力、电商行业新闻的静态网站
"""

import json
import os
import sys
import shutil
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('website_generation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebsiteGenerator:
    """网站生成器"""
    
    def __init__(self, config_path="config.json"):
        """初始化生成器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.industries = self.config['industries']
        self.website_config = self.config['website']
        self.data_dir = "data"
        self.output_dir = "docs"  # GitHub Pages要求
        os.makedirs(self.output_dir, exist_ok=True)
        
    def generate_website(self):
        """生成完整网站"""
        logger.info("开始生成静态网站...")
        
        # 1. 加载最新数据
        latest_data = self._load_latest_data()
        if not latest_data:
            logger.error("没有找到新闻数据，请先运行新闻收集器")
            return False
        
        # 2. 生成HTML文件
        self._generate_html_files(latest_data)
        
        # 3. 复制静态资源
        self._copy_static_resources()
        
        # 4. 生成sitemap和robots.txt
        self._generate_seo_files()
        
        logger.info("✅ 网站生成完成！")
        return True
    
    def _load_latest_data(self):
        """加载最新的新闻数据"""
        try:
            # 查找最新的汇总文件
            data_files = [f for f in os.listdir(self.data_dir) if f.startswith('summary_')]
            if not data_files:
                logger.error("没有找到数据文件")
                return None
            
            # 按日期排序，取最新的
            data_files.sort(reverse=True)
            latest_file = data_files[0]
            data_path = os.path.join(self.data_dir, latest_file)
            
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return None
    
    def _generate_html_files(self, data):
        """生成HTML文件"""
        # 1. 生成首页
        self._generate_index_html(data)
        
        # 2. 生成行业详情页
        for industry_id in self.industries.keys():
            self._generate_industry_html(data, industry_id)
        
        # 3. 生成关于页面
        self._generate_about_html()
    
    def _generate_index_html(self, data):
        """生成首页"""
        logger.info("生成首页...")
        
        # 准备数据
        today = datetime.now().strftime('%Y年%m月%d日')
        total_news = data['total_news']
        
        # 生成行业卡片HTML
        industry_cards = ""
        for industry_id, industry_info in self.industries.items():
            industry_data = data['data'].get(industry_id, {})
            news_count = len(industry_data.get('news_items', []))
            
            industry_cards += f"""
            <div class="industry-card" style="border-left: 5px solid {industry_info['color']};">
                <div class="industry-header">
                    <span class="industry-icon">{industry_info['icon']}</span>
                    <h3>{industry_info['name']}</h3>
                    <span class="news-count">{news_count}条新闻</span>
                </div>
                <p class="industry-desc">{industry_info['name_en']}</p>
                <div class="industry-news-preview">
                    {self._generate_news_preview(industry_data.get('news_items', []))}
                </div>
                <a href="{industry_id}.html" class="view-more">查看全部新闻 →</a>
            </div>
            """
        
        # 生成热门新闻
        hot_news = self._generate_hot_news(data)
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.website_config['name']} - {today}</title>
    <meta name="description" content="{self.website_config['description']}">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <h1><i class="fas fa-newspaper"></i> {self.website_config['name']}</h1>
                <p class="tagline">{self.website_config['description']}</p>
            </div>
            <nav>
                <ul>
                    <li><a href="index.html" class="active"><i class="fas fa-home"></i> 首页</a></li>
                    {"".join([f'<li><a href="{industry_id}.html">{industry_info["icon"]} {industry_info["name"]}</a></li>' for industry_id, industry_info in self.industries.items()])}
                    <li><a href="about.html"><i class="fas fa-info-circle"></i> 关于</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <div class="hero-content">
                <h2>每日行业动态汇总</h2>
                <p class="date"><i class="far fa-calendar-alt"></i> 更新日期：{today}</p>
                <p class="stats"><i class="fas fa-chart-line"></i> 今日收录 {total_news} 条行业新闻</p>
            </div>
        </section>

        <section class="hot-news">
            <h2><i class="fas fa-fire"></i> 今日热点新闻</h2>
            <div class="hot-news-grid">
                {hot_news}
            </div>
        </section>

        <section class="industries">
            <h2><i class="fas fa-industry"></i> 行业分类</h2>
            <div class="industry-grid">
                {industry_cards}
            </div>
        </section>

        <section class="stats-section">
            <h2><i class="fas fa-chart-bar"></i> 数据统计</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-newspaper"></i></div>
                    <div class="stat-number">{total_news}</div>
                    <div class="stat-label">今日新闻总数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-industry"></i></div>
                    <div class="stat-number">{len(self.industries)}</div>
                    <div class="stat-label">覆盖行业</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-sync-alt"></i></div>
                    <div class="stat-number">每日</div>
                    <div class="stat-label">更新频率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon"><i class="fas fa-robot"></i></div>
                    <div class="stat-number">AI驱动</div>
                    <div class="stat-label">内容收集</div>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>{self.website_config['name']}</h3>
                    <p>{self.website_config['description']}</p>
                </div>
                <div class="footer-section">
                    <h3>快速导航</h3>
                    <ul>
                        {"".join([f'<li><a href="{industry_id}.html">{industry_info["icon"]} {industry_info["name"]}</a></li>' for industry_id, industry_info in self.industries.items()])}
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>关于我们</h3>
                    <p>由 {self.website_config['author']} 提供技术支持</p>
                    <p>AI驱动的行业信息聚合平台</p>
                </div>
            </div>
            <div class="copyright">
                <p>© {datetime.now().year} {self.website_config['author']} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p class="tech-note">本网站内容由AI自动收集整理，信息仅供参考</p>
            </div>
        </div>
    </footer>

    <script src="js/script.js"></script>
</body>
</html>"""
        
        output_path = os.path.join(self.output_dir, "index.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✓ 首页已生成: {output_path}")
    
    def _generate_industry_html(self, data, industry_id):
        """生成行业详情页"""
        logger.info(f"生成{self.industries[industry_id]['name']}行业页面...")
        
        industry_info = self.industries[industry_id]
        industry_data = data['data'].get(industry_id, {})
        news_items = industry_data.get('news_items', [])
        today = datetime.now().strftime('%Y年%m月%d日')
        
        # 生成新闻列表
        news_list = ""
        for i, news in enumerate(news_items, 1):
            news_list += f"""
            <article class="news-item">
                <div class="news-number">{i}</div>
                <div class="news-content">
                    <h3><a href="{news.get('url', '#')}" target="_blank">{news.get('title', '')}</a></h3>
                    <div class="news-meta">
                        <span class="source"><i class="fas fa-newspaper"></i> {news.get('source', '未知来源')}</span>
                        <span class="date"><i class="far fa-calendar-alt"></i> {news.get('published_date', today)}</span>
                        {"<span class='mock-tag'><i class='fas fa-robot'></i> 模拟数据</span>" if news.get('is_mock_data') else ""}
                    </div>
                    <p class="news-summary">{news.get('summary', '')}</p>
                    <a href="{news.get('url', '#')}" target="_blank" class="read-more">阅读原文 <i class="fas fa-external-link-alt"></i></a>
                </div>
            </article>
            """
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{industry_info['name']}行业新闻 - {self.website_config['name']}</title>
    <meta name="description" content="{industry_info['name']}行业最新动态和新闻汇总">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .hero {{ background: linear-gradient(135deg, {industry_info['color']}22 0%, {industry_info['color']}44 100%); }}
        .industry-title {{ color: {industry_info['color']}; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <h1><i class="fas fa-newspaper"></i> {self.website_config['name']}</h1>
                <p class="tagline">{self.website_config['description']}</p>
            </div>
            <nav>
                <ul>
                    <li><a href="index.html"><i class="fas fa-home"></i> 首页</a></li>
                    {"".join([f'<li><a href="{id}.html" {"class=active" if id == industry_id else ""}>{info["icon"]} {info["name"]}</a></li>' for id, info in self.industries.items()])}
                    <li><a href="about.html"><i class="fas fa-info-circle"></i> 关于</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="hero">
            <div class="hero-content">
                <h1 class="industry-title">{industry_info['icon']} {industry_info['name']}行业新闻</h1>
                <p class="industry-subtitle">{industry_info['name_en']}</p>
                <div class="industry-stats">
                    <span class="stat"><i class="fas fa-newspaper"></i> 今日新闻: {len(news_items)}条</span>
                    <span class="stat"><i class="far fa-calendar-alt"></i> 更新日期: {today}</span>
                    <span class="stat"><i class="fas fa-sync-alt"></i> 更新频率: 每日</span>
                </div>
                <p class="industry-description">
                    本页面汇总{industry_info['name']}行业的最新动态、技术进展和市场趋势，帮助您及时了解行业发展。
                </p>
            </div>
        </section>

        <section class="news-list">
            <div class="section-header">
                <h2><i class="fas fa-list-ul"></i> 今日新闻列表</h2>
                <div class="sort-options">
                    <span class="total-news">共 {len(news_items)} 条新闻</span>
                </div>
            </div>
            
            <div class="news-container">
                {news_list if news_list else '<p class="no-news">今日暂无新闻，请稍后再来查看。</p>'}
            </div>
        </section>

        <section class="back-to-home">
            <a href="index.html" class="back-button">
                <i class="fas fa-arrow-left"></i> 返回首页
            </a>
        </section>
    </main>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>{self.website_config['name']}</h3>
                    <p>{self.website_config['description']}</p>
                </div>
                <div class="footer-section">
                    <h3>行业导航</h3>
                    <ul>
                        {"".join([f'<li><a href="{id}.html">{info["icon"]} {info["name"]}</a></li>' for id, info in self.industries.items()])}
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>技术支持</h3>
                    <p>由 {self.website_config['author']} 提供</p>
                    <p>AI驱动的信息聚合</p>
                </div>
            </div>
            <div class="copyright">
                <p>© {datetime.now().year} {self.website_config['author']} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p class="tech-note">本页面内容由AI自动收集整理，信息仅供参考</p>
            </div>
        </div>
    </footer>

    <script src="js/script.js"></script>
</body>
</html>"""
        
        output_path = os.path.join(self.output_dir, f"{industry_id}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✓ {industry_info['name']}行业页面已生成: {output_path}")
    
    def _generate_about_html(self):
        """生成关于页面"""
        logger.info("生成关于页面...")
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>关于我们 - {self.website_config['name']}</title>
    <meta name="description" content="关于{self.website_config['name']}的介绍和说明">
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body>
    <header>
        <div class="container">
            <div class="logo">
                <h1><i class="fas fa-newspaper"></i> {self.website_config['name']}</h1>
                <p class="tagline">{self.website_config['description']}</p>
            </div>
            <nav>
                <ul>
                    <li><a href="index.html"><i class="fas fa-home"></i> 首页</a></li>
                    {"".join([f'<li><a href="{industry_id}.html">{industry_info["icon"]} {industry_info["name"]}</a></li>' for industry_id, industry_info in self.industries.items()])}
                    <li><a href="about.html" class="active"><i class="fas fa-info-circle"></i> 关于</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main class="container">
        <section class="about-hero">
            <h1><i class="fas fa-info-circle"></i> 关于我们</h1>
            <p class="about-subtitle">了解{self.website_config['name']}的使命和技术</p>
        </section>

        <section class="about-content">
            <div class="about-card">
                <h2><i class="fas fa-bullseye"></i> 项目使命</h2>
                <p>{self.website_config['name']}旨在通过AI技术聚合多行业信息，为用户提供及时、准确的行业动态。我们覆盖{len(self.industries)}个核心行业，每日更新最新新闻。</p>
            </div>

            <div class="about-card">
                <h2><i class="fas fa-cogs"></i> 技术架构</h2>
                <p>本网站采用全自动化技术栈：</p>
                <ul>
                    <li><strong>数据收集：</strong>AI自动搜索和抓取多行业新闻</li>
                    <li><strong>内容处理：</strong>自动摘要、分类和标签化</li>
                    <li><strong>网站生成：</strong>静态网站生成器自动构建页面</li>
                    <li><strong>部署更新：</strong>每日自动更新和部署</li>
                </ul>
            </div>

            <div class="about-card">
                <h2><i class="fas fa-industry"></i> 覆盖行业</h2>
                <div class="industries-list">
                    {"".join([f'<div class="about-industry" style="border-color: {info["color"]}"><span class="industry-icon">{info["icon"]}</span><div><h3>{info["name"]}</h3><p>{info["name_en"]}</p></div></div>' for industry_id, info in self.industries.items()])}
                </div>
            </div>

            <div class="about-card">
                <h2><i class="fas fa-history"></i> 更新机制</h2>
                <ul>
                    <li><strong>更新频率：</strong>每日自动更新</li>
                    <li><strong>收集时间：</strong>每天上午9:00</li>
                    <li><strong>生成时间：</strong>收集完成后立即生成</li>
                    <li><strong>部署时间：</strong>生成后自动部署</li>
                </ul>
            </div>

            <div class="about-card">
                <h2><i class="fas fa-shield-alt"></i> 免责声明</h2>
                <p>本网站内容由AI自动收集整理，信息仅供参考，不构成任何投资建议或决策依据。用户应自行核实信息的准确性和完整性。</p>
                <p>所有新闻版权归原作者所有，本网站仅提供信息聚合服务。</p>
            </div>
        </section>

        <section class="back-to-home">
            <a href="index.html" class="back-button">
                <i class="fas fa-arrow-left"></i> 返回首页
            </a>
        </section>
    </main>

    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>{self.website_config['name']}</h3>
                    <p>{self.website_config['description']}</p>
                </div>
                <div class="footer-section">
                    <h3>技术支持</h3>
                    <p>由 {self.website_config['author']} 提供</p>
                    <p>AI驱动的信息聚合平台</p>
                </div>
                <div class="footer-section">
                    <h3>联系方式</h3>
                    <p>如有问题或建议，请联系我们</p>
                </div>
            </div>
            <div class="copyright">
                <p>© {datetime.now().year} {self.website_config['author']} | 最后更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </footer>

    <script src="js/script.js"></script>
</body>
</html>"""
        
        output_path = os.path.join(self.output_dir, "about.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✓ 关于页面已生成: {output_path}")
    
    def _generate_news_preview(self, news_items, limit=3):
        """生成新闻预览"""
        preview = ""
        for i, news in enumerate(news_items[:limit]):
            title = news.get('title', '')
            if len(title) > 30:
                title = title[:30] + "..."
            preview += f'<div class="preview-item"><i class="fas fa-chevron-right"></i> {title}</div>'
        return preview
    
    def _generate_hot_news(self, data, limit=6):
        """生成热门新闻"""
        hot_news = ""
        all_news = []
        
        # 收集所有新闻
        for industry_id, industry_data in data['data'].items():
            for news in industry_data.get('news_items', []):
                news['industry'] = industry_id
                all_news.append(news)
        
        # 取前limit条
        for i, news in enumerate(all_news[:limit]):
            industry_info = self.industries.get(news['industry'], {})
            hot_news += f"""
            <div class="hot-news-card" style="border-top: 3px solid {industry_info.get('color', '#4CAF50')};">
                <div class="hot-news-header">
                    <span class="industry-tag" style="background: {industry_info.get('color', '#4CAF50')}22; color: {industry_info.get('color', '#4CAF50')};">
                        {industry_info.get('icon', '📰')} {industry_info.get('name', '行业')}
                    </span>
                    <span class="hot-index"><i class="fas fa-fire"></i> 热点</span>
                </div>
                <h3><a href="{news.get('url', '#')}" target="_blank">{news.get('title', '')}</a></h3>
                <p class="hot-summary">{news.get('summary', '')[:100]}...</p>
                <div class="hot-meta">
                    <span class="source"><i class="fas fa-newspaper"></i> {news.get('source', '未知来源')}</span>
                </div>
            </div>
            """
        
        return hot_news
    
    def _copy_static_resources(self):
        """复制静态资源（CSS、JS）"""
        static_dir = os.path.join(self.output_dir, "static")
        os.makedirs(os.path.join(self.output_dir, "css"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "js"), exist_ok=True)
        
        # 创建CSS文件
        css_content = self._generate_css()
        css_path = os.path.join(self.output_dir, "css", "style.css")
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # 创建JS文件
        js_content = self._generate_js()
        js_path = os.path.join(self.output_dir, "js", "script.js")
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        logger.info("✓ 静态资源已生成")
    
    def _generate_css(self):
        """生成CSS样式"""
        return """
/* 基础样式 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* 头部样式 */
header {
    background: white;
    box-shadow: 0 2px 15px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
}

.logo h1 {
    color: #2c3e50;
    font-size: 1.8rem;
    margin-bottom: 5px;
}

.logo .tagline {
    color: #7f8c8d;
    font-size: 0.9rem;
}

nav ul {
    display: flex;
    list-style: none;
    gap: 25px;
}

nav a {
    text-decoration: none;
    color: #555;
    font-weight: 500;
    padding: 8px 0;
    border-bottom: 2px solid transparent;
    transition: all 0.3s ease;
}

nav a:hover,
nav a.active {
    color: #3498db;
    border-bottom-color: #3498db;
}

/* Hero区域 */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 60px 0;
    margin: 30px 0;
    border-radius: 15px;
    text-align: center;
}

.hero h2 {
    font-size: 2.5rem;
    margin-bottom: 15px;
}

.date, .stats {
    font-size: 1.1rem;
    margin: 10px 0;
}

/* 行业网格 */
.industry-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 25px;
    margin: 30px 0;
}

.industry-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.industry-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
}

.industry-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
}

.industry-icon {
    font-size: 1.5rem;
    margin-right: 10px;
}

.news-count {
    background: #f1f8ff;
    color: #3498db;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
}

/* 新闻列表 */
.news-list {
    margin: 40px 0;
}

.news-item {
    background: white;
    padding: 25px;
    margin: 20px 0;
    border-radius: 10px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    display: flex;
    gap: 20px;
    transition: transform 0.2s ease;
}

.news-item:hover {
    transform: translateX(5px);
}

.news-number {
    background: #3498db;
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1.2rem;
    flex-shrink: 0;
}

.news-content h3 {
    margin-bottom: 10px;
}

.news-content h3 a {
    color: #2c3e50;
    text-decoration: none;
    transition: color 0.3s ease;
}

.news-content h3 a:hover {
    color: #3498db;
}

.news-meta {
    display: flex;
    gap: 20px;
    color: #7f8c8d;
    font-size: 0.9rem;
    margin: 10px 0;
}

.news-summary {
    color: #555;
    line-height: 1.7;
    margin: 15px 0;
}

.read-more {
    color: #3498db;
    text-decoration: none;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 5px;
}

/* 统计卡片 */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.stat-card {
    background: white;
    padding: 30px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

.stat-icon {
    font-size: 2.5rem;
    color: #3498db;
    margin-bottom: 15px;
}

.stat-number {
    font-size: 2.2rem;
    font-weight: bold;
    color: #2c3e50;
    margin: 10px 0;
}

.stat-label {
    color: #7f8c8d;
    font-size: 0.9rem;
}

/* 页脚 */
footer {
    background: #2c3e50;
    color: white;
    padding: 50px 0 20px;
    margin-top: 50px;
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 40px;
    margin-bottom: 40px;
}

.footer-section h3 {
    color: #ecf0f1;
    margin-bottom: 20px;
    font-size: 1.2rem;
}

.footer-section ul {
    list-style: none;
}

.footer-section ul li {
    margin: 10px 0;
}

.footer-section a {
    color: #bdc3c7;
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-section a:hover {
    color: #3498db;
}

.copyright {
    border-top: 1px solid #34495e;
    padding-top: 20px;
    text-align: center;
    color: #95a5a6;
    font-size: 0.9rem;
}

.tech-note {
    font-size: 0.8rem;
    color: #7f8c8d;
    margin-top: 10px;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .container {
        padding: 0 15px;
    }
    
    nav ul {
        flex-direction: column;
        gap: 10px;
    }
    
    .industry-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .news-item {
        flex-direction: column;
        gap: 15px;
    }
    
    .news-number {
        align-self: flex-start;
    }
}

@media (max-width: 480px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
    
    .hero h2 {
        font-size: 1.8rem;
    }
}
"""
    
    def _generate_js(self):
        """生成JavaScript代码"""
        return """
// 基础交互功能
document.addEventListener('DOMContentLoaded', function() {
    // 新闻卡片悬停效果
    const newsCards = document.querySelectorAll('.news-item, .industry-card, .hot-news-card');
    newsCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transition = 'all 0.3s ease';
        });
    });

    // 平滑滚动
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // 外部链接新窗口打开
    document.querySelectorAll('a[href^="http"]').forEach(link => {
        if (!link.href.includes(window.location.hostname)) {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        }
    });

    // 更新年份
    const yearElement = document.querySelector('.copyright');
    if (yearElement) {
        const currentYear = new Date().getFullYear();
        yearElement.innerHTML = yearElement.innerHTML.replace(/\\d{4}/, currentYear);
    }

    // 控制台欢迎信息
    console.log('%c🎉 欢迎访问行业信息聚合平台！', 'color: #3498db; font-size: 16px; font-weight: bold;');
    console.log('%c🤖 本网站由AI自动生成和维护', 'color: #2c3e50; font-size: 14px;');
});

// 主题切换（预留功能）
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    body.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // 显示切换提示
    const themeName = newTheme === 'light' ? '明亮模式' : '深色模式';
    showNotification(`已切换到${themeName}`);
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 5px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// 动画关键帧
const style = document.createElement('style');
style.textContent = `
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOut {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

[data-theme="dark"] {
    background-color: #1a1a1a;
    color: #ffffff;
}

[data-theme="dark"] .industry-card,
[data-theme="dark"] .news-item,
[data-theme="dark"] .stat-card {
    background-color: #2d2d2d;
    color: #ffffff;
}
`;
document.head.appendChild(style);
"""
    
    def _generate_seo_files(self):
        """生成SEO文件"""
        # 生成sitemap.xml
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://qingning-tech.github.io/industry-news/</loc>
        <lastmod>""" + datetime.now().strftime('%Y-%m-%d') + """</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://qingning-tech.github.io/industry-news/about.html</loc>
        <lastmod>""" + datetime.now().strftime('%Y-%m-%d') + """</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>"""
        
        for industry_id in self.industries.keys():
            sitemap += f"""
    <url>
        <loc>https://qingning-tech.github.io/industry-news/{industry_id}.html</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>"""
        
        sitemap += """
</urlset>"""
        
        sitemap_path = os.path.join(self.output_dir, "sitemap.xml")
        with open(sitemap_path, 'w', encoding='utf-8') as f:
            f.write(sitemap)
        
        # 生成robots.txt
        robots = """User-agent: *
Allow: /
Sitemap: https://qingning-tech.github.io/industry-news/sitemap.xml"""
        
        robots_path = os.path.join(self.output_dir, "robots.txt")
        with open(robots_path, 'w', encoding='utf-8') as f:
            f.write(robots)
        
        logger.info("✓ SEO文件已生成")

def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("静态网站生成器启动")
    logger.info("=" * 50)
    
    try:
        generator = WebsiteGenerator()
        success = generator.generate_website()
        
        if success:
            logger.info("\n🎉 网站生成成功！")
            logger.info("📁 生成的文件位于 docs/ 目录")
            logger.info("🌐 可以通过以下方式访问：")
            logger.info("   1. 本地打开 docs/index.html")
            logger.info("   2. 部署到 GitHub Pages")
            logger.info("   3. 部署到 Vercel/Netlify")
        else:
            logger.error("❌ 网站生成失败")
            return 1
            
    except Exception as e:
        logger.error(f"网站生成失败: {e}", exc_info=True)
        return 1
    
    logger.info("=" * 50)
    return 0

if __name__ == "__main__":
    sys.exit(main())