@echo off
chcp 65001 > nul
echo ========================================
echo  🗺️ 行业网站全量更新
echo  青青柠檬科技 🦐
echo  时间: %date% %time%
echo ========================================

cd /d "%~dp0"

echo.
echo [步骤 1/3] 运行主程序生成网站...
python main.py
if errorlevel 1 (
    echo [错误] 网站生成失败
    exit /b 1
)

echo.
echo [步骤 2/3] 更新世界地图首页数据...
python update_worldmap_data.py
if errorlevel 1 (
    echo [错误] 世界地图更新失败
    exit /b 1
)

echo.
echo [步骤 3/3] 验证网站文件...
if exist docs\index.html (
    for %%f in (docs\*.html) do (
        echo   ✓ %%f
    )
    echo.
    echo ✅ 网站全量更新完成！
    echo   打开 docs\index.html 查看世界地图版首页
) else (
    echo [错误] 网站文件未生成
    exit /b 1
)

echo ========================================
echo 完成时间: %date% %time%
echo ========================================
