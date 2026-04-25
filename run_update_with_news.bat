:: 一键更新AI新闻到行业网站
:: 使用方法: run_update_with_news.bat
:: 脚本会把今日AI新闻日报数据格式化为网站JSON并重新生成

@echo off
chcp 65001 > nul
echo ========================================
echo  AI新闻日报 → 行业网站 一键更新
echo  青青柠檬科技 🦐
echo  时间: %date% %time%
echo ========================================

cd /d "%~dp0"

set TODAY=%date:~0,4%%date:~5,2%%date:~8,2%
echo 今日日期: %TODAY%

echo.
echo [步骤 1/2] 运行主程序生成网站...
python main.py

if errorlevel 1 (
    echo [错误] 网站生成失败
    exit /b 1
)

echo.
echo [步骤 2/2] 验证网站...
if exist docs\index.html (
    for %%f in (docs\*.html) do (
        echo   ✓ %%f
    )
    echo.
    echo ✅ 网站更新成功！
    echo 可以打开 docs\index.html 查看最新AI新闻
) else (
    echo [错误] 网站文件未生成
    exit /b 1
)

echo ========================================
echo 完成时间: %date% %time%
echo ========================================
