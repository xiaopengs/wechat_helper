"""
renwei-writing 公众号封面 · 孟菲斯波普 v3
- 1200×500 整体
- 左侧 0-700: 标题区
- 右侧 700-1200 (500×500): 独立可截的"右边封面"方形区
- 几何元素集中在右侧方形区,截图即用
"""
from PIL import Image, ImageDraw, ImageFont
import os, math

W, H = 1200, 500
SQUARE_X = 700   # 方形区左边界
SQUARE_W = W - SQUARE_X  # 500
OUT = "/tmp/renwei_cover_v3.jpg"

# 孟菲斯撞色
BG = (255, 230, 120)       # 奶油黄
PINK = (255, 107, 157)
BLUE = (74, 144, 226)
GREEN = (6, 214, 160)
BLACK = (26, 26, 26)
ORANGE = (255, 107, 53)
PURPLE = (155, 89, 182)
CREAM = (255, 248, 220)
DARK_YELLOW = (180, 150, 50)

# 字体(CJK 优先)
FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

font_h1 = get_font(FONT_PATHS, 58)
font_sub = get_font(FONT_PATHS, 24)
font_brand = get_font(FONT_PATHS, 20)

img = Image.new('RGB', (W, H), BG)
draw = ImageDraw.Draw(img)

# ===== 左侧标题区 (0-700) =====
# 左侧散落小点(装饰,不侵入方形区)
left_dots = [
    (260, 100, 8, PINK),
    (340, 70, 10, BLUE),
    (450, 50, 7, GREEN),
    (430, 200, 7, PURPLE),
    (660, 80, 9, BLACK),
    (560, 90, 7, PINK),
    (620, 220, 6, ORANGE),
    (90, 90, 7, PINK),
    (140, 420, 6, BLUE),
    (50, 460, 8, BLACK),
    (400, 460, 5, ORANGE),
    (220, 460, 7, GREEN),
]
for x, y, r, c in left_dots:
    draw.ellipse([x-r, y-r, x+r, y+r], fill=c)

# 锯齿(左上,装饰)
zig_y = 30
zig_x = 50
zigzag = []
for i in range(7):
    x = zig_x + i * 16
    y = zig_y - (12 if i % 2 == 0 else 0)
    zigzag.append((x, y))
    zigzag.append((x + 8, zig_y + (0 if i % 2 == 0 else 0)))
draw.line(zigzag, fill=ORANGE, width=5)

# 标题主文
title1 = "凌晨五点的失败,"
title2 = "催生了一个改稿 skill"

def measure(text, font):
    try:
        return font.getbbox(text)[2]
    except Exception:
        return font.getsize(text)[0]

# 阴影 + 黑色
draw.text((52+4, 110+4), title1, font=font_h1, fill=DARK_YELLOW)
draw.text((52, 110), title1, font=font_h1, fill=BLACK)

draw.text((52+4, 180+4), title2, font=font_h1, fill=DARK_YELLOW)
draw.text((52, 180), title2, font=font_h1, fill=BLACK)

# "skill" 粉色高亮(也在左侧)
prefix_text = "催生了一个改稿 "
prefix_w = measure(prefix_text, font_h1)
skill_x = 52 + prefix_w
draw.rectangle([skill_x-6, 186, skill_x+measure("skill", font_h1)+6, 186+62], fill=PINK)
# 重画"skill"和阴影
draw.text((52+4, 180+4), title2, font=font_h1, fill=DARK_YELLOW)
draw.text((52, 180), title2, font=font_h1, fill=BLACK)
draw.rectangle([skill_x-6, 186, skill_x+measure("skill", font_h1)+6, 186+62], fill=PINK)
draw.text((skill_x, 186), "skill", font=font_h1, fill=BLACK)

# 副标题
sub = "人味儿写作心法 · renwei-writing 项目拆解"
draw.rectangle([48, 274, 52+measure(sub, font_sub)+8, 274+38], fill=BLACK)
draw.text((52, 276), sub, font=font_sub, fill=CREAM)

# ===== 中间分界线(可选,加一条浅色细线) =====
draw.line([(SQUARE_X, 0), (SQUARE_X, H)], fill=(220, 190, 80), width=1)

# ===== 右侧 500×500 方形区 (700-1200) =====
# 这是独立可截的"右边封面"

# 1) 粉色大圆(剪出方形区右上)
draw.ellipse([SQUARE_W+SQUARE_X-200, -100, SQUARE_W+SQUARE_X+50, 150], fill=PINK)
draw.arc([SQUARE_W+SQUARE_X-200, -100, SQUARE_W+SQUARE_X+50, 150], 180, 360, fill=BLACK, width=6)

# 2) 绿色错位方块(右下,带白点)
sq_x, sq_y, sq_size = SQUARE_X+30, 320, 100
angle = math.radians(12)
cos_a, sin_a = math.cos(angle), math.sin(angle)
def rot(x, y, cx, cy):
    return (cx + (x-cx)*cos_a - (y-cy)*sin_a, cy + (x-cx)*sin_a + (y-cy)*cos_a)
cx, cy = sq_x + sq_size/2, sq_y + sq_size/2
points = [
    rot(sq_x, sq_y, cx, cy),
    rot(sq_x+sq_size, sq_y, cx, cy),
    rot(sq_x+sq_size, sq_y+sq_size, cx, cy),
    rot(sq_x, sq_y+sq_size, cx, cy),
]
draw.polygon(points, fill=GREEN, outline=BLACK)
draw.ellipse([sq_x+30, sq_y+30, sq_x+75, sq_y+75], fill=CREAM, outline=BLACK, width=3)

# 3) 紫色同心圆(中部偏右)
draw.ellipse([SQUARE_X+220, 200, SQUARE_X+400, 380], fill=PURPLE, outline=BLACK, width=5)
draw.ellipse([SQUARE_X+275, 245, SQUARE_X+345, 315], fill=ORANGE)

# 4) 黑色点阵(左上)
for r in range(5):
    for c_idx in range(7):
        x = SQUARE_X + 25 + c_idx * 16
        y = 30 + r * 16
        draw.ellipse([x-2, y-2, x+2, y+2], fill=BLACK)

# 5) 粉色三角(中部偏左,装饰)
tri = [(SQUARE_X+50, 130), (SQUARE_X+130, 130), (SQUARE_X+90, 195)]
draw.polygon(tri, fill=PINK, outline=BLACK, width=3)

# 6) 蓝色波浪(下方)
wave_y = 410
points_wave = []
for i in range(120):
    x = SQUARE_X + 180 + i * 2
    y = wave_y + math.sin(i * 0.18) * 10
    points_wave.append((x, y))
for i in range(len(points_wave)-1):
    draw.line([points_wave[i], points_wave[i+1]], fill=BLUE, width=5)

# 7) 错位三色小方块(左下)
for i, (x, y, c) in enumerate([(SQUARE_X+15, 450, BLUE), (SQUARE_X+25, 440, GREEN), (SQUARE_X+35, 460, PINK)]):
    draw.rectangle([x, y, x+22, y+22], fill=c, outline=BLACK, width=2)

# 8) 品牌(右下角, 方形区内)
brand = "RENWEI-WRITING"
bw = measure(brand, font_brand)
draw.rectangle([SQUARE_X+SQUARE_W-bw-20, H-40, SQUARE_X+SQUARE_W-15, H-12], fill=BLACK)
draw.text((SQUARE_X+SQUARE_W-bw-12, H-37), brand, font=font_brand, fill=CREAM)

# 9) 一些散落小点(方形区内补一点)
right_dots = [
    (SQUARE_X+165, 60, 6, BLACK),
    (SQUARE_X+200, 180, 7, ORANGE),
    (SQUARE_X+440, 100, 6, PINK),
    (SQUARE_X+460, 250, 5, GREEN),
    (SQUARE_X+450, 350, 6, BLACK),
    (SQUARE_X+200, 380, 5, PINK),
    (SQUARE_X+420, 460, 6, BLUE),
]
for x, y, r, c in right_dots:
    draw.ellipse([x-r, y-r, x+r, y+r], fill=c)

# 10) 锯齿(底部装饰)
zig_y2 = 460
zig_x2 = SQUARE_X + 100
zigzag2 = []
for i in range(8):
    x = zig_x2 + i * 14
    y = zig_y2 - (10 if i % 2 == 0 else 0)
    zigzag2.append((x, y))
    zigzag2.append((x + 7, zig_y2 + (0 if i % 2 == 0 else 0)))
draw.line(zigzag2, fill=ORANGE, width=4)

# 保存
img = img.convert('RGB')
img.save(OUT, "JPEG", quality=92, optimize=True)
print(f"✅ 孟菲斯 v3: {OUT}")
print(f"   整体: {W}x{H}, 方形区(右边封面): {SQUARE_W}x{H}")
print(f"   大小: {os.path.getsize(OUT)} bytes")

# 同时保存右侧 500×500 截图(演示效果)
sq_img = img.crop((SQUARE_X, 0, SQUARE_X+SQUARE_W, H))
sq_out = "/tmp/renwei_cover_v3_square.jpg"
sq_img.save(sq_out, "JPEG", quality=92, optimize=True)
print(f"✅ 右侧方形区截图: {sq_out} ({sq_img.size[0]}x{sq_img.size[1]}, {os.path.getsize(sq_out)} bytes)")
