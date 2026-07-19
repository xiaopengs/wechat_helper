"""
renwei-writing 公众号封面 · 孟菲斯波普风格 v2
- 去掉"黑爪爪"署名
- 满版几何元素(圆点/三角/波浪/错位方块/锯齿/点阵)
- 高饱和撞色
- 黑粗描边 sans-serif
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, random

random.seed(42)

W, H = 1200, 500
OUT = "/tmp/renwei_cover_v2.jpg"

# 孟菲斯经典撞色
BG = (255, 230, 120)        # 奶油黄背景
PINK = (255, 107, 157)      # 电光粉
BLUE = (74, 144, 226)       # 湖蓝
GREEN = (6, 214, 160)       # 薄荷绿
BLACK = (26, 26, 26)        # 哑黑
ORANGE = (255, 107, 53)     # 橙红
PURPLE = (155, 89, 182)     # 紫
CREAM = (255, 248, 220)     # 奶油白

# 字体路径
# CJK 优先(中文字形只在 CJK 字体里)
FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]
CJK_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

# 字体(全部用 CJK 优先)
font_h1 = get_font(FONT_PATHS, 64)        # 主标题
font_sub = get_font(FONT_PATHS, 26)        # 副标题
font_brand = get_font(FONT_PATHS, 22)     # 品牌

# 创建画布
img = Image.new('RGB', (W, H), BG)
draw = ImageDraw.Draw(img)

# ===== 孟菲斯几何元素层 =====

# 1) 右上角大粉色圆(剪掉一部分超出边界)
draw.ellipse([W-180, -100, W+50, 130], fill=PINK)
# 给圆加黑色粗描边(只画可见部分)
draw.arc([W-180, -100, W+50, 130], 180, 360, fill=BLACK, width=6)

# 2) 左下角大绿色错位方块(旋转感)
# 用多边形画一个错位方块
sq_x, sq_y, sq_size = 80, 360, 110
# 旋转 12 度的方块(用多边形)
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
# 在方块内画个小白点
draw.ellipse([sq_x+30, sq_y+30, sq_x+80, sq_y+80], fill=CREAM, outline=BLACK, width=3)

# 3) 中间偏右大蓝紫圆
draw.ellipse([700, 280, 880, 460], fill=PURPLE, outline=BLACK, width=5)
# 圆里画个黄色圆
draw.ellipse([750, 320, 830, 400], fill=ORANGE)

# 4) 散落的小圆点(各种颜色)
small_dots = [
    (260, 100, 8, PINK),
    (340, 70, 10, BLUE),
    (450, 50, 7, GREEN),
    (980, 200, 9, BLACK),
    (1080, 280, 11, PINK),
    (1130, 80, 8, BLUE),
    (430, 200, 7, PURPLE),
    (1080, 380, 9, ORANGE),
    (50, 420, 11, BLUE),
    (240, 430, 8, BLACK),
    (380, 380, 7, PINK),
    (1020, 150, 8, GREEN),
    (660, 80, 9, BLACK),
    (560, 90, 7, PINK),
]
for x, y, r, c in small_dots:
    draw.ellipse([x-r, y-r, x+r, y+r], fill=c)

# 5) 蓝色波浪线(右下)
wave_y = 380
wave_x_start = 500
points_wave = []
for i in range(200):
    x = wave_x_start + i * 2
    y = wave_y + math.sin(i * 0.15) * 12
    points_wave.append((x, y))
for i in range(len(points_wave)-1):
    draw.line([points_wave[i], points_wave[i+1]], fill=BLUE, width=5)

# 6) 锯齿条(粉色,左上)
zig_y = 130
zig_x = 420
zigzag = []
for i in range(7):
    x = zig_x + i * 18
    y = zig_y - (15 if i % 2 == 0 else 0)
    zigzag.append((x, y))
    zigzag.append((x + 9, zig_y + (0 if i % 2 == 0 else 0)))
draw.line(zigzag, fill=ORANGE, width=6)

# 7) 错位色块(右下角, 3 个错位小方块)
for i, (x, y, c) in enumerate([(1100, 430, BLUE), (1110, 420, GREEN), (1120, 440, PINK)]):
    draw.rectangle([x, y, x+22, y+22], fill=c, outline=BLACK, width=2)

# 8) 点阵(右下,8x5)
for r in range(5):
    for c_idx in range(8):
        x = 980 + c_idx * 18
        y = 90 + r * 18
        draw.ellipse([x-3, y-3, x+3, y+3], fill=BLACK)

# 9) 一条粗黑色横线(中部偏下,分割作用, 但要弱)
draw.line([(0, 410), (W, 410)], fill=BLACK, width=3)

# 10) 右侧大三角(粉色,装饰)
tri = [(880, 60), (970, 60), (925, 130)]
draw.polygon(tri, fill=PINK, outline=BLACK, width=3)

# ===== 标题区 =====
# 主标题: "凌晨五点的失败"
title1 = "凌晨五点的失败,"
title2 = "催生了一个改稿 skill"

# 阴影
shadow_offset = 4
draw.text((52+shadow_offset, 130+shadow_offset), title1, font=font_h1, fill=(180, 150, 50))
draw.text((52, 130), title1, font=font_h1, fill=BLACK)

# 第二行
draw.text((52+shadow_offset, 210+shadow_offset), title2, font=font_h1, fill=(180, 150, 50))
draw.text((52, 210), title2, font=font_h1, fill=BLACK)

# 在 "skill" 后面加个粉色高亮色块
# 估算 "催生了一个改稿 " 长度,然后画矩形在 "skill" 后面
def measure(text, font):
    try:
        return font.getbbox(text)[2]
    except Exception:
        return font.getsize(text)[0]

# 计算 skill 位置
prefix_text = "催生了一个改稿 "
prefix_w = measure(prefix_text, font_h1)
skill_x = 52 + prefix_w
# 粉色高亮(包住 "skill")
draw.rectangle([skill_x-6, 215, skill_x+measure("skill", font_h1)+6, 215+68], fill=PINK)
# 重新写第二行(让 skill 在粉色块上是黑色,清晰)
draw.text((52+shadow_offset, 210+shadow_offset), title2, font=font_h1, fill=(180, 150, 50))
draw.text((52, 210), title2, font=font_h1, fill=BLACK)
# 重画粉色块(覆盖阴影)
draw.rectangle([skill_x-6, 215, skill_x+measure("skill", font_h1)+6, 215+68], fill=PINK)
draw.text((skill_x, 215), "skill", font=font_h1, fill=BLACK)

# 副标题
sub = "人味儿写作心法 · renwei-writing 项目拆解"
draw.rectangle([48, 308, 52+measure(sub, font_sub)+8, 308+40], fill=BLACK)
draw.text((52, 310), sub, font=font_sub, fill=CREAM)

# 底部品牌标识
brand = "RENWEI-WRITING · 2026.06.14"
draw.text((W-380, H-45), brand, font=font_brand, fill=BLACK)

# 保存(JPEG q92, 微信 <1MB 一般没问题)
img = img.convert('RGB')
img.save(OUT, "JPEG", quality=92, optimize=True)
size = os.path.getsize(OUT)
print(f"✅ 孟菲斯风封面: {OUT}")
print(f"   尺寸: {W}x{H}, 大小: {size} bytes ({size/1024:.1f} KB)")
