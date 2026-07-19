"""
CodeGraph 公众号封面 · 深色科技 PIL 兜底
- 1536×1024 整体(横向)
- 中央 1024×1024 主体区
- 主题:Agent 不需要更多 context,需要一张地图
- 视觉:代码地图(节点+连线)、数据钩子
"""
from PIL import Image, ImageDraw, ImageFont
import os, math, random

W, H = 1536, 1024
SQ_X = 256
SQ_W = 1024
SQ_END = SQ_X + SQ_W
OUT = "/home/ubuntu/.openclaw/workspace/wechat_helper/草稿/cover_codegraph_pil_v1.jpg"

# tech-dark 配色
BG_TOP = (10, 25, 41)
BG_BOT = (13, 27, 42)
NEON_BLUE = (0, 212, 255)    # 关键词蓝
ELEC_PURPLE = (177, 78, 255)
CYAN = (0, 255, 194)
ORANGE = (255, 107, 53)      # 判断橙
WHITE = (245, 248, 252)
GRAY = (140, 160, 180)
DIM = (60, 80, 100)
CARD_BG = (22, 38, 58)
CARD_BORDER = (90, 130, 180)

# 字体
FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
MONO_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

font_h1 = get_font(FONT_PATHS, 78)        # 主标题 "Agent 不需要更多 context"
font_h2 = get_font(FONT_PATHS, 110)       # 副主标 "需要一张地图"
font_en = get_font(MONO_PATHS, 48)        # codegraph
font_sub = get_font(FONT_PATHS, 38)       # 副标题
font_chip = get_font(FONT_PATHS, 38)      # 数据 chip
font_chip_en = get_font(FONT_PATHS, 26)   # chip 副
font_small = get_font(FONT_PATHS, 22)     # 装饰
font_mono = get_font(MONO_PATHS, 28)      # 序号/命令
font_label = get_font(FONT_PATHS, 30)     # 节点标签
font_brand = get_font(FONT_PATHS, 24)     # 底部品牌

def measure(text, font):
    try:
        return font.getbbox(text)[2]
    except Exception:
        return font.getsize(text)[0]

def text_w(text, font):
    return measure(text, font)

# 渐变背景
img = Image.new('RGB', (W, H), BG_TOP)
grad = Image.new('RGB', (W, H))
for y in range(H):
    t = y / H
    r = int(BG_TOP[0] * (1 - t) + BG_BOT[0] * t)
    g = int(BG_TOP[1] * (1 - t) + BG_BOT[1] * t)
    b = int(BG_TOP[2] * (1 - t) + BG_BOT[2] * t)
    for x in range(W):
        grad.putpixel((x, y), (r, g, b))
img.paste(grad, (0, 0))
draw = ImageDraw.Draw(img)

# 主体区底色(略深)
for y in range(H):
    t = y / H
    base_r = int(15 * (1 - t) + 18 * t)
    base_g = int(30 * (1 - t) + 35 * t)
    base_b = int(48 * (1 - t) + 55 * t)
    for x in range(SQ_X, SQ_END):
        img.putpixel((x, y), (base_r, base_g, base_b))

draw = ImageDraw.Draw(img)

# === 左侧 0-256 装饰条:数据钩子 ===
draw.text((30, 50), "+15,909", font=font_chip_en, fill=DIM)
draw.text((30, 78), "本周新增", font=font_small, fill=DIM)
draw.text((30, 130), "19,392", font=font_chip_en, fill=DIM)
draw.text((30, 158), "总 Star", font=font_small, fill=DIM)
draw.text((30, 210), "20k+", font=font_chip_en, fill=DIM)
draw.text((30, 238), "5 月抓取", font=font_small, fill=DIM)

# 左下角小标
draw.text((30, 920), "CodeGraph", font=font_label, fill=GRAY)
draw.text((30, 955), "MCP · Local", font=font_small, fill=DIM)

# === 右侧 1280-1536 装饰条:数据钩子 ===
draw.text((1290, 50), "-71%", font=font_chip_en, fill=NEON_BLUE)
draw.text((1290, 78), "工具调用", font=font_small, fill=DIM)
draw.text((1290, 130), "-57%", font=font_chip_en, fill=NEON_BLUE)
draw.text((1290, 158), "Token 消耗", font=font_small, fill=DIM)
draw.text((1290, 210), "+46%", font=font_chip_en, fill=ORANGE)
draw.text((1290, 238), "速度", font=font_small, fill=DIM)
draw.text((1290, 290), "100%", font=font_chip_en, fill=CYAN)
draw.text((1290, 318), "本地运行", font=font_small, fill=DIM)
draw.text((1290, 370), "0", font=font_chip_en, fill=CYAN)
draw.text((1290, 398), "API Key", font=font_small, fill=DIM)

# 右下角:标签
draw.text((1290, 920), "v0.9.4", font=font_label, fill=GRAY)
draw.text((1290, 955), "2026-06-16", font=font_small, fill=DIM)

# === 主体区设计 ===
mx0 = SQ_X + 60
mx1 = SQ_END - 60
my0 = 80
my1 = H - 80

# 顶部:小标 + 英文项目名
draw.text((mx0, my0), "AGENT · MCP · CODE INTELLIGENCE", font=font_small, fill=DIM)
draw.text((mx0, my0 + 28), "codegraph", font=font_en, fill=NEON_BLUE)

# 分隔线
draw.line([(mx0, my0 + 90), (mx1, my0 + 90)], fill=DIM, width=2)

# 主标题(两行,大字号)
title1 = "Agent 不需要更多 context,"
title2 = "需要一张地图"
y_t1 = my0 + 130
y_t2 = y_t1 + 100
draw.text((mx0, y_t1), title1, font=font_h1, fill=WHITE)
draw.text((mx0, y_t2), title2, font=font_h2, fill=ORANGE)

# 副标题/钩子
sub = "预计算代码地图 · 工具调用 -71% · Token -57% · 速度 +46%"
y_sub = y_t2 + 150
draw.text((mx0, y_sub), sub, font=font_sub, fill=GRAY)

# === 视觉中心:代码地图(节点 + 连线) ===
# 位置:右下区域
map_cx = SQ_END - 280
map_cy = 720
node_r = 18

# 节点坐标(围绕中心)
nodes = [
    (map_cx, map_cy, "main", NEON_BLUE),
    (map_cx - 180, map_cy - 100, "auth", GRAY),
    (map_cx + 180, map_cy - 100, "api", GRAY),
    (map_cx - 220, map_cy + 60, "db", GRAY),
    (map_cx + 220, map_cy + 60, "util", GRAY),
    (map_cx - 100, map_cy - 200, "route", CYAN),
    (map_cx + 100, map_cy - 200, "ctrl", CYAN),
    (map_cx + 0, map_cy + 180, "test", GRAY),
]

# 连线(预先画,在节点下层)
edges = [
    (0, 1), (0, 2), (0, 3), (0, 4),
    (0, 5), (0, 6), (0, 7),
    (1, 5), (2, 6), (3, 7), (4, 7),
]
for a, b in edges:
    xa, ya, _, _ = nodes[a]
    xb, yb, _, _ = nodes[b]
    # 主节点连出的是亮蓝,其余暗灰
    col = NEON_BLUE if (a == 0 or b == 0) else DIM
    draw.line([(xa, ya), (xb, yb)], fill=col, width=2)

# 节点
for x, y, label, color in nodes:
    # 外圈光晕
    if color in (NEON_BLUE, CYAN):
        draw.ellipse([x - node_r - 6, y - node_r - 6, x + node_r + 6, y + node_r + 6],
                     outline=color, width=1)
    # 节点本体
    draw.ellipse([x - node_r, y - node_r, x + node_r, y + node_r],
                 fill=color if color != GRAY else (40, 60, 80), outline=WHITE, width=2)
    # 主节点标签
    if label == "main":
        draw.text((x - 30, y + node_r + 8), label, font=font_mono, fill=NEON_BLUE)

# 装饰:远端小点(模拟更多节点)
random.seed(42)
for _ in range(35):
    x = random.randint(SQ_X + 30, SQ_END - 30)
    y = random.randint(180, H - 30)
    # 远离主标题区域
    if y < 460 and x < SQ_X + 700:
        continue
    r = random.choice([1, 1, 2])
    draw.ellipse([x - r, y - r, x + r, y + r], fill=DIM)

# === 底部:jerry-wechat 风格签名 ===
draw.text((mx0, H - 70), "工程哲学 · 实测数据 · 踩坑指南", font=font_sub, fill=GRAY)
draw.text((mx0, H - 35), "— 黑爪爪 / 2026.06.16", font=font_brand, fill=DIM)

# 保存
img = img.convert('RGB')
img.save(OUT, "JPEG", quality=92, optimize=True)
print(f"✅ PIL 兜底封面: {OUT}")
print(f"   整体: {W}x{H}, 主体区: {SQ_W}x{H} 中央")
print(f"   大小: {os.path.getsize(OUT)//1024} KB")

# 主体区方形
sq_img = img.crop((SQ_X, 0, SQ_END, H))
sq_out = "/home/ubuntu/.openclaw/workspace/wechat_helper/草稿/cover_codegraph_pil_v1_square.jpg"
sq_img.save(sq_out, "JPEG", quality=92, optimize=True)
print(f"✅ 主体区方形截图: {sq_out} ({sq_img.size[0]}x{sq_img.size[1]}, {os.path.getsize(sq_out)//1024} KB)")
