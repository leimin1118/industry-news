#!/usr/bin/env python3
"""
更新世界地图版首页（docs/index.html）的新闻数据
从 data/ 目录读取最新 JSON，替换 HTML 中的硬编码 countryNews
"""

import json
import os
import re
import glob
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = "data"
OUTPUT_FILE = "docs/index.html"

# 国家/地区关键词映射 —— 用于将新闻智能归类到国家
COUNTRY_KEYWORDS = {
    '美国': [
        'OpenAI', 'Google', 'AWS', 'Anthropic', 'xAI', 'DOJ', 'Microsoft',
        'NVIDIA', 'Apple', 'Meta', 'Amazon', 'Tesla', 'Intel', 'AMD', 'IBM',
        'Oracle', 'Uber', 'Airbnb', 'Twitter', 'Snapchat', 'Pinterest',
        'Netflix', 'Zoom', 'Slack', 'Salesforce', 'Palantir', 'Qualcomm',
        'Broadcom', 'Waymo', 'SpaceX', 'Neuralink', 'Stripe', 'Coinbase',
        'Robinhood', 'PayPal', 'Block', 'Square', 'Lyft', 'DoorDash',
        'Instacart', 'Airbnb', 'Reddit', 'Discord', 'Twitch', 'Dropbox',
        'Box', 'DocuSign', 'Workday', 'ServiceNow', 'Snowflake', 'Databricks',
        'Cloudflare', 'CrowdStrike', 'Palo Alto', 'Fortinet', 'Cisco',
        'Dell', 'HP', '惠普', '戴尔',
    ],
    '中国': [
        '中国', '腾讯', '百度', '阿里', '阿里巴巴', '字节跳动', '华为',
        '小米', '京东', '美团', '滴滴', '商汤', '科大讯飞', '旷视',
        '依图', '云从', '智谱', '百川', '月之暗面', '零一万物',
        'MiniMax', '阶跃星辰', '深度求索', 'DeepSeek', '通义', '文心',
        '混元', '盘古', '天工', '360', '小红书', '哔哩哔哩', 'B站',
        '拼多多', 'PDD', '网易', '搜狐', '新浪', '微博', '快手',
        '比亚迪', '蔚来', '小鹏', '理想', '大疆', '海康', '中兴',
    ],
    '加拿大': ['加拿大', 'Cohere', 'Element AI', 'Mila', 'Vector Institute', 'Shopify', 'BlackBerry', 'Waterloo', '多伦多大学', 'UBC', '麦吉尔'],
    '英国': [
        '英国', 'DeepMind', 'UCL', 'Cambridge', '剑桥', 'Oxford', '牛津',
        'Imperial', '帝国理工', 'Graphcore', 'Wayve', 'BenevolentAI',
        'ARM', 'Revolut', 'Monzo', 'TransferWise', 'Wise', 'Deliveroo',
        'Darktrace', 'DeepMind',
    ],
    '日本': ['日本', '软银', 'Sony', '索尼', 'Toyota', '丰田', 'NEC', '富士通', 'Preferred Networks', 'RIKEN', '东京大学', '京都大学', '松下', '本田', '日产'],
    '韩国': ['韩国', '三星', 'Samsung', 'LG', 'SK', 'Naver', 'Kakao', '首尔大学', 'KAIST', '现代', '起亚'],
    '德国': ['德国', 'SAP', 'Siemens', '西门子', 'Bosch', '博世', 'Volkswagen', '大众', 'BMW', '宝马', 'Mercedes', '奔驰', 'Fraunhofer', '亥姆霍兹', '马克斯·普朗克', '安联', 'Allianz'],
    '法国': ['法国', 'Mistral AI', 'Hugging Face', 'LightOn', 'Naver Labs Europe', 'INRIA', 'CNRS', '空客', 'Airbus', 'LVMH', '欧莱雅', '赛诺菲'],
    '印度': ['印度', 'Infosys', 'TCS', 'Reliance', 'Wipro', 'HCL', '印度理工', 'IIT', 'Flipkart', 'Zomato', 'Paytm', 'Byju'],
    '新加坡': ['新加坡', '南洋理工', '新加坡国立', 'NUS', 'NTU', 'Sea', 'Grab', 'Shopee', 'Lazada', '淡马锡'],
    '澳大利亚': ['澳大利亚', 'Atlassian', 'Canva', '悉尼大学', '澳洲国立', '墨尔本大学', '联邦银行'],
    '以色列': ['以色列', 'Mobileye', 'Waze', 'Wix', 'Fiverr', 'AI21 Labs', '特拉维夫大学', '希伯来大学', '魏茨曼', 'Check Point'],
    '俄罗斯': ['俄罗斯', 'Yandex', 'Sber', 'Sberbank', 'Moscow State', '莫斯科大学', '卡巴斯基', 'Kaspersky'],
    '芬兰': ['芬兰', 'Nokia', '诺基亚', '赫尔辛基大学', '阿尔托大学', 'Supercell', 'Rovio'],
    '瑞典': ['瑞典', 'Spotify', 'Klarna', '爱立信', 'Ericsson', '阿斯利康', 'AstraZeneca', '沃尔沃', 'Volvo', 'SKF'],
    '瑞士': ['瑞士', '苏黎世联邦理工', 'ETH', '洛桑联邦理工', 'EPFL', '诺华', 'Novartis', '罗氏', 'Roche', 'ABB', '雀巢', 'Nestle', '瑞银', 'UBS'],
    '荷兰': ['荷兰', 'ASML', '飞利浦', 'Philips', 'ING', '阿姆斯特丹大学', '代尔夫特理工', 'Shell', '联合利华', 'Unilever'],
    '阿联酋': ['阿联酋', '迪拜', 'Dubai', 'Abu Dhabi', '阿布扎比', 'G42', '穆罕默德·本·扎耶德'],
    '沙特阿拉伯': ['沙特', '沙特阿拉伯', 'NEOM', 'KAUST', '沙特国王大学', 'Aramco', '阿美'],
}

# 所有支持的国家（顺序保持稳定）
ALL_COUNTRIES = [
    '美国', '中国', '加拿大', '英国', '日本', '韩国', '德国', '法国',
    '印度', '新加坡', '澳大利亚', '以色列', '俄罗斯', '芬兰', '瑞典',
    '瑞士', '荷兰', '阿联酋', '沙特阿拉伯',
]


def load_latest_data():
    """从 data/ 目录加载最新的汇总数据"""
    summary_files = sorted(
        glob.glob(os.path.join(DATA_DIR, "summary_*.json")),
        reverse=True
    )
    if not summary_files:
        logger.error("没有找到数据文件")
        return None

    latest = summary_files[0]
    logger.info(f"加载数据: {os.path.basename(latest)}")
    with open(latest, 'r', encoding='utf-8') as f:
        return json.load(f)


def classify_news_to_countries(news_items):
    """将新闻归类到国家"""
    result = {}

    for item in news_items:
        title = item.get('title', '')
        summary = item.get('summary', '')
        source = item.get('source', '')
        full_text = (title + ' ' + summary + ' ' + source).lower()

        matched = []
        for country, keywords in COUNTRY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in full_text:
                    matched.append(country)
                    break

        if matched:
            primary = matched[0]
        else:
            primary = '美国'  # 默认归入美国

        if primary not in result:
            result[primary] = []
        result[primary].append({
            'title': title,
            'summary': summary,
            'source': source,
        })

    return result


def escape_js_string(s):
    """转义字符串中的单引号和换行符，用于嵌入JS"""
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    s = s.replace('\n', ' ')
    s = s.replace('\r', ' ')
    return s


def generate_country_news_js(classified):
    """生成 countryNews JS 对象字符串"""
    lines = []
    for country in ALL_COUNTRIES:
        items = classified.get(country, [])
        if not items:
            items = [{
                'title': f'{country}AI产业持续发展',
                'summary': f'{country}在人工智能领域持续投入和创新。',
                'source': '综合报道'
            }]
        # 每个国家最多5条
        items = items[:5]

        entries = []
        for n in items:
            title = escape_js_string(n['title'])
            summary = escape_js_string(n['summary'])
            source = escape_js_string(n['source'])
            entries.append(f"        {{ title: '{title}', summary: '{summary}', source: '{source}' }}")

        items_str = ',\n'.join(entries)
        lines.append(f"    '{country}': [\n{items_str}\n    ]")

    return ',\n'.join(lines)


def get_js_count(country_news_js_snippet):
    """估算生成countryNews用了多少条新闻"""
    return country_news_js_snippet.count("title:")


def update_html(data):
    """替换 docs/index.html 中的硬编码 countryNews"""
    if not os.path.exists(OUTPUT_FILE):
        logger.error(f"文件不存在: {OUTPUT_FILE}")
        return False

    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 收集所有新闻
    all_news = []
    for ind_data in data.get('data', {}).values():
        for item in ind_data.get('news_items', []):
            all_news.append(item)

    classified = classify_news_to_countries(all_news)
    country_news_js = generate_country_news_js(classified)

    # 更新日期
    today_str = datetime.now().strftime('%Y年%m月%d日')
    update_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    total_news = data.get('total_news', len(all_news))

    # 替换标题中的日期
    content = re.sub(
        r'<title>行业信息聚合平台\s*-\s*\S+?</title>',
        f'<title>行业信息聚合平台 - {today_str}</title>',
        content
    )

    # 替换描述中的日期
    content = re.sub(
        r'世界地图 \+ AI行业新闻聚合',
        f'世界地图 + AI行业新闻聚合 | 更新：{update_date}',
        content
    )

    # 替换 hero 中的日期文本
    content = re.sub(
        r'查看各国基本信息 \+ 最新AI行业新闻[\s\S]*?</p>',
        f'查看各国基本信息 + 最新AI行业新闻 ｜ 更新日期：{today_str}</p>',
        content
    )

    # 替换 countryNews 数据块
    # 模式：查找 const countryNews = { ... }; 并替换
    pattern = r'const countryNews\s*=\s*\{[\s\S]*?\};'
    replacement = f'const countryNews = {{\n{country_news_js}\n}};'

    if not re.search(pattern, content):
        logger.error("未找到 countryNews 定义！HTML结构可能已变化。")
        # 尝试查找简化模式
        pattern2 = r'const countryNews\s*='
        if re.search(pattern2, content):
            logger.info("找到 countryNews 但未能匹配完整模式，尝试备选方案...")
            # 尝试从 const countryNews = 到下一个 ; 或用 regex 更精确
            content = re.sub(
                r'(const countryNews\s*=\s*\{).*?(\};)',
                lambda m: m.group(1) + '\n' + country_news_js + '\n' + m.group(2),
                content,
                flags=re.DOTALL
            )
        else:
            logger.error("完全找不到 countryNews，无法更新")
            return False
    else:
        content = re.sub(pattern, replacement, content)

    # 替换 defaultNews 中的摘要文本（显示新闻总数）
    def replace_default_summary(match):
        return match.group(1) + f'{total_news}条行业新闻今日收录' + match.group(2)
    content = re.sub(
        r"(title:\s*'全球AI产业持续高速增长',\s*summary:\s*').*?(')",
        replace_default_summary,
        content
    )

    # 写回文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)

    used_items = sum(len(items) for items in classified.values())
    logger.info(f"✅ 已更新 {OUTPUT_FILE}")
    logger.info(f"   数据来源: {data.get('date', 'unknown')}")
    logger.info(f"   新闻总数: {total_news}")
    logger.info(f"   归类到国家的新闻: {used_items}")
    return True


def main():
    data = load_latest_data()
    if not data:
        logger.error("无法加载数据，退出")
        return 1

    success = update_html(data)
    if success:
        logger.info("🎉 世界地图首页更新完成！")
        return 0
    else:
        logger.error("❌ 更新失败")
        return 1


if __name__ == "__main__":
    exit(main())
