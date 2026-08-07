# P1-P8 配文模板 · 8 段

## P1 ｜封面
> {cover_hook}
**{name}** 拆给你看：{tagline_right}。
{license} · {version} · {stars_text}{footer_source}

## P2 ｜全局视角
> 一句话架构：{overview.title}
{overview.description} 主路径：{overview.key_path}。
共 6 个阶段，下滑逐节拆给你看。

## P3 ｜{section[1].title_en}
> {section[1].title_zh}
{section[1].bullets as 列表}。
{section[1].details}。

## P4 ｜{section[2].title_en}
> {section[2].title_zh}
{section[2].bullets as 列表}。
{section[2].details}。

## P5 ｜{section[3].title_en}
> {section[3].title_zh}
{section[3].bullets as 列表}。
{section[3].details}。

## P6 ｜{section[4].title_en}
> {section[4].title_zh}
{section[4].bullets as 列表}。
{section[4].details}。

## P7 ｜{section[5].title_en}
> {section[5].title_zh}
{section[5].bullets as 列表}。
{section[5].details}。

## P8 ｜{section[6].title_en} + 输出三件套
> {section[6].title_zh}
{section[6].bullets as 列表}。
{section[6].details}。
最终产出：**{output_trio[0].label}** / **{output_trio[1].label}** / **{output_trio[2].label}**。
{closing.one_liner}

---

## 公众号「图片·文字」首图说明（总导语）

你有没有遇到过：拿到一张架构图，让 AI 帮忙描述，结果输出到第 4 节就戛然而止，停在 "≥50 lines" 那里再也没下文？

**这不是 AI 的错。** 错在提示词：「用自由文本描述这张架构图」意味着模型必须一口气写完所有内容，token 超了就嘎断在中间，丢字了你也不知道丢了什么。

**这套模板的做法**：分节提取协议。
1. **Stage 1** — 枚举所有视觉区块（每项一行 JSON，~12 项）
2. **Stage 2** — 逐区块独立提取（每段 100-300 tokens，远低于模型上限）
3. **Stage 3** — 校验字段长度 / 数量，缺了只重跑那段

**结果**：永远不会被截断、永远知道哪一段没填满、可重试、可见即可复制。

下面 8 张图就是这套协议的产物。