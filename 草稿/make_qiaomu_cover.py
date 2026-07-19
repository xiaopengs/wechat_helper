"""
qiaomu-novel-generator 公众号封面 · 深色科技 PIL 兜底
- 1536×1024 整体(横向,接近公众号头条 1.78:1)
- 中央 1024×1024 主体区(feed 裁方也保信息)
- 左侧 0-256 + 右侧 1280-1536 装饰条(各 256px)
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1536, 1024
SQ_X = 256          # 主体区左边界
SQ_W = 1024         # 主体区宽度(中央正方形)
SQ_END = SQ_X + SQ_W  # 1280
OUT = "/home/ubuntu/.openclaw/workspace/wechat_helper/草稿/cover_qiaomu_pil_v1.jpg"

# tech-dark 配色
BG_TOP = (10, 25, 41)        # #0A1929
BG_BOT = (13, 27, 42)        # #0D1B2A
NEON_BLUE = (0, 212, 255)    # #00D4FF
ELEC_PURPLE = (177, 78, 255) # #B14EFF
CYAN = (0, 255, 194)         # #00FFC2
ORANGE = (255, 107, 53)      # #FF6B35
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

font_h1 = get_font(FONT_PATHS, 130)        # "乔木小说" 主标题
font_h2 = get_font(FONT_PATHS, 96)         # "qiaomu-novel"
font_h3 = get_font(FONT_PATHS, 150)        # "SKILL"
font_sub = get_font(FONT_PATHS, 44)        # 副标题
font_chip = get_font(FONT_PATHS, 38)       # 4 chip
font_chip_en = get_font(FONT_PATHS, 26)    # chip 副
font_small = get_font(FONT_PATHS, 22)      # 装饰
font_mono = get_font(MONO_PATHS, 28)       # 序号/命令
font_label = get_font(FONT_PATHS, 32)      # JOESEE SUN 等
font_brand = get_font(FONT_PATHS, 26)

def measure(text, font):
    try:
        return font.getbbox(text)[2]
    except Exception:
        return font.getsize(text)[0]

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

# 暗格点阵背景(主体区除外,主体区是干净)
def draw_dots(x0, y0, x1, y1, step, color, r=1):
    for x in range(x0, x1, step):
        for y in range(y0, y1, step):
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)

# 左侧 0-256 装饰
draw_dots(20, 30, 240, 1000, 20, DIM, 1)
# 右侧 1280-1536 装饰
draw_dots(1290, 30, 1520, 1000, 20, DIM, 1)
# 主体区也有点阵(更稀)
draw_dots(SQ_X+20, 30, SQ_END-20, 1000, 32, DIM, 1)

# 主体区暗色卡片底(深蓝,边框霓虹蓝)
draw.rectangle([SQ_X+10, 30, SQ_END-10, H-30], fill=CARD_BG, outline=CARD_BORDER, width=2)

# === 主体区内容 ===
# 顶部小标签
top_label = "JOESEE SUN  ·  GITHUB OPEN SOURCE  ·  MIT"
tw = measure(top_label, font_label)
draw.text((SQ_X + (SQ_W - tw)//2, 70), top_label, font=font_label, fill=CYAN)

# 装饰条(顶部小线)
draw.line([(SQ_X+200, 130), (SQ_X+400, 130)], fill=NEON_BLUE, width=3)
draw.line([(SQ_END-400, 130), (SQ_END-200, 130)], fill=NEON_BLUE, width=3)
draw.ellipse([SQ_X+400-6, 124, SQ_X+400+6, 136], fill=ORANGE)
draw.ellipse([SQ_END-400-6, 124, SQ_END-400+6, 136], fill=ORANGE)

# 主标题"乔木小说" 大
t1 = "乔木小说"
t1w = measure(t1, font_h1)
draw.text((SQ_X + (SQ_W - t1w)//2, 175), t1, font=font_h1, fill=WHITE)
# 阴影描边
for off in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
    draw.text((SQ_X + (SQ_W - t1w)//2 + off[0], 175 + off[1]), t1, font=font_h1, fill=NEON_BLUE)

# 重画主线(白)
draw.text((SQ_X + (SQ_W - t1w)//2, 175), t1, font=font_h1, fill=WHITE)

# "qiaomu-novel"
t2 = "qiaomu-novel"
t2w = measure(t2, font_h2)
draw.text((SQ_X + (SQ_W - t2w)//2, 330), t2, font=font_h2, fill=GRAY)

# "SKILL" 超大
t3 = "SKILL"
t3w = measure(t3, font_h3)
# 投影
for off in [(4, 4), (-2, -2)]:
    draw.text((SQ_X + (SQ_W - t3w)//2 + off[0], 445 + off[1]), t3, font=font_h3, fill=NEON_BLUE)
# 主体
draw.text((SQ_X + (SQ_W - t3w)//2, 445), t3, font=font_h3, fill=NEON_BLUE)
# 内描边
draw.text((SQ_X + (SQ_W - t3w)//2, 445), t3, font=font_h3, fill=NEON_BLUE)

# 副标题
sub = "从一句灵感,生成 2500 字钩子短篇"
subw = measure(sub, font_sub)
draw.text((SQ_X + (SQ_W - subw)//2, 620), sub, font=font_sub, fill=CYAN)

# 4 个能力 chip(2x2)
chip_w = 420
chip_h = 90
chip_gap = 24
chip_total_w = chip_w * 2 + chip_gap
chip_x0 = SQ_X + (SQ_W - chip_total_w) // 2
chip_y0 = 700
chips = [
    ("15 个 Hook 检查点", "15 Hooks · 完整流程"),
    ("0 AI 味 强钩子", "Anti-AI · 强钩子"),
    ("写前访谈 + 经典桥段", "Interview · Beats"),
    ("2500 字完整小说", "1800-4000 字短篇"),
]
for i, (main, en) in enumerate(chips):
    r, c = i // 2, i % 2
    x = chip_x0 + c * (chip_w + chip_gap)
    y = chip_y0 + r * (chip_h + chip_gap)
    # 卡片
    draw.rounded_rectangle([x, y, x+chip_w, y+chip_h], radius=12, fill=(28, 48, 72), outline=NEON_BLUE, width=2)
    # 左边小色块
    draw.rectangle([x, y, x+8, y+chip_h], fill=[NEON_BLUE, ELEC_PURPLE, CYAN, ORANGE][i])
    # 主文字
    draw.text((x+24, y+12), main, font=font_chip, fill=WHITE)
    # 英文小字
    draw.text((x+24, y+58), en, font=font_chip_en, fill=GRAY)

# 底部安装命令
cmd = "npx skills add joeseesun/qiaomu-novel-generator"
cmds = measure(cmd, font_mono)
draw.rectangle([SQ_X + (SQ_W - cmds)//2 - 18, 920, SQ_X + (SQ_W + cmds)//2 + 18, 970], fill=(15, 30, 50), outline=NEON_BLUE, width=1)
draw.text((SQ_X + (SQ_W - cmds)//2, 928), cmd, font=font_mono, fill=NEON_BLUE)

# === 左侧 256px 装饰条 ===
# 5 个物理"钩子"图形 + 序号
def draw_hook(cx, cy, size, color, direction='right'):
    """画一个钩子形状(类似 'J' 反向或 'L')"""
    pts = []
    # 钩子主干(竖)+ 弯钩(水平)
    pts.append((cx, cy - size//2))   # 顶
    pts.append((cx, cy + size//3))   # 底
    if direction == 'right':
        pts.append((cx + size//2, cy + size//3))  # 弯
        pts.append((cx + size//2, cy + size//2))  # 底
    else:
        pts.append((cx - size//2, cy + size//3))
        pts.append((cx - size//2, cy + size//2))
    pts.append((cx, cy + size//2))   # 回到中
    pts.append((cx, cy - size//2))   # 闭合
    draw.polygon(pts, outline=color, width=5)
    # 填充钩子弯处
    if direction == 'right':
        draw.ellipse([cx+size//2-8, cy+size//3-4, cx+size//2+8, cy+size//3+12], fill=color)
    else:
        draw.ellipse([cx-size//2-8, cy+size//3-4, cx-size//2+8, cy+size//3+12], fill=color)

hook_colors = [CYAN, NEON_BLUE, ELEC_PURPLE, ORANGE, CYAN]
hook_dirs = ['right', 'left', 'right', 'left', 'right']
for i in range(5):
    cy = 180 + i * 160
    # 序号(右侧)
    num = f"0{i+1}"
    nw = measure(num, font_mono)
    draw.text((180, cy - 14), num, font=font_mono, fill=hook_colors[i])
    # 钩子
    draw_hook(80, cy, 70, hook_colors[i], hook_dirs[i])

# 顶部小标签
draw.text((20, 60), "15", font=font_h1, fill=NEON_BLUE)
draw.text((130, 80), "·", font=font_h1, fill=ORANGE)
draw.text((150, 95), "HOOK", font=font_label, fill=WHITE)

# === 右侧 256px 装饰条 ===
# 3D 等距半开书
bx, by = 1380, 250
# 书底(暗)
draw.rounded_rectangle([bx-110, by+30, bx+110, by+260], radius=8, fill=(35, 55, 80), outline=WHITE, width=2)
# 翻页(亮)
draw.polygon([
    (bx-110, by+30),
    (bx, by-10),
    (bx+110, by+30),
    (bx+110, by+260),
    (bx, by+220),
    (bx-110, by+260),
], fill=(70, 110, 160), outline=WHITE, width=2)
# 中心线
draw.line([(bx, by-10), (bx, by+220)], fill=WHITE, width=2)
# 钩子交叉符号(在书上)
draw_hook(bx-25, by+120, 50, NEON_BLUE, 'right')
draw_hook(bx+25, by+120, 50, ELEC_PURPLE, 'left')

# 数字矩阵
matrix_y = 560
matrix_items = [
    ("0 AI 味", CYAN),
    ("100% 原创", ORANGE),
    ("MIT", NEON_BLUE),
]
for i, (text, color) in enumerate(matrix_items):
    y = matrix_y + i * 80
    # 圆点
    draw.ellipse([1310, y-8, 1330, y+12], fill=color)
    draw.text((1340, y-6), text, font=font_brand, fill=WHITE)

# 底部小字
draw.text((1300, 980), "v1.0", font=font_small, fill=DIM)
draw.text((1460, 980), "2026", font=font_small, fill=DIM)

# 保存
img = img.convert('RGB')
img.save(OUT, "JPEG", quality=92, optimize=True)
print(f"✅ PIL 兜底封面: {OUT}")
print(f"   整体: {W}x{H}, 主体区: {SQ_W}x{H} 中央")
print(f"   大小: {os.path.getsize(OUT)//1024} KB")

# 同时保存主体区方形(900x900)演示
sq_img = img.crop((SQ_X, 0, SQ_END, H))
sq_out = "/home/ubuntu/.openclaw/workspace/wechat_helper/草稿/cover_qiaomu_pil_v1_square.jpg"
sq_img.save(sq_out, "JPEG", quality=92, optimize=True)
print(f"✅ 主体区方形截图: {sq_out} ({sq_img.size[0]}x{sq_img.size[1]}, {os.path.getsize(sq_out)//1024} KB)")
