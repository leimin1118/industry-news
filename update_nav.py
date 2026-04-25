#!/usr/bin/env python3
"""更新所有HTML页面的导航栏，添加世界地图链接"""
import os

docs_dir = os.path.join(os.path.dirname(__file__), 'docs')
html_files = ['index.html', 'ai.html', 'electricity.html', 'ecommerce.html', 'about.html']

for filename in html_files:
    filepath = os.path.join(docs_dir, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP {filename} (not found)")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    changed = False
    
    # 导航栏：在 about 链接前插入 worldmap
    if 'worldmap.html' not in content:
        # 主导航
        old = '<li><a href="about.html"><i class="fas fa-info-circle"></i> 关于</a></li>'
        new = '<li><a href="worldmap.html">🌍 世界地图</a></li>\n                    <li><a href="about.html"><i class="fas fa-info-circle"></i> 关于</a></li>'
        if old in content:
            content = content.replace(old, new)
            changed = True
        
        # 页脚导航
        old_footer = '<li><a href="ai.html">🤖 人工智能</a></li>'
        new_footer = '<li><a href="ai.html">🤖 人工智能</a></li><li><a href="worldmap.html">🌍 世界地图</a></li>'
        if old_footer in content:
            content = content.replace(old_footer, new_footer)
            changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {filename} - 已添加世界地图链接")
    else:
        # 检查是否已经存在
        if 'worldmap.html' in content:
            print(f"  ✓ {filename} - 已有世界地图链接")
        else:
            print(f"  ❌ {filename} - 未找到匹配的导航栏")

print("\n✅ 导航栏更新完成！")
