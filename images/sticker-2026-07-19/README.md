# sticker-2026-07-19 — 愤怒猫猫日常（首个表情包样本）

> wechat-sticker-generator v1.0.3 首次实跑产物 / 2026-07-19 / provider=gpt-image-2

## 主题

「愤怒猫猫日常」——一只穿紫色卫衣的小白猫，每天都有值得愤怒的事。

## 内容

| 文件 / 目录 | 说明 |
|------|------|
| `base_reference.png` | 定妆图（白底、正面半身） |
| `params.json` | 完整生成参数，可复现 |
| `wechat_export/` | 微信合规导出包（240×240 GIF < 1MB） |
| `wechat_export/main/01-09.gif` | 9 张微信可直接上传的动态 GIF |
| `wechat_export/thumb/01-09.png` | 9 张缩略图（120×120 PNG） |
| `wechat_export/cover.png` | 表情专辑封面（240×240 PNG） |
| `wechat_export/icon.png` | 表情专辑头像（50×50 PNG） |
| `wechat_export/banner.png` | 表情专辑横幅（750×400） |
| `wechat_export/upload_info.txt` | 微信表情后台填单材料 |
| `export_gifs/origin/` | 切宫格后未抠图的 GIF（调试参考） |
| `export_gifs/nobg/` | 已抠图的 GIF（去背景透明） |

## 9 张动作 / 配文

| # | 动作 | 配文 |
|---|------|------|
| 01 | 双手叉腰，身体前倾，眉毛倒竖，眼神凶狠 | 气死了 |
| 02 | 右手握拳用力挥过头顶，左手攥紧卫衣下摆，跺脚 | 不干了 |
| 03 | 右手指向镜头前方，左手叉腰，嘴巴大张怒吼 | 就是你 |
| 04 | 双手抱胸侧身扭头，尾巴大幅甩动 | 哼 |
| 05 | 瞪大眼张大嘴往后仰，爪子举起贴脸 | 啊? |
| 06 | 俯身伸爪向前扑，头部压低锁定前方 | 冲鸭 |
| 07 | 侧身抬腿大步走，尾巴竖直甩动，嘴紧闭皱眉 | 走人 |
| 08 | 双手捂脸低头，耳朵向后压，尾巴下垂 | 心累 |
| 09 | 双手举过头顶欢呼跳起，嘴巴大张微笑，尾巴蓬松展开 | 耶! |

## 实跑参数

- **provider**: `gpt-image-2`（TokenRouter / image-provider-constraint 委派）
- **style_preset**: `2D_KAWAII`（萌系 Q 版）
- **scene_theme**: `COMPREHENSIVE`（综合）
- **mode**: `animated`（动态 GIF）
- **grid_size**: 9（每张 9 帧，3×3 宫格）
- **character_prompt**: 「白色短毛猫咪，紫罗兰色耳尖内侧偏粉，蓬松大尾巴，粉色腮红，宽大的紫色连帽卫衣，胸口有一枚白色小爪印，圆润大眼，水汪汪的紫色瞳孔，2D KAWAII 萌系Q版」

## 复现命令

```bash
# 在 wechat_helper/wechat-sticker-generator/ 目录下执行
TOKENROUTER_API_KEY=<你的 key> python3 sticker_utils.py draw_character \
  "白色短毛猫咪，紫罗兰色耳尖内侧偏粉，蓬松大尾巴，粉色腮红，宽大的紫色连帽卫衣，胸口有一枚白色小爪印，圆润大眼，水汪汪的紫色瞳孔，2D KAWAII 萌系Q版" \
  2D_KAWAII \
  /tmp/sticker_test/base_reference.png \
  --provider gpt-image-2

# 然后写 params.json，跑 build_prompts + batch_draw + process
# 详见 SKILL.md 第 5-7 步
```

## 已知短板

- 9 张之间角色有轻微漂移（耳尖色、爪印位置）—— gpt-image-2 /v1/images/generations 不支持原生参考图，依赖 prompt 文本控制
- 动作幅度被「不能出框」压扁，GIF 看起来偏静态 —— 想动作更戏剧性需改 Gemini provider
- 24 张微信专辑标准还差 15 张，下次接着跑