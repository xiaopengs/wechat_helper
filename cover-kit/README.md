# cover-kit · 公众号封面固定版式「左文右图 · 火柴人讽刺画」

> 2026-09-20 定版。左文右图，右边是 1:1 正方形火柴人讽刺插画，铺满整个高度。
> 插画题材固定：讽刺「AI 替代人」（机器人干活、人类抱着纸箱离场）。

## 一句话

```bash
# 有底图：直接排版
python3 make_cover_satire.py --art 底图.png \
    --label 项目管理 \
    --title "一个内核，" "两个前门。" \
    --sub "Copilot Agent Runtime" "43 万行 TypeScript → 83 万行 Rust" \
    --footer "14.5 周 · 128 个 PR · 原地换芯" \
    --out cover_vN.png

# 没底图：自动生成讽刺画再排版
python3 make_cover_satire.py --gen --out cover_vN.png
```

## 固定版式（不要逐次试参数）

| 项 | 值 |
|---|---|
| 画布 | 1400 × 596 px（微信 2.35:1），纯白底 |
| 右侧插画 | 1:1 正方形，自动裁到内容边界后放大，**铺满整个高度**；位置 x=804–1400, y=0–596 |
| 右图标签 | 左下角橙底白字圆角签，默认「项目管理」，字号 28 |
| 左文 x0 | 88 |
| y=132 | 蓝色 52×8 短块 + 橙色 28×8 短块（品牌色节拍器） |
| y=166 / y=242 | 主标题两行，粗体 58 |
| y=344 / y=386 | 副标题两行，常规 26，灰 |
| y=468 | 橙色横线 220×4 |
| y=490 | 页脚小字，常规 23，极浅灰 |
| 配色 | ink `#22262B` / grey `#787E88` / faint `#969BA3` / blue `#1a73e8` / orange `#ff6b35` |

## 流程（6 步）

1. **底图**：`bash gen_cover_satire.sh out.png` 生成 1:1 讽刺画底图；已有底图优先复用，别重复生成。
2. **排版**：跑 `make_cover_satire.py`（参数见上）。
3. **判据**：脚本会打印「内容区 W×H → 正方形 Npx」。若 **内容高/宽 < 0.4**，说明主体画得太扁，在正方形里上下会空洞 → 重生成，prompt 里加
   `subjects drawn LARGE, fill the frame edge to edge with only a small even margin`。
4. **确认**：把封面发用户过目（QQ：复制成 preview-cover/card_1.png，跑
   `node ../../greenbook-creator/templates/_lib/send_qq.mjs --config preview-cover/config.json --only 1`）。
5. **推草稿**（换封面必须整篇重走，不能用 update_draft）：
   ```bash
   python3 ../wechat-draft-publish/wechat_api.py one_click_publish \
       --title "标题" --html_file 稿件.html --cover_image cover_vN.png
   ```
6. **核对**：`list_drafts` 最新一条的 `thumb_media_id` 必须等于本次 publish 返回的 `cover_media_id`；同一篇文章只应保留一条草稿。

## 坑（都踩过）

- **图里绝不写字**：MiniMax 中文渲染不可控，所有文字由 PIL 合成。
- **别用 `ImageChops.getbbox()` 裁边**：纸面浅灰噪点会让 bbox 变成整张图，插画看着就"变小了"。用 numpy 暗像素阈值（<200）+ 每行/列暗点数 >3。
- **`MINIMAX_API_KEY=$(...)` 别直接写在 exec 里**：会被空格吞并 bug 搞成语法错误，一律写进 `.sh` 再 `bash` 执行。
- **换封面别走 `update_draft`**：`draft/get` 返回的 `thumb_media_id` 是空串，会报 `invalid media_id`。
- **读微信响应**：`r.content.decode("utf-8")`，不要 `r.json()`（返回头无 charset，会按 ISO-8859-1 解码成乱码）。

## 文件

- `make_cover_satire.py` — 版式生成器（版式是常量，只换文案/底图）
- `gen_cover_satire.sh` — 讽刺画底图生成（MiniMax image-01，1:1，浅色白底）
