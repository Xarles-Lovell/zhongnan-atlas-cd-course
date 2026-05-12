# -*- coding: utf-8 -*-
"""
============================================================
中南标图集 OCR 识别脚本
============================================================
作用:把扫描版的 PDF 图集(图片)转成电脑能读的文字
输出:每本图集的文字识别结果,保存为 json 文件

使用方法:
1. 按照同目录下的"安装教程.md"安装好依赖
2. 双击运行此文件,或在命令行输入 python OCR工具/ocr识别图集.py

运行时间:取决于电脑性能,6 本图集 523 页,预估 30-60 分钟
============================================================
"""
import os
import sys
import json
import time
import io

# ---------- 第 1 步:检查依赖是否安装好 ----------
# 如果缺库,给出明确的安装提示,而不是报一串看不懂的错
try:
    import fitz  # pymupdf:把 PDF 页面转成图片
except ImportError:
    print("❌ 缺少 pymupdf 库。请在命令行运行:pip install pymupdf")
    sys.exit(1)

try:
    from rapidocr_onnxruntime import RapidOCR  # 轻量 OCR 引擎,中文效果好
except ImportError:
    print("❌ 缺少 rapidocr_onnxruntime 库。请在命令行运行:pip install rapidocr-onnxruntime")
    sys.exit(1)

try:
    from PIL import Image  # 图像处理库
except ImportError:
    print("❌ 缺少 Pillow 库。请在命令行运行:pip install pillow")
    sys.exit(1)

import numpy as np

# ---------- 第 2 步:配置要处理的 PDF 文件 ----------
# 这里列出 6 本图集的文件名,必须和实际文件名完全一致
PDF_FILES = [
    "中南15ZJ001《建筑构造用料做法》.pdf",
    "中南15ZJ201《平屋面》.pdf",
    "中南15ZJ203《种植屋面》.pdf",
    "中南15ZJ211《坡屋面》.pdf",
    "中南15ZJ602《建筑节能门窗》.pdf",
    "中南15ZJ611《拉闸门和卷帘门建筑构造》.pdf",
]

# 输出目录:OCR 识别结果保存在这里
OUT_DIR = "OCR工具/识别结果"
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- 第 3 步:初始化 OCR 引擎 ----------
# 第一次运行会自动下载模型文件(约 10MB),之后就不用再下载了
print("🔧 正在初始化 OCR 引擎(第一次运行会下载模型,请耐心等待)...")
ocr_engine = RapidOCR()
print("✅ OCR 引擎准备就绪\n")


def pdf_page_to_image(page, dpi=200):
    """把 PDF 的一页转成图片(numpy 数组),供 OCR 引擎识别
    dpi 值越高识别越准,但速度越慢,200 是平衡值
    """
    # zoom 决定清晰度,2.0 ≈ 144dpi, 2.78 ≈ 200dpi
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    # 把 pymupdf 的图像转成 PIL 图像
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    # 转成 OCR 引擎需要的 numpy 格式(RGB)
    return np.array(img.convert("RGB"))


def ocr_one_pdf(pdf_path):
    """对一本 PDF 图集做完整的 OCR 识别"""
    print(f"\n📖 开始处理:{pdf_path}")
    doc = fitz.open(pdf_path)
    total = doc.page_count
    pages_result = []
    start_time = time.time()

    for i in range(total):
        page_num = i + 1
        page = doc.load_page(i)

        # 把这一页 PDF 转成图片
        img_array = pdf_page_to_image(page)

        # 交给 OCR 引擎识别
        # 返回格式:([[框坐标, 文字, 置信度], ...], 耗时)
        try:
            result, _ = ocr_engine(img_array)
        except Exception as e:
            print(f"   ⚠️ 第 {page_num} 页识别出错:{e}")
            result = None

        # 整理识别到的文字
        texts = []
        if result:
            for item in result:
                # item = [框坐标, 文字, 置信度]
                text = item[1]
                confidence = float(item[2])
                texts.append({"text": text, "confidence": round(confidence, 3)})

        pages_result.append({
            "page": page_num,
            "text_count": len(texts),
            "texts": texts,
        })

        # 每识别 5 页输出一次进度,让人知道没卡死
        if page_num % 5 == 0 or page_num == total:
            elapsed = time.time() - start_time
            avg = elapsed / page_num
            remaining = avg * (total - page_num)
            print(f"   进度 {page_num}/{total},已用时 {elapsed:.0f} 秒,预计还需 {remaining:.0f} 秒")

    doc.close()
    return pages_result


def main():
    overall_start = time.time()

    # 检查 PDF 文件是否都存在
    missing = [f for f in PDF_FILES if not os.path.exists(f)]
    if missing:
        print("❌ 以下 PDF 文件找不到,请确认它们和本脚本在同一目录:")
        for f in missing:
            print(f"   - {f}")
        return

    # 依次处理每本图集
    for pdf_name in PDF_FILES:
        # 生成一个安全的输出文件名(去掉书名号)
        safe_name = pdf_name.replace("《", "-").replace("》", "").replace(".pdf", "")
        out_path = os.path.join(OUT_DIR, f"{safe_name}.json")

        # 如果已经识别过,跳过(方便中断后续跑)
        if os.path.exists(out_path):
            print(f"⏩ 跳过已识别的:{pdf_name}")
            continue

        result = ocr_one_pdf(pdf_name)

        # 保存识别结果
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({
                "pdf": pdf_name,
                "total_pages": len(result),
                "pages": result,
            }, f, ensure_ascii=False, indent=2)
        print(f"✅ 已保存:{out_path}")

    total_time = time.time() - overall_start
    print(f"\n🎉 全部完成!总耗时 {total_time/60:.1f} 分钟")
    print(f"📁 识别结果保存在:{OUT_DIR}/")
    print("\n👉 下一步:把这个结果告诉 Kiro,它会帮你建立 skill 的索引")


if __name__ == "__main__":
    main()
