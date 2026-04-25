@echo off
chcp 65001 > nul
echo ========================================
echo 🏭 行业信息聚合网站系统
echo ========================================

echo 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    pause
    exit /b 1
)

echo.
echo 安装依赖（如果需要）...
pip install -r requirements.txt

echo.
echo 开始运行系统...
python main.py

if errorlevel 1 (
    echo.
    echo ❌ 系统运行失败
    pause
    exit /b 1
)

echo.
echo ✅ 系统运行完成！
echo.
echo 📁 生成的网站位于 docs/ 目录
echo 🌐 打开 docs/index.html 查看网站
echo.
echo 🚀 部署建议：
echo    1. 将 docs/ 上传到 GitHub Pages
echo    2. 或部署到 Vercel/Netlify
echo.
echo ========================================
pause