# -*- coding: utf-8 -*-
"""
============================================================
生成 skill 索引脚本
============================================================
作用:把 OCR 识别结果(原始 json)整理成 skill 能查的 Markdown 索引
输入:OCR工具/识别结果/*.json
输出:施工图设计中南标图集/references/*.md

使用方法:等 OCR 全部跑完后,执行
  python OCR工具/生成索引.py
============================================================
"""
import os
import json
import re

# OCR 识别结果目录
INPUT_DIR = "OCR工具/识别结果"
# skill 的索引输出目录
OUTPUT_DIR = "施工图设计中南标图集/references"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 图集的人话介绍,放在每个索引文件开头
PDF_INTRO = {
    "中南15ZJ001-建筑构造用料做法": {
        "name": "中南 15ZJ001 建筑构造用料做法",
        "description": "中南标全套图集的【总做法表】。楼地面、内墙、外墙、顶棚、屋面、散水、变形缝等所有【做法编号】的定义都在这里。你在施工图上标的 L3、N2、W1 这类编号,都要到这本查原始定义。",
    },
    "中南15ZJ201-平屋面": {
        "name": "中南 15ZJ201 平屋面",
        "description": "平屋面的详细节点图集:找坡、防水、保温、排水、上人/不上人、分仓缝、女儿墙、排水口等节点的大样详图。",
    },
    "中南15ZJ203-种植屋面": {
        "name": "中南 15ZJ203 种植屋面",
        "description": "种植屋面(屋顶花园)的构造:排水板、蓄水板、过滤层、种植土等专用构造,比普通屋面多了【植物相关】的几层。",
    },
    "中南15ZJ211-坡屋面": {
        "name": "中南 15ZJ211 坡屋面",
        "description": "坡屋面的构造(瓦面、金属板屋面等),包括屋脊、檐口、天沟、突出屋面物件的节点。",
    },
    "中南15ZJ602-建筑节能门窗": {
        "name": "中南 15ZJ602 建筑节能门窗",
        "description": "节能门窗的选型、型号、安装节点、传热系数 K 值数据。做门窗表和门窗大样时主要查这本。",
    },
    "中南15ZJ611-拉闸门和卷帘门建筑构造": {
        "name": "中南 15ZJ611 拉闸门和卷帘门建筑构造",
        "description": "商业门面常用的拉闸门、卷帘门构造详图。",
    },
}


def filter_texts(texts, min_conf=0.5):
    """过滤掉识别置信度过低的文字(可能是噪声)"""
    return [t for t in texts if t.get("confidence", 1.0) >= min_conf]


def categorize_texts(texts):
    """把一页识别出的文字简单分类:
    - 可能的章节/标题(通常较短且位置靠上,但这里我们只能按长度大致判断)
    - 做法编号(L1/L2/W1/屋1等模式)
    - 正文
    """
    codes = []  # 做法编号
    titles = []  # 可能的标题
    content = []  # 正文

    # 做法编号的常见正则:字母/汉字 + 数字,如 L3、WS2、屋1、屋面1、门1
    code_pattern = re.compile(r'^(L|N|W|P|T|WP|WS|屋|屋面|平屋|坡屋|门|窗|节|大样|详图)\s?-?\s?\d+[a-zA-Z]?$')

    for item in texts:
        txt = item["text"].strip()
        if not txt:
            continue
        if code_pattern.match(txt):
            codes.append(txt)
        elif len(txt) < 20 and ("做法" in txt or "详图" in txt or "节点" in txt
                                 or "大样" in txt or "构造" in txt or "目录" in txt
                                 or "屋面" in txt or "门窗" in txt):
            titles.append(txt)
        else:
            content.append(txt)
    return codes, titles, content


def build_page_section(page_data):
    """为一页生成 Markdown 内容"""
    page_num = page_data["page"]
    texts = filter_texts(page_data["texts"])

    if not texts:
        return f"### 第 {page_num} 页\n\n(本页未识别到有效文字,可能是纯图纸或空白页)\n\n"

    codes, titles, content = categorize_texts(texts)

    lines = [f"### 第 {page_num} 页\n"]

    if titles:
        lines.append("**关键词/标题**:" + " · ".join(titles[:10]) + "\n")

    if codes:
        lines.append("**做法编号 / 节点号**:" + "、".join(codes) + "\n")

    if content:
        # 把正文按识别顺序拼成段,去重
        seen = set()
        content_clean = []
        for c in content:
            if c not in seen:
                seen.add(c)
                content_clean.append(c)
        # 控制长度,太长的页面截断
        content_text = " | ".join(content_clean[:40])
        lines.append(f"**正文摘要**:{content_text}\n")

    return "\n".join(lines) + "\n"


def process_one(json_path):
    """处理一个 OCR 结果 json,生成对应的 Markdown 索引"""
    filename = os.path.basename(json_path).replace(".json", "")
    intro = PDF_INTRO.get(filename, {
        "name": filename,
        "description": "图集索引(自动生成)",
    })

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = data["total_pages"]
    pages = data["pages"]

    # 生成 Markdown
    out_lines = [
        f"# {intro['name']} 索引\n",
        f"> {intro['description']}\n",
        f"\n**总页数**:{total} 页\n",
        "\n**使用说明**:AI 查询时按关键词在本文件搜索(做法编号、材料名、节点名等),找到对应页码后告诉用户。\n",
        "\n---\n",
        "\n## 全图集关键词速查\n",
    ]

    # 先全局收集一次所有做法编号,放在开头
    all_codes = {}
    for page_data in pages:
        texts = filter_texts(page_data["texts"])
        codes, _, _ = categorize_texts(texts)
        for c in codes:
            all_codes.setdefault(c, []).append(page_data["page"])

    if all_codes:
        out_lines.append("\n### 做法编号/节点号一览(自动提取,请以图集原文为准)\n")
        # 按编号排序
        for code in sorted(all_codes.keys()):
            pages_str = "、".join(str(p) for p in sorted(set(all_codes[code])))
            out_lines.append(f"- **{code}**:见第 {pages_str} 页")
        out_lines.append("")

    out_lines.append("\n---\n")
    out_lines.append("\n## 逐页索引\n")

    for page_data in pages:
        out_lines.append(build_page_section(page_data))

    out_path = os.path.join(OUTPUT_DIR, f"{filename}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"✅ 已生成索引:{out_path}")


def main():
    if not os.path.isdir(INPUT_DIR):
        print(f"❌ 找不到 OCR 结果目录:{INPUT_DIR}")
        print("请先运行:python OCR工具/ocr识别图集.py")
        return

    json_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    if not json_files:
        print("❌ OCR 结果目录是空的。请先运行 OCR 识别脚本")
        return

    print(f"📂 找到 {len(json_files)} 个 OCR 结果文件,开始生成索引...\n")
    for jf in sorted(json_files):
        process_one(os.path.join(INPUT_DIR, jf))

    print(f"\n🎉 全部索引已生成到 {OUTPUT_DIR}/")
    print("👉 现在 skill 就能用这些索引回答你的问题了!")


if __name__ == "__main__":
    main()
