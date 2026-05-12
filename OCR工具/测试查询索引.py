# -*- coding: utf-8 -*-
"""
============================================================
测试索引查询脚本
============================================================
作用:测试索引建得好不好用——输入关键词,看看能在哪几本图集、哪些页找到
输入:施工图设计中南标图集/references/*.md
输出:命令行直接打印匹配到的页码和摘要

使用方法(索引生成后):
  python OCR工具/测试查询索引.py 保温
  python OCR工具/测试查询索引.py 天沟
  python OCR工具/测试查询索引.py L3
============================================================
"""
import os
import sys
import re

REF_DIR = "施工图设计中南标图集/references"


def search_in_file(md_path, keyword):
    """在一个索引 md 文件中搜索关键词,返回命中的页码和上下文片段"""
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 按"### 第 X 页"切分
    pages = re.split(r'\n### 第 (\d+) 页\n', content)
    # 切完之后结构:[开头, 页码1, 页1内容, 页码2, 页2内容, ...]

    matches = []
    # 从索引 1 开始,步长 2
    i = 1
    while i < len(pages):
        page_num = pages[i]
        page_content = pages[i + 1] if (i + 1) < len(pages) else ""
        if keyword in page_content:
            # 提取包含关键词的那一行作为摘要
            snippet_lines = []
            for line in page_content.split("\n"):
                if keyword in line:
                    snippet_lines.append(line.strip())
            matches.append({
                "page": int(page_num),
                "snippets": snippet_lines[:3],  # 最多取 3 行
            })
        i += 2

    return matches


def main():
    if len(sys.argv) < 2:
        print("用法:python OCR工具/测试查询索引.py <关键词>")
        print("示例:")
        print("  python OCR工具/测试查询索引.py 保温")
        print("  python OCR工具/测试查询索引.py 天沟")
        print("  python OCR工具/测试查询索引.py L3")
        return

    keyword = sys.argv[1]

    if not os.path.isdir(REF_DIR):
        print(f"❌ 索引目录不存在:{REF_DIR}")
        print("请先运行索引生成脚本:python OCR工具/生成索引.py")
        return

    md_files = [f for f in os.listdir(REF_DIR) if f.endswith(".md") and f != "README.md"]
    if not md_files:
        print("❌ 索引目录里没有索引文件。请先生成索引")
        return

    print(f"🔍 关键词:{keyword}\n")
    total_hits = 0

    for md in sorted(md_files):
        path = os.path.join(REF_DIR, md)
        matches = search_in_file(path, keyword)
        if not matches:
            continue

        # 从文件名提取图集名
        book_name = md.replace(".md", "")
        print(f"📖 《{book_name}》—— 命中 {len(matches)} 页:")
        for m in matches[:10]:  # 每本图集最多显示 10 页
            print(f"   第 {m['page']} 页:")
            for s in m['snippets']:
                # 把过长的行截断
                if len(s) > 150:
                    s = s[:150] + "..."
                print(f"      • {s}")
        if len(matches) > 10:
            print(f"   ...还有 {len(matches) - 10} 页命中(省略)")
        print()
        total_hits += len(matches)

    if total_hits == 0:
        print("😕 所有图集都没匹配到这个关键词")
        print("提示:试试别的关键词,比如换一个说法、或只输入其中 1-2 个字")
    else:
        print(f"✅ 共命中 {total_hits} 页")


if __name__ == "__main__":
    main()
