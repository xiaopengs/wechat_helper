#!/usr/bin/env python3
"""
renwei-writing 公众号封面图生成器
- 1200×500
- 深色科技感 + 红色"03:50 AM"印章 + 主副标题
- 主标题: 一个凌晨五点的失败,催生了一个改稿 skill
- 副标题: 人味儿写作心法 · renwei-writing 拆解
"""

from PIL import Image, ImageDraw, ImageFont
import math
import random

NOTO_CJK_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
NOTO_CJK_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


W, H = 1200, 500
img = Image.new("RGB", (W, H), (10, 20, 40))

# 对角线渐变
for y in range(H):
    for x in range(W):
        t = (x / W + y / H) / 2
        r = int(10 + (26 - 10) * t)
        g = int(20 + (40 - 20) * t)
        b = int(40 + (64 - 40) * t)
        img.putpixel((x, y), (r, g, b))

draw = ImageDraw.Draw(img, "RGBA")

# 浅蓝网格 50px
grid_color = (100, 160, 220, 30)
for x in range(0, W, 50):
    draw.line([(x, 0), (x, H)], fill=grid_color, width=1)
for y in range(0, H, 50):
    draw.line([(0, y), (W, y)], fill=grid_color, width=1)

# 随机小亮点
random.seed(42)
for _ in range(40):
    x = random.randint(0, W)
    y = random.randint(0, H)
    r = random.randint(1, 3)
    a = random.randint(60, 180)
    draw.ellipse([x-r, y-r, x+r, y+r], fill=(100, 200, 255, a))


def draw_rotated_rect(draw, center, size, angle, fill, outline, outline_w=4):
    cx, cy = center
    w, h = size
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    corners = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
    rotated = [(cx + x*cos_a - y*sin_a, cy + x*sin_a + y*cos_a) for x, y in corners]
    draw.polygon(rotated, fill=fill, outline=outline)
    return rotated


# 左侧印章: "03:50 AM"(凌晨五点的失败)
stamp_x, stamp_y = 200, 230
stamp_w, stamp_h = 240, 130
stamp_color = (220, 50, 50, 180)
draw_rotated_rect(draw, (stamp_x, stamp_y), (stamp_w, stamp_h), -7,
                  stamp_color, (255, 80, 80, 230), outline_w=5)

# 印章文字
font_stamp = get_font(NOTO_CJK_BOLD, 56)
stamp_text = "03:50 AM"
bbox = draw.textbbox((0, 0), stamp_text, font=font_stamp)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
draw.text((stamp_x - tw/2, stamp_y - th/2 - 12), stamp_text,
          font=font_stamp, fill=(255, 255, 255, 255))

# 印章下方小字
font_sub = get_font(NOTO_CJK_BOLD, 22)
sub_text = "凌晨五点 · 一次失败"
bbox = draw.textbbox((0, 0), sub_text, font=font_sub)
tw = bbox[2] - bbox[0]
draw.text((stamp_x - tw/2, stamp_y + 38), sub_text,
          font=font_sub, fill=(255, 220, 200, 220))


# 右侧主标题
# 第一行:"凌晨五点的失败"
font_t1 = get_font(NOTO_CJK_BOLD, 60)
t1 = "凌晨五点的失败"
draw.text((W - 680, 70), t1, font=font_t1, fill=(255, 255, 255, 255))

# 第二行:"催生了一个改稿 skill"
font_t2 = get_font(NOTO_CJK_BOLD, 56)
t2 = "催生了一个改稿 skill"
bbox = draw.textbbox((0, 0), t2, font=font_t2)
tw = bbox[2] - bbox[0]
draw.text((W - tw - 60, 140), t2, font=font_t2, fill=(255, 130, 100, 255))

# 副标题
font_sub2 = get_font(NOTO_CJK_BOLD, 26)
sub2 = "人味儿写作心法 · renwei-writing 项目拆解"
bbox = draw.textbbox((0, 0), sub2, font=font_sub2)
tw = bbox[2] - bbox[0]
draw.text((W - tw - 60, 235), sub2, font=font_sub2, fill=(180, 220, 255, 255))

# 装饰线
draw.line([(W - tw - 60, 282), (W - 60, 282)], fill=(255, 130, 100, 180), width=3)

# 描述行
font_desc = get_font(NOTO_CJK_REG, 22)
desc = "改稿时保住文字背后那个人的存在感"
bbox = draw.textbbox((0, 0), desc, font=font_desc)
tw = bbox[2] - bbox[0]
draw.text((W - tw - 60, 300), desc, font=font_desc, fill=(220, 230, 245, 230))


# 底部信息条
font_tag = get_font(NOTO_CJK_REG, 20)
tag_text = "项目拆解 · 三层结构 · 真实失败案例"
bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
tw = bbox[2] - bbox[0]
draw.text((W - tw - 60, 360), tag_text, font=font_tag, fill=(150, 180, 220, 200))

# 左下角:作者信息
font_byline = get_font(NOTO_CJK_REG, 20)
byline = "黑爪爪 · 整理"
draw.text((40, H - 50), byline, font=font_byline, fill=(120, 160, 200, 180))

# 右上角:日期
font_date = get_font(NOTO_CJK_REG, 20)
date_text = "2026.06.14"
bbox = draw.textbbox((0, 0), date_text, font=font_date)
tw = bbox[2] - bbox[0]
draw.text((W - tw - 40, H - 50), date_text, font=font_date, fill=(120, 160, 200, 180))


out = "/tmp/renwei_cover.jpg"
img.save(out, "JPEG", quality=88, optimize=True)
print(f"✅ 封面图: {out}")
print(f"   尺寸: {W}x{H}")
import os
print(f"   大小: {os.path.getsize(out)} bytes")