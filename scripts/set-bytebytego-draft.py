#!/usr/bin/env python3
"""
将所有 ByteByteGo 翻译文章的 draft 设置为 true
"""

import os
import re
from pathlib import Path

CONTENT_DIR = Path(__file__).parent.parent / "content" / "translation"

def set_draft_to_true(file_path: Path) -> bool:
    """将文件的 draft 设置为 true，如果已经是 true 则跳过"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经有 draft: true
    if re.search(r'^draft:\s*true\s*$', content, re.MULTILINE):
        return False  # 已经是 true，无需修改

    # 替换 draft: false 为 draft: true
    new_content = re.sub(
        r'^draft:\s*false\s*$',
        'draft: true',
        content,
        flags=re.MULTILINE
    )

    # 如果没有 draft 字段，在 frontmatter 中添加
    if new_content == content:
        # 在 description 之后或 favicon 之后添加 draft: true
        if 'description:' in content:
            new_content = re.sub(
                r'^(description:.*$)',
                r'\1\ndraft: true',
                content,
                flags=re.MULTILINE
            )
        elif 'favicon:' in content:
            new_content = re.sub(
                r'^(favicon:.*$)',
                r'\1\ndraft: true',
                content,
                flags=re.MULTILINE
            )

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True  # 已修改

    return False

def main():
    modified_count = 0
    skipped_count = 0

    for md_file in CONTENT_DIR.glob("**/*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否是 ByteByteGo 相关的文章
        if 'ByteByteGo' in content or 'bytebytego' in content.lower():
            if set_draft_to_true(md_file):
                print(f"✓ 修改：{md_file.name}")
                modified_count += 1
            else:
                print(f"- 跳过（已是 draft: true）：{md_file.name}")
                skipped_count += 1

    print(f"\n完成！")
    print(f"  修改：{modified_count} 个文件")
    print(f"  跳过：{skipped_count} 个文件")

if __name__ == "__main__":
    main()
