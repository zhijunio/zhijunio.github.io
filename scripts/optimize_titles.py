#!/usr/bin/env python3
"""批量优化博客文章标题（SEO 搜索意图驱动）。

从 /tmp/blog_titles_review_final.json 读取标题映射，
批量替换 content/ 下所有 .md 文件的 frontmatter title 字段。
"""

import json
import re
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content"
TITLES_JSON = Path("/tmp/blog_titles_review_final.json")


def update_title(file_path: Path, new_title: str) -> bool:
    """替换 frontmatter 中的 title 字段。返回是否成功替换。"""
    content = file_path.read_text(encoding="utf-8")
    
    # 匹配 frontmatter 中的 title
    pattern = r'^(title:\s*)["\']?.+?["\']?\s*$'
    replacement = f'title: "{new_title}"'
    
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    if new_content != content:
        file_path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    # 读取标题映射
    with open(TITLES_JSON, "r", encoding="utf-8") as f:
        posts = json.load(f)
    
    # 创建文件路径到建议标题的映射
    title_map = {}
    for post in posts:
        if post.get("suggested_title"):
            title_map[post["file"]] = post["suggested_title"]
    
    print(f"加载了 {len(title_map)} 个标题映射")
    
    # 遍历所有 .md 文件并更新标题
    updated = 0
    skipped = 0
    not_found = 0
    
    for md_file in sorted(CONTENT_DIR.rglob("*.md")):
        if md_file.name.startswith("_"):
            continue
        
        rel_path = str(md_file.relative_to(CONTENT_DIR))
        
        if rel_path in title_map:
            new_title = title_map[rel_path]
            if update_title(md_file, new_title):
                print(f"✅ {rel_path}")
                print(f"   → {new_title}")
                updated += 1
            else:
                print(f"⚠️  {rel_path}（title 未变化或格式不匹配）")
                skipped += 1
        else:
            print(f"❌ {rel_path}（无建议标题）")
            not_found += 1
    
    print(f"\n=== 统计 ===")
    print(f"✅ 更新: {updated} 篇")
    print(f"⚠️  跳过: {skipped} 篇")
    print(f"❌ 未找到: {not_found} 篇")


if __name__ == "__main__":
    main()
