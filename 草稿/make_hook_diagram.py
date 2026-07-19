"""
qiaomu 15 Hooks 流程图 PIL 兜底
- 1536×1024 整体
- 5 列 3 行 网格,共 15 个 Hook 卡片
- 深色科技风格
"""
from PIL import Image, ImageDraw, ImageFont
import os

W, H = 1536, 1024
OUT = "/home/ubuntu/.openclaw/workspace/wechat_helper/草稿/hook_diagram_pil_v1.jpg"

# tech-dark 配色
BG_TOP = (10, 25, 41)
BG_BOT = (13, 27, 42)
NEON_BLUE = (0, 212, 255)
ELEC_PURPLE = (177, 78, 255)
CYAN = (0, 255, 194)
ORANGE = (255, 107, 53)
WHITE = (245, 248, 252)
GRAY = (140, 160, 180)
DIM = (60, 80, 100)
CARD_BG = (22, 38, 58)
CARD_BORDER = (90, 130, 180)

FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
MONO_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]

def get_font(paths, size):
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()

font_title = get_font(FONT_PATHS, 52)
font_num = get_font(FONT_PATHS, 48)
font_zh = get_font(FONT_PATHS, 38)
font_en = get_font(MONO_PATHS, 22)
font_brand = get_font(FONT_PATHS, 24)
font_arrow = get_font(FONT_PATHS, 32)

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
    r = int(BG_TOP[0]*(1-t) + BG_BOT[0]*t)
    g = int(BG_TOP[1]*(1-t) + BG_BOT[1]*t)
    b = int(BG_TOP[2]*(1-t) + BG_BOT[2]*t)
    for x in range(W):
        grad.putpixel((x, y), (r, g, b))
img.paste(grad, (0, 0))
draw = ImageDraw.Draw(img)

# 暗格点阵
def draw_dots(x0, y0, x1, y1, step, color, r=1):
    for x in range(x0, x1, step):
        for y in range(y0, y1, step):
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
draw_dots(20, 20, W-20, H-20, 30, DIM, 1)

# 顶部标题
title = "15 个 Hook · 一个完整小说生成的 15 个检查点"
tw = measure(title, font_title)
draw.text((60, 50), title, font=font_title, fill=WHITE)
# 装饰条
draw.line([(60, 120), (60+tw+30, 120)], fill=NEON_BLUE, width=3)
draw.ellipse([60+tw+30-6, 114, 60+tw+30+6, 126], fill=ORANGE)
# 副标题(英文)
sub = "Qiaomu Novel Generator  ·  15 Hook Checkpoints  ·  Fixed Order"
draw.text((60, 130), sub, font=font_brand, fill=CYAN)

# 15 Hook 卡片布局
hooks = [
    ("01", "意图识别", "Intent", NEON_BLUE),
    ("02", "资料调研", "Source", CYAN),
    ("03", "灵感混音", "Inspiration", ELEC_PURPLE),
    ("04", "故事引擎", "Engine", ORANGE),
    ("05", "写前访谈", "Interview", NEON_BLUE),
    ("06", "故事策略", "Strategy", CYAN),
    ("07", "故事内核", "Story", ELEC_PURPLE),
    ("08", "技法选择", "Technique", ORANGE),
    ("09", "大纲计划", "Plan", NEON_BLUE),
    ("10", "草稿生成", "Draft", CYAN),
    ("11", "反 AI 味", "Anti-AI", ELEC_PURPLE),
    ("12", "质量自检", "Quality", ORANGE),
    ("13", "反馈分类", "Feedback", NEON_BLUE),
    ("14", "演化循环", "Evolution", CYAN),
    ("15", "验证交付", "Validate", ELEC_PURPLE),
]

# 5 列 3 行
COLS = 5
ROWS = 3
CARD_W = 268
CARD_H = 200
GAP_X = 16
GAP_Y = 36
GRID_X0 = 50
GRID_Y0 = 200

# 卡片颜色组(用第 4 个元素)
def draw_card(x, y, w, h, num, zh, en, color):
    # 卡片底
    draw.rounded_rectangle([x, y, x+w, y+h], radius=14, fill=CARD_BG, outline=color, width=2)
    # 左上角序号徽章(圆形)
    draw.ellipse([x+12, y+12, x+68, y+68], fill=color)
    nw = measure(num, font_num)
    # 序号白色(数字)
    draw.text((x + 40 - nw//2, y + 18), num, font=font_num, fill=(20, 30, 50))
    # 中文名
    draw.text((x+14, y+90), zh, font=font_zh, fill=WHITE)
    # 英文名(等宽)
    draw.text((x+14, y+138), en, font=font_en, fill=GRAY)
    # 右下角小色块(装饰)
    draw.rectangle([x+w-12, y+h-12, x+w-4, y+h-4], fill=color)

for i, (num, zh, en, color) in enumerate(hooks):
    r, c = i // COLS, i % COLS
    x = GRID_X0 + c * (CARD_W + GAP_X)
    y = GRID_Y0 + r * (CARD_H + GAP_Y)
    draw_card(x, y, CARD_W, CARD_H, num, zh, en, color)

# 流程箭头(从 01→02→...→05,然后 05→06 是列间)
# 横向箭头(同行)
arrow_y_off = 100  # 卡片中心
for r in range(ROWS):
    for c in range(COLS - 1):
        i = r * COLS + c
        if i >= len(hooks) - 1:
            break
        x_start = GRID_X0 + c * (CARD_W + GAP_X) + CARD_W
        x_end = GRID_X0 + (c+1) * (CARD_W + GAP_X)
        y = GRID_Y0 + r * (CARD_H + GAP_Y) + arrow_y_off
        # 短横线
        draw.line([(x_start+2, y), (x_end-6, y)], fill=GRAY, width=2)
        # 箭头三角
        draw.polygon([(x_end-6, y-5), (x_end-6, y+5), (x_end, y)], fill=GRAY)

# 纵向下行箭头(每行末→下一行首)
for r in range(ROWS - 1):
    x = GRID_X0 + (COLS-1) * (CARD_W + GAP_X) + CARD_W // 2
    y_start = GRID_Y0 + r * (CARD_H + GAP_Y) + CARD_H
    y_end = GRID_Y0 + (r+1) * (CARD_H + GAP_Y) - 10
    draw.line([(x, y_start+2), (x, y_end)], fill=NEON_BLUE, width=3)
    draw.polygon([(x-6, y_end), (x+6, y_end), (x, y_end+10)], fill=NEON_BLUE)

# 顶部"起点"标记(01 卡片)
start_x = GRID_X0 - 25
start_y = GRID_Y0 + 100
draw.polygon([(start_x, start_y-15), (start_x, start_y+15), (start_x+18, start_y)], fill=ORANGE)
draw.text((start_x-90, start_y-14), "START", font=font_brand, fill=ORANGE)

# 底部"终点"标记(15 卡片右下)
end_x = GRID_X0 + (COLS-1) * (CARD_W + GAP_X) + CARD_W + 30
end_y = GRID_Y0 + (ROWS-1) * (CARD_H + GAP_Y) + 100
draw.polygon([(end_x-18, end_y-10), (end_x-18, end_y+10), (end_x, end_y)], fill=CYAN)
draw.text((end_x+8, end_y-14), "DONE", font=font_brand, fill=CYAN)

# 底部品牌
brand = "joeseesun/qiaomu-novel-generator"
bw = measure(brand, font_brand)
draw.text((W - bw - 40, H - 50), brand, font=font_brand, fill=NEON_BLUE)
draw.line([(W - bw - 50, H - 58), (W - 30, H - 58)], fill=NEON_BLUE, width=1)

# 关键标注(左下角注释)
note_lines = [
    "● 输入: 一句话灵感 / 类型 / 桥段 / 已有片段",
    "● 输出: 1800-4000 字低 AI 味钩子短篇",
    "● 检查点 9 项: 钩子 / 欲望 / 升级 / 对白 / 画面 / 反转 / 余味 / 开头 / 反 AI 味",
]
for i, line in enumerate(note_lines):
    draw.text((60, H - 130 + i * 28), line, font=font_brand, fill=GRAY)

# 保存
img = img.convert('RGB')
img.save(OUT, "JPEG", quality=92, optimize=True)
print(f"✅ PIL 兜底 15 Hooks 流程图: {OUT}")
print(f"   整体: {W}x{H}")
print(f"   卡片: 5×3 = 15 个")
print(f"   大小: {os.path.getsize(OUT)//1024} KB")
