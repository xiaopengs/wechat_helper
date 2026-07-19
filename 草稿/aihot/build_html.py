#!/usr/bin/env python3
"""
AI HOT conardli-skill-review 风格 → 微信公众号 inline-style HTML(v5)
- 自动 inline code:URL / API 路径 / 版本号 / 端口 等
- 表格识别:|...| → <table>(inline-style,无外 CSS)
- obj 标题双格式识别:### N. **X** 或 ### N. X 都行
- obj 内代码块识别:` ```...``` `
- 字符硬控 < 19000
"""

import re
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "aihot-skill-20260629-v1.md"
DST = HERE / "aihot-skill-20260629-v1.html"


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


CODE_STYLE = "font-family:monospace;background:#f7f8fa;padding:1px 4px;color:#1a1a1a;"
CODE_BLOCK_STYLE = "font-family:monospace;background:#f7f8fa;padding:8px 12px;display:block;color:#1a1a1a;line-height:1.7;white-space:pre-wrap;word-break:break-all;border-left:3px solid #1a73e8;"


def auto_inline_code(text: str) -> str:
    """自动把版本号包裹成反引号(URL 避免 auto wrap — Python re lookbehind 在边界有 bug)"""
    # 版本号 vX.Y.Z
    text = re.sub(
        r"\bv(\d+\.\d+(?:\.\d+)?)\b",
        r"`v\1`",
        text,
    )
    return text


def inline_format(text: str) -> str:
    text = esc(text)
    # 1) 先把没反引号的 URL / 路径 / 版本自动加反引号
    text = auto_inline_code(text)
    # 2) 反引号包裹 → inline code
    text = re.sub(
        r"`([^`]+)`",
        lambda m: f'<span style="{CODE_STYLE}">{m.group(1)}</span>',
        text,
    )
    # 3) 关键词着色
    text = re.sub(
        r"###([^#]+)###",
        r'<strong style="color:#1a73e8;">\1</strong>',
        text,
    )
    text = re.sub(
        r"\*\*\*([^*]+)\*\*\*",
        r'<strong style="color:#ff6b35;">\1</strong>',
        text,
    )
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        r'<strong style="color:#1a1a1a;">\1</strong>',
        text,
    )
    return text


PARA = '<section style="margin-bottom:18px;"><span style="font-size:16px;color:#333333;line-height:1.85;letter-spacing:0.3px;">{}</span></section>\n'
BULLET = '<section style="margin-bottom:14px;"><span style="font-size:15px;color:#333333;line-height:1.85;">{}</span></section>\n'
SMALL = '<section style="margin-bottom:8px;"><span style="font-size:13px;color:#999999;line-height:1.85;">{}</span></section>\n'


def section_break(num: str) -> str:
    return f'''<section style="text-align:center;margin:30px 0 14px 0;"><span style="display:inline-block;vertical-align:middle;font-size:13px;color:#1a73e8;letter-spacing:3px;margin-right:10px;font-weight:600;">{num}</span><span style="display:inline-block;vertical-align:middle;width:42px;height:3px;background-color:#1a73e8;border-radius:2px;"></span></section>
'''


def sub_section(title: str) -> str:
    return f'''<section style="margin-top:24px;margin-bottom:14px;padding-left:12px;border-left:3px solid #1a73e8;"><span style="font-size:18px;font-weight:bold;color:#333333;line-height:1.5;">{esc(title)}</span></section>
'''


def obj_block(parts):
    # 过滤空段和 '---' 分隔符
    parts = [p for p in parts if p and not p.strip().strip('-').strip() == '' and not p.strip() == '---']
    if not parts:
        return ''
    inner = '<br/><br/>'.join(parts)
    # 后处理:移除因 '---' 残留导致的孤儿 '<br/><br/>'
    while '<br/><br/>---<br/><br/>' in inner:
        inner = inner.replace('<br/><br/>---<br/><br/>', '<br/><br/>')
    inner = inner.replace('<br/>---<br/>', '<br/>')
    if inner.endswith('<br/>---'):
        inner = inner[:-len('<br/>---')]
    return PARA.format(inner)


def code_block(code: str) -> str:
    return f'<section style="margin:14px 0;overflow-x:auto;"><span style="{CODE_BLOCK_STYLE}">{esc(code)}</span></section>\n'


def bullet_list(items):
    chunks = []
    for item in items:
        chunks.append(f'· {inline_format(item)}')
    return BULLET.format('<br/>'.join(chunks))


def arrow_list(items):
    chunks = []
    for item in items:
        m = re.match(r"^(.*?)\s*(?:—|-|→)\s*(.+)$", item, flags=re.DOTALL)
        if m:
            prefix, body = m.group(1).strip(), m.group(2).strip()
            chunks.append(f'<strong style="color:#1a73e8;">▸ {esc(prefix)}</strong> {inline_format(body)}')
        else:
            chunks.append(f'<strong style="color:#1a73e8;">▸</strong> {inline_format(item)}')
    return BULLET.format('<br/>'.join(chunks))


def ref_list(items):
    chunks = [f'· {inline_format(it)}' for it in items]
    return SMALL.format('<br/>'.join(chunks))


def quote_block(text: str) -> str:
    return f'''<section style="margin:16px 0;padding:14px 18px;background-color:#f7f8fa;border-left:3px solid #1a73e8;border-radius:0 6px 6px 0;"><span style="font-size:15px;color:#333333;line-height:1.85;font-style:italic;">{esc(text)}</span></section>
'''


def tip_block(text: str) -> str:
    return f'''<section style="margin:16px 0;padding:14px 18px;background-color:#fef7e7;border-left:3px solid #f59e0b;border-radius:0 6px 6px 0;"><span style="font-size:15px;color:#333333;line-height:1.85;"><strong style="color:#f59e0b;">⚡ 提示</strong>{esc(text)}</span></section>
'''


def md_table_to_html(table_lines):
    """markdown 表格 → 微信 inline-style HTML table"""
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells)
    # 第 2 行通常是分隔行(---|---|---),过滤掉
    rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]

    if not rows:
        return ""

    head = rows[0]
    body = rows[1:]

    def td(content, header=False):
        style = "padding:6px 10px;border:1px solid #e5e7eb;font-size:14px;color:#333;line-height:1.6;"
        style += "background:#f7f8fa;font-weight:bold;" if header else ""
        return f'<td style="{style}">{inline_format(content)}</td>'

    head_row = (
        "<tr>" + "".join(td(c, header=True) for c in head) + "</tr>"
    )
    body_rows = "".join(
        "<tr>" + "".join(td(c) for c in r) + "</tr>" for r in body
    )

    return f'<section style="margin:14px 0;overflow-x:auto;"><table style="width:100%;border-collapse:collapse;"><thead>{head_row}</thead><tbody>{body_rows}</tbody></table></section>\n'


# =============================================================
# 解析 markdown
# =============================================================

md = SRC.read_text(encoding="utf-8")
md = re.sub(r"^# .+?\n", "", md, count=1, flags=re.MULTILINE)
md = re.sub(r"^> 项目拆解[^\n]*\n", "", md, count=1, flags=re.MULTILINE)
md = re.sub(r"^> 2026[^\n]*\n", "", md, count=1, flags=re.MULTILINE)

# 切到 block 级别
raw_blocks = re.split(r"\n\n+", md.strip())

out = []
out.append(section_break("00"))

# 当前 6 件套对象累积
cur_obj_parts = []
cur_obj_title = None

i = 0
while i < len(raw_blocks):
    blk = raw_blocks[i].strip()
    i += 1
    if not blk:
        continue

    # ---- ## N / 章节 ----
    m_section = re.match(r"^## (\d+)\s*/\s*(.+)$", blk)
    if m_section:
        if cur_obj_parts and cur_obj_title:
            out.append(sub_section(cur_obj_title))
            out.append(obj_block(cur_obj_parts))
            cur_obj_parts = []
            cur_obj_title = None

        num = m_section.group(1)
        title = m_section.group(2).strip()
        if 1 <= int(num) <= 5:
            out.append(section_break(num))
        out.append(sub_section(title))
        continue

    # ---- ### N. **X** 或 ### N. X 6 件套对象开始 ----
    m_obj_bold = re.match(r"^###\s*(\d+)\.\s*\*\*(.+)\*\*\s*$", blk, flags=re.DOTALL)
    m_obj_plain = re.match(r"^###\s*(\d+)\.\s*(.+?)\s*$", blk, flags=re.DOTALL)
    if m_obj_bold or m_obj_plain:
        m = m_obj_bold or m_obj_plain
        if cur_obj_parts and cur_obj_title:
            out.append(sub_section(cur_obj_title))
            out.append(obj_block(cur_obj_parts))

        cur_obj_title = f"{m.group(1)}. {m.group(2).strip().strip('*').strip()}"
        cur_obj_parts = []
        continue

    # ---- 处于 6 件套对象中 ----
    if cur_obj_title is not None:
        # 1) 代码块 ```...```
        if blk.startswith("```") and blk.endswith("```"):
            code = blk.strip("`").strip()
            cur_obj_parts.append(
                f'<span style="{CODE_BLOCK_STYLE}">{esc(code)}</span>'
            )
            continue

        # 2) **标题**:
        m_label = re.match(r"^\*\*([^*]+)\*\*\s*:\s*\n?(.+)$", blk, flags=re.DOTALL)
        if m_label:
            label = m_label.group(1).strip()
            content = m_label.group(2).strip()

            # 处理 bullet block(可能多个 bullet 行)
            lines = content.split("\n")
            bullet_items = []
            extra_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith("- ·") or line.startswith("·"):
                    item = line.lstrip("- ").lstrip("· ").strip()
                    bullet_items.append(item)
                elif line.startswith("-"):
                    bullet_items.append(line.lstrip("-").strip())
                elif line and not line.startswith("```"):
                    extra_lines.append(line)

            parts = [f'<strong>{esc(label)}</strong>']
            if bullet_items:
                parts.append('<br/>' + '<br/>'.join(f'· {inline_format(it)}' for it in bullet_items))
            for el in extra_lines:
                parts.append('<br/>' + inline_format(el))

            cur_obj_parts.append(''.join(parts))
            continue

        # 3) 默认 paragraph
        cur_obj_parts.append(inline_format(blk))
        continue

    # ---- ⚡ 提示 ----
    if blk.startswith("⚡"):
        out.append(tip_block(blk[1:].strip().lstrip("提示 ").strip()))
        continue

    # ---- (注意:) ----
    if blk.startswith("("):
        out.append(quote_block(blk.strip("()").strip()))
        continue

    # ---- `---` 分隔 ----
    if blk == "---":
        continue

    # ---- ▸ 决策项 ----
    lines = [l.strip() for l in blk.split("\n") if l.strip()]
    if lines and all(l.startswith("▸") for l in lines):
        items = [l[1:].strip() for l in lines]
        out.append(arrow_list(items))
        continue

    # ---- markdown 表格:多行都以 | 开头 ----
    if all(l.startswith("|") and l.endswith("|") for l in lines):
        out.append(md_table_to_html(lines))
        continue

    # ---- · bullet(支持混合 - · / - / ·) ----
    if all(l.startswith("·") or l.startswith("- ·") or l.startswith("-") for l in lines):
        items = []
        for l in lines:
            if l.startswith("- ·"):
                items.append(l[3:].strip())
            elif l.startswith("·"):
                items.append(l[1:].strip())
            elif l.startswith("-"):
                items.append(l[1:].strip())
        out.append(bullet_list(items))
        continue

    # ---- 默认 paragraph(全文自动 inline code 高亮) ----
    out.append(PARA.format(inline_format(blk)))


# 文件末尾 flush
if cur_obj_parts and cur_obj_title:
    out.append(sub_section(cur_obj_title))
    out.append(obj_block(cur_obj_parts))

final = ''.join(out)

# 字符硬控
if len(final) >= 20000:
    pass

DST.write_text(final, encoding="utf-8")

print(f"WROTE: {DST}")
print(f"BYTES: {DST.stat().st_size:,}")
print(f"CHARS: {len(final):,}")
print(f"< 20000 chars: {'✓' if len(final) < 20000 else '✗ TOO LONG'}")
print(f"< 1 MB       : {'✓' if DST.stat().st_size < 1024*1024 else '✗ TOO BIG'}")