# zhongnan-atlas-cd-course

> 中南标图集 × AI = 施工图前辈随叫随到

把老师给的 6 本中南标图集 PDF（共 523 页扫描件）用 OCR 蒸馏成轻量文字索引，让任何 AI 都能帮你查做法编号、找页码、解释构造——**不用再上传几百 MB 的 PDF**。

---

## 快速安装（Kiro 用户）

在 Kiro 里一句话安装：

```
安装 skill：https://github.com/Xarles-Lovell/zhongnan-atlas-cd-course
```

Kiro 会自动克隆 `zhongnan-atlas-cd-course/` 文件夹（skill 本体）到你的工作区。安装后直接问施工图问题即可。

---

## 不用 Kiro？也能用

这个 skill 的核心就是一组 Markdown 文件，**任何 AI 对话都能用**：

1. 下载 `zhongnan-atlas-cd-course/` 文件夹
2. 把 `SKILL.md` + `references/` 里的索引文件发给你习惯用的 AI（不确定发哪个就全部发，README 不用发）
3. 开始问问题

详细使用方法见 [`zhongnan-atlas-cd-course/README.md`](zhongnan-atlas-cd-course/README.md)

---

## 直接用 GitHub 链接（最懒的方式）

如果你用的 AI 支持联网/读链接（比如 Kimi、ChatGPT 联网模式、豆包等），**不用下载任何文件**，直接在对话里发这段话：

```
请你访问这个链接 https://github.com/Xarles-Lovell/zhongnan-atlas-cd-course/blob/main/zhongnan-atlas-cd-course/SKILL.md 阅读里面的内容，按照要求扮演施工图前辈来回答我的问题。再访问 https://github.com/Xarles-Lovell/zhongnan-atlas-cd-course/tree/main/zhongnan-atlas-cd-course/references 读取里面的索引文件作为你的知识库。
```

然后直接问问题就行。

> 💡 如果 AI 说"无法访问链接"，说明它不支持联网,换上面的"下载文件"方式就行。

---

## 仓库结构

```
.
├── zhongnan-atlas-cd-course/    ← 🎯 skill 本体（安装只需要这个）
│   ├── SKILL.md                 ← AI 行为指令
│   ├── README.md                ← skill 使用说明
│   └── references/              ← 6 本图集的文字索引（共 500 KB）
│       ├── 中南15ZJ001-建筑构造用料做法.md   ⭐ 总做法表，最重要
│       ├── 中南15ZJ201-平屋面.md
│       ├── 中南15ZJ203-种植屋面.md
│       ├── 中南15ZJ211-坡屋面.md
│       ├── 中南15ZJ602-建筑节能门窗.md
│       └── 中南15ZJ611-拉闸门和卷帘门建筑构造.md
│
├── 原图集/                      ← � 6 本 PDF 原件（补充材料，用来核对页码）
│
├── OCR工具/                     ← 🔧 OCR 脚本（想重新生成索引时用）
│
└── README.md                    ← 你正在看的这个
```

### references 文件夹说明

`references/` 里的 6 个 `.md` 文件是从扫描版 PDF 用 OCR 识别后整理的结构化索引，包含：
- 每本图集的目录结构
- 每页的关键文字内容（做法编号、材料说明、节点名称等）
- 页码与节点号对照

AI 查询时会读取这些文件，然后告诉用户精确的页码出处。如果图集 PDF 有更新，用 `OCR工具/` 里的脚本重新生成即可。

**只想用 skill？** → 只需要 `zhongnan-atlas-cd-course/` 文件夹  
**想核对页码？** → 下载 `原图集/` 里的 PDF  
**想重新跑 OCR？** → 用 `OCR工具/` 里的脚本

---

## 包含哪些图集

| 编号 | 名称 | 页数 | 用途 |
|---|---|---|---|
| 中南15ZJ001 | 建筑构造用料做法 | 154 | 总做法表（L3、N2、W1 等编号的定义） |
| 中南15ZJ201 | 平屋面 | 42 | 平屋面节点详图 |
| 中南15ZJ203 | 种植屋面 | 38 | 屋顶花园构造 |
| 中南15ZJ211 | 坡屋面 | 74 | 瓦面、金属屋面 |
| 中南15ZJ602 | 建筑节能门窗 | 181 | 门窗选型、K 值 |
| 中南15ZJ611 | 拉闸门和卷帘门 | 29 | 商业门面门构造 |

---

## 适用范围

- ✅ 中南林业科技大学 22 级建筑学 · 施工图设计课程
- ✅ 老师指定的这 6 本中南标图集（2015 版）
- ❌ 不适用于其他地区图集（华北标、西南标、国标 06J 等）
- ❌ 不适用于结构/暖通/给排水等其他专业

---

## 示例问题

```
楼101 是什么做法？详细说说每一层
平屋面的排水口节点怎么画？
卫生间大样怎么画？
下沉式卫生间用什么做法编号？
天沟和檐沟的防水构造有什么区别？
中空玻璃 5+9A+5 的 K 值是多少？
女儿墙泛水节点在哪一页？
```

---

## 技术细节

- **OCR 引擎**：RapidOCR (onnxruntime)
- **源文件**：无水印版 PDF
- **识别置信度**：平均 97%
- **索引总大小**：~500 KB（原始 PDF 几百 MB → 压缩 99%）
- **Python 依赖**：pymupdf, pillow, rapidocr-onnxruntime

---

## 版权说明

图集内容版权归湖北中南标科技发展中心 / 中国建材工业出版社所有。本仓库仅做文字索引化处理，用于课程学习，不用于商业用途。
