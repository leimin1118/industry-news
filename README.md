# 🏭 行业信息聚合网站

AI驱动的多行业信息聚合平台，自动收集、整理和展示AI、电力、电商行业的最新动态。

## ✨ 功能特性

- **🤖 AI自动收集**: 自动搜索和收集三个行业的新闻
- **🌐 静态网站**: 生成高性能的静态HTML网站
- **📱 响应式设计**: 适配手机、平板和电脑
- **🎨 美观界面**: 现代化的卡片式设计
- **🚀 快速部署**: 支持GitHub Pages、Vercel等平台
- **🔄 自动更新**: 支持定时自动更新内容

## 🏗️ 项目结构

```
industry-news-website/
├── config.json              # 配置文件
├── main.py                 # 主程序
├── news_collector.py       # 新闻收集器
├── website_generator.py    # 网站生成器
├── data/                   # 新闻数据目录
├── docs/                   # 生成的网站文件
├── README.md              # 说明文档
└── requirements.txt       # Python依赖
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装tavily CLI（可选，用于真实新闻）
curl -fsSL https://cli.tavily.com/install.sh | bash
tvly login
```

### 2. 运行系统

```bash
# 完整运行（收集新闻 + 生成网站）
python main.py

# 只收集新闻
python news_collector.py

# 只生成网站  
python website_generator.py

# 测试系统
python main.py test
```

### 3. 查看结果

生成的网站文件在 `docs/` 目录中：
- `docs/index.html` - 首页
- `docs/ai.html` - AI行业新闻
- `docs/electricity.html` - 电力行业新闻  
- `docs/ecommerce.html` - 电商行业新闻
- `docs/about.html` - 关于页面

## ⚙️ 配置说明

编辑 `config.json` 文件自定义：

### 行业配置
```json
{
  "ai": {
    "name": "人工智能",
    "keywords": ["AI 新闻", "人工智能", "机器学习"],
    "sources": ["机器之心", "36氪AI"],
    "color": "#4CAF50",
    "icon": "🤖"
  }
}
```

### 网站配置
```json
{
  "website": {
    "name": "行业信息聚合平台",
    "description": "AI驱动的多行业信息聚合",
    "author": "青青柠檬科技有限公司",
    "base_url": "https://your-site.com/"
  }
}
```

## 🌐 部署指南

### GitHub Pages（推荐）

1. 在GitHub创建新仓库
2. 将 `docs/` 目录内容推送到仓库
3. 进入仓库 Settings → Pages
4. 选择 `main` 分支，`/docs` 目录
5. 访问: `https://<用户名>.github.io/<仓库名>/`

### Vercel（最快速）

1. 访问 https://vercel.com
2. 导入GitHub仓库
3. 框架选择 `Other`
4. 输出目录设置为 `docs`
5. 自动部署，获得 `vercel.app` 域名

### Netlify

1. 访问 https://netlify.com
2. 拖放 `docs/` 文件夹
3. 获得 `netlify.app` 域名

## 🔄 自动更新

### Windows任务计划
```batch
# 创建 daily_update.bat
@echo off
cd /d "C:\path\to\industry-news-website"
python main.py
```

### Linux/Mac Cron
```bash
# 每天9点运行
0 9 * * * cd /path/to/industry-news-website && python main.py
```

### GitHub Actions
创建 `.github/workflows/update.yml`:
```yaml
name: Daily Update
on:
  schedule:
    - cron: '0 9 * * *'  # 每天9点
  workflow_dispatch:      # 手动触发

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - run: python main.py
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
```

## 📊 数据源

### 真实新闻（需tavily CLI）
- **AI行业**: 机器之心、36氪AI、TechCrunch AI等
- **电力行业**: 北极星电力网、中国电力新闻网等  
- **电商行业**: 亿邦动力、派代网、天下网商等

### 模拟数据（无tavily时）
当tavily不可用时，系统自动生成高质量的模拟数据，保证网站正常显示。

## 🛠️ 自定义开发

### 添加新行业
1. 在 `config.json` 的 `industries` 中添加新行业
2. 设置行业名称、关键词、颜色、图标
3. 重新运行系统即可

### 修改网站样式
编辑 `website_generator.py` 中的 `_generate_css()` 方法，或直接修改生成的 `docs/css/style.css` 文件。

### 扩展功能
- **搜索功能**: 添加客户端搜索（使用lunr.js或FlexSearch）
- **评论系统**: 集成Giscus（GitHub Discussions）
- **数据分析**: 添加图表展示行业趋势
- **RSS订阅**: 为每个行业生成RSS feed

## 📈 效果预览

### 首页
- 行业分类卡片
- 今日热点新闻
- 数据统计面板
- 响应式导航

### 行业页面
- 行业专属配色
- 新闻列表（带摘要）
- 来源和日期信息
- 阅读原文链接

### 关于页面
- 项目介绍
- 技术架构说明
- 行业覆盖清单
- 免责声明

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [tavily](https://tavily.com/) - AI搜索API
- [Font Awesome](https://fontawesome.com/) - 图标库
- [GitHub Pages](https://pages.github.com/) - 免费托管
- [Vercel](https://vercel.com/) - 极速部署

## 📞 联系我们

如有问题或建议，请通过GitHub Issues联系我们。

---

**由 🦐 奶虾（AI助手）为 青青柠檬科技有限公司 开发**  
**最后更新: 2026-04-21**