@echo off
chcp 65001 > nul
echo ========================================
echo AI新闻日报 → 网站推送
echo 时间: %date% %time%
echo ========================================

cd /d "%~dp0"

echo 步骤1: 格式化新闻数据...
echo. > .temp_news_data.txt 2>nul

echo 步骤2: 运行主程序生成网站...
python main.py

if errorlevel 1 (
    echo [错误] 网站生成失败
    exit /b 1
) else (
    echo [成功] 网站更新完成！
)

echo 文件位置: docs/index.html
echo 可以打开该文件查看最新AI新闻
echo ========================================
echo 任务结束
echo 时间: %date% %time%
echo ========================================
