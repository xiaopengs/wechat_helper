#!/usr/bin/env python3
"""
微信公众号文章 HTML 生成器
将结构化文本转为公众号兼容的排版 HTML

模板特性：
- 内联样式，无 <style> 标签
- 观点块：橙色左边框 + 灰底
- 引用块：蓝色左边框 + 斜体
- 章节标题：蓝色左边框
- 数据卡片：三列/双列
- 图片占位：虚线框
- 互动引导框：蓝底居中
- 参考文献：极简左边框
"""

primary = "#1a73e8"
accent = "#ff6b35"
text_c = "#333333"
secondary = "#666666"
muted = "#999999"
bg_quote = "#f7f8fa"
bg_interact = "#e8f0fe"


# ---- 排版组件 ----

def divider():
    """章节分隔线"""
    return '''<section style="text-align:center;margin:24px 0;">
<span style="display:inline-block;width:36px;height:2px;background-color:#eeeeee;"></span>
</section>'''


def h2(heading):
    """章节标题（蓝色左边框）"""
    return f'''<section style="margin-top:36px;margin-bottom:18px;padding-left:12px;border-left:3px solid {primary};">
<span style="font-size:19px;font-weight:bold;color:{text_c};line-height:1.6;">{heading}</span>
</section>'''


def p(text, bottom=18):
    """正文段落"""
    return f'''<section style="margin-bottom:{bottom}px;">
<span style="font-size:16px;color:{text_c};line-height:1.85;letter-spacing:0.3px;">{text}</span>
</section>'''


def paras(*items):
    """合并多段为单 section(<br/><br/> 分隔,省 wrapper 字节) — build_fable5.py 紧凑版"""
    inner = '<br/><br/>'.join(items)
    return f'''<section style="margin-bottom:14px;">
<span style="font-size:15px;color:{text_c};line-height:1.85;letter-spacing:0.2px;">{inner}</span>
</section>'''


def p_small(text):
    """次要文字"""
    return f'''<section style="margin-bottom:12px;">
<span style="font-size:15px;color:{secondary};line-height:1.8;">{text}</span>
</section>'''


def quote_block(text):
    """引用/金句块（蓝色左边框 + 斜体 + 灰底）"""
    return f'''<section style="margin:20px 0;padding:16px 18px;background-color:{bg_quote};border-left:3px solid {primary};border-radius:0 6px 6px 0;">
<span style="font-size:15px;color:{text_c};line-height:1.8;font-style:italic;">{text}</span>
</section>'''


def opinion_block(text):
    """观点块（橙色左边框 + 灰底）"""
    return f'''<section style="margin:20px 0;padding:16px 18px;background-color:{bg_quote};border-left:3px solid {accent};border-radius:0 6px 6px 0;">
<span style="font-size:16px;color:{text_c};line-height:1.85;letter-spacing:0.3px;">{text}</span>
</section>'''


def ref_item(text):
    """参考文献条目（极简左边框）"""
    return f'''<section style="margin-bottom:8px;padding:6px 0 6px 12px;border-left:2px solid {primary};">
<span style="font-size:14px;color:{secondary};line-height:1.7;">{text}</span>
</section>'''


def divider_with_num(num):
    """章节分隔线 + 段落号(02d 格式:01/02/03) — fusion-article 实际版"""
    n = f'{num:02d}'
    return f'''<section style="text-align:center;margin:24px 0 14px 0;">
<span style="display:inline-block;vertical-align:middle;font-size:13px;color:{primary};letter-spacing:3px;margin-right:10px;">{n}</span>
<span style="display:inline-block;vertical-align:middle;width:42px;height:4px;background-color:{primary};border-radius:2px;"></span>
</section>'''


def img_section(src, caption):
    """实图 + 图注(图片宽度100%,图注12px灰色emoji开头)"""
    return f'''<section style="margin:20px 0;text-align:center;">
<img src="{src}" style="width:100%;border-radius:6px;"/>
<p style="font-size:12px;color:{muted};margin-top:6px;">{caption}</p>
</section>'''


def ref_line(text):
    """参考条目(单行 · 列表,灰色小字)"""
    return f'''<section style="margin-bottom:4px;"><span style="font-size:13px;color:{muted};line-height:1.7;">· {text}</span></section>'''


def ref_section_header():
    """参考文档区头(顶部浅灰分割线 + 小标签) — fusion-article 风格"""
    return f'''<section style="margin-top:22px;padding-top:10px;border-top:1px solid #eeeeee;"><span style="font-size:13px;color:{secondary};font-weight:bold;letter-spacing:1px;">参考文档</span></section>'''


def ref_item_dual(desc, url):
    """参考条目(描述 + 蓝色URL双行,左侧2px蓝竖条)"""
    return f'''<section style="margin-bottom:3px;padding:3px 0 3px 10px;border-left:2px solid {primary};font-size:12px;line-height:1.7;">
<span style="color:{secondary};">{desc} </span><a href="{url}" style="color:{primary};text-decoration:underline;word-break:break-all;">{url}</a></section>'''


def pre_block(code_text):
    """代码块(<pre>,浅灰底圆角,12px Menlo/Consolas)"""
    return f'''<section style="margin:10px 0;padding:10px 14px;background-color:{bg_quote};border-radius:6px;overflow-x:auto;">
<pre style="font-size:12px;color:{text_c};line-height:1.6;margin:0;font-family:Menlo,Consolas,monospace;">{code_text}</pre></section>'''


def bold_blue(text):
    """蓝色强调（术语/数据）"""
    return f'<strong style="color:{primary};">{text}</strong>'


def bold_orange(text):
    """橙色强调（关键词/判断）"""
    return f'<strong style="color:{accent};">{text}</strong>'


def code_inline(text):
    """内联代码"""
    return f'<span style="font-size:14px;color:{accent};background-color:{bg_quote};padding:2px 6px;border-radius:3px;">{text}</span>'


def subheading(text):
    """子标题"""
    return f'''<section style="margin-top:28px;margin-bottom:12px;">
<span style="font-size:17px;font-weight:bold;color:{text_c};line-height:1.6;">{text}</span>
</section>'''


def triple_data_card(n1, l1, n2, l2, n3, l3):
    """三列数据卡片"""
    return f'''<section style="margin:18px 0;text-align:center;">
<span style="display:inline-block;width:29%;padding:14px 4px;background-color:{bg_quote};border-radius:8px;margin:0 1%;vertical-align:top;">
<span style="font-size:24px;font-weight:bold;color:{primary};">{n1}</span><br/>
<span style="font-size:11px;color:{secondary};">{l1}</span>
</span>
<span style="display:inline-block;width:29%;padding:14px 4px;background-color:{bg_quote};border-radius:8px;margin:0 1%;vertical-align:top;">
<span style="font-size:24px;font-weight:bold;color:{primary};">{n2}</span><br/>
<span style="font-size:11px;color:{secondary};">{l2}</span>
</span>
<span style="display:inline-block;width:29%;padding:14px 4px;background-color:{bg_quote};border-radius:8px;margin:0 1%;vertical-align:top;">
<span style="font-size:24px;font-weight:bold;color:{primary};">{n3}</span><br/>
<span style="font-size:11px;color:{secondary};">{l3}</span>
</span>
</section>'''


def dual_data_card(n1, l1, n2, l2):
    """双列数据卡片"""
    return f'''<section style="margin:18px 0;text-align:center;">
<span style="display:inline-block;width:44%;padding:16px 8px;background-color:{bg_quote};border-radius:8px;margin:0 2%;vertical-align:top;">
<span style="font-size:28px;font-weight:bold;color:{primary};">{n1}</span><br/>
<span style="font-size:12px;color:{secondary};">{l1}</span>
</span>
<span style="display:inline-block;width:44%;padding:16px 8px;background-color:{bg_quote};border-radius:8px;margin:0 2%;vertical-align:top;">
<span style="font-size:28px;font-weight:bold;color:{primary};">{n2}</span><br/>
<span style="font-size:12px;color:{secondary};">{l2}</span>
</span>
</section>'''


def interaction_box(text):
    """互动引导框"""
    return f'''<section style="margin-top:36px;padding:20px;background-color:{bg_interact};border-radius:8px;text-align:center;">
<span style="font-size:16px;color:{primary};font-weight:bold;line-height:1.8;">{text}</span>
</section>'''


def image_placeholder(caption):
    """图片占位（虚线框）"""
    return f'''<section style="margin:25px 0;text-align:center;padding:40px 20px;background-color:{bg_quote};border-radius:6px;border:1px dashed #cccccc;">
<span style="font-size:14px;color:{muted};">📷 {caption}</span>
</section>'''


# ---- 构建函数 ----

def build_article(parts: list) -> str:
    """将所有部件拼接为完整 HTML 片段"""
    return '\n'.join(parts)


def validate(html: str, max_chars: int = 20000) -> bool:
    """检查是否超限"""
    if len(html) > max_chars:
        print(f"⚠️ 超出限制: {len(html)} > {max_chars}")
        return False
    print(f"✅ {len(html)} chars (limit {max_chars})")
    return True


# ---- 示例：快速生成 ----
if __name__ == '__main__':
    # 示例用法
    parts = [
        p('这是正文段落。'),
        opinion_block('这是重要观点。'),
        quote_block('这是引用或金句。'),
        h2('章节标题'),
        divider(),
        interaction_box('💬 互动引导语'),
        h2('参考文献'),
        ref_item('来源名称<br/><span style="font-size:12px;color:#999999;">domain.com/path</span>'),
    ]
    html = build_article(parts)
    print(html)
