# Pipeline — HTML + Playwright 完整出图流程

> **2026-06-19 新增**。把 SKILL.md "模式 B" 的 6 步流程展开成可执行 SOP,踩坑全记录。

## 为什么走这条路径

| 路径 | 优势 | 劣势 | 适用 |
|----|----|----|----|
| **AI 生图**(`gen_media.sh generate`) | 单页快、风格统一 | 多页 / 多代码块 / 中文段落 OOD、不可控 | 封面 / 单页插图 / 概念图 |
| **Gamma / Tome** | 自动渲染、自动布局 | 中文支持差、代码块丑、定制难 | 商业演示、内部汇报 |
| **HTML + Playwright** | 100% 精确、可复用、可批量改 | 需手写 HTML、需装 Playwright | **12 页技术拆解、代码密集型** |

**结论**:
- ≤6 张 → AI 生图走 `gen_media.sh` + `default/tech-dark/tech-light/cartographer` 风格
- 6-12 张 → HTML + Playwright(本文件)
- 复杂演示 → Gamma,但代码丑,慎用

## 完整 6 步流程

### Step 1: 复制模板

```bash
# 模板位置
TEMPLATE=/home/ubuntu/.openclaw/workspace/wechat_helper/greenbook-creator/references/cartographer-template

# 复制到工作目录
PROJECT=/home/ubuntu/.openclaw/workspace/<project-name>
cp -r $TEMPLATE $PROJECT
ls $PROJECT/
# → css/  index.html  _shoot.py  assets/ (空目录)
```

模板文件 56KB,无 screenshots(节省体积)。

### Step 2: 写 HTML

打开 `$PROJECT/index.html`,按"逐页细节"修改 12 个 `<section class="slide">` 的内容。

**核心约束**:
- ✅ **改 index.html 内容**(kicker / 标题 / 文案 / list / code)
- ✅ **改 cat-label / chip 文字**
- ✅ **改 big-num 数字**
- ❌ **不改 css/styles.css**(除非确实需要调整字号或颜色 token)
- ❌ **不增删 `.slide` 数量**(12 页固定)
- ❌ **不混用其他设计风格**

**关键 class 用法**:
```html
<!-- 封面 -->
<section class="slide slide--black slide--hero">

<!-- 普通内容页(3 块卡片均分) -->
<section class="slide">
  <div class="content content--spread">
    <div>
      <div class="kicker">第 02 章 · 痛点</div>
      <h2 class="h2">标题</h2>
      <p class="lead">引文</p>
    </div>
    <div class="stack-lg">
      <div class="block-black">...</div>
      <div class="block-black">...</div>
      <div class="block-black">...</div>
    </div>
  </div>
</section>
```

**内容密度自检**:每页 3-4 个 block / block 内 ≤ 6 行文案 / 字号 ≥ 18px / 不出现单字行

### Step 3: 截图

```bash
cd $PROJECT
python3 _shoot.py
# → screenshots/slide-01.png ~ slide-12.png
```

**`_shoot.py` 关键代码**(模板自带,通常不需要改):
```python
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

WIDTH, HEIGHT = 1080, 1440

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            executable_path="/home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome",
        )
        ctx = await browser.new_context(viewport={"width": WIDTH, "height": HEIGHT})
        page = await ctx.new_page()
        await page.goto(f"file://{Path('index.html').absolute()}")
        for i in range(12):
            await page.locator(".slide").nth(i).screenshot(path=f"screenshots/slide-{i+1:02d}.png")
        await browser.close()
```

### Step 4: 部署到公网(1Panel 静态站)

```bash
PROJECT_DIR=/home/ubuntu/1panel/www/sites/thinkspc.fun/index/<project-name>
sudo mkdir -p $PROJECT_DIR/screenshots

# ⚠️ 老文件是 root:root 644,cp -f 不能覆盖,必须 sudo
sudo cp -f $PROJECT/screenshots/slide-*.png $PROJECT_DIR/screenshots/
sudo chown -R root:root $PROJECT_DIR/screenshots/
sudo chmod 755 $PROJECT_DIR/screenshots/
sudo chmod 644 $PROJECT_DIR/screenshots/*.png
```

**nginx 配置**(`/etc/nginx/sites-available/thinkspc.fun`):
```
rewrite ^/static/<project-name>/?$ /static/<project-name>/index.html last;
rewrite ^/static(/.*)$ $1 break;  # 兜底,所有子目录走 break
```

**已有 `^/static(/.*)$ $1 break;` 兜底**就不用改 nginx,直接 cp 即可。

### Step 5: 验 200

```bash
# 用 GET,不要用 HEAD(nginx HEAD 走不同 rewrite 链,会假阴性)
for n in 01 02 03 04 05 06 07 08 09 10 11 12; do
  printf "slide-$n: "
  curl -s -o /dev/null -w 'HTTP %{http_code} | %{size_download} bytes\n' \
    "https://thinkspc.fun/static/<project-name>/screenshots/slide-$n.png"
done
```

期望:全部 `HTTP 200 | <100KB 左右>`。

### Step 6: 用公网 URL 发送

```html
<qqimg>https://thinkspc.fun/static/<project-name>/screenshots/slide-01.png</qqimg>
<qqimg>https://thinkspc.fun/static/<project-name>/screenshots/slide-02.png</qqimg>
...
```

**为什么必须用公网 URL**(base64 上传被 QQ 服务端拒):
- `<qqimg>` 标签走 `outbound.js:341` → plugin 自己读文件 → 转 base64 → `sendC2CImageMessage` → `uploadC2CMedia` POST `/v2/users/{openid}/files` 传 `file_data`
- QQ 服务端对 `file_data` 路径有白名单校验,直接报 "Image path must be inside QQ Bot media storage"
- plugin 代码 `api.js:399` 有 `body.url = url` 分支,QQ 服务端**自己 fetch** 公网 URL,绕开上传限制
- SKILL.md `qqbot-media` 写"支持 local path",**实测不行**,走 URL 最稳

## 故障排查(踩坑全记录)

### Q1: Playwright chromium 启动报 `libatk-1.0.so.0: cannot open shared object`

```bash
sudo apt install libatk1.0-0 libatk-bridge2.0-0 libcups2 libxcomposite1 libxdamage1 libatspi2.0-0
```

装完重新跑 `_shoot.py`。

**注意**:`playwright install` 后的 `DEPENDENCIES_VALIDATED` 标记不可信,**实测装了 lib 才能真跑**。

### Q2: `TargetClosedError: BrowserType.launch: Target page, context or browser has been closed`

症状:chromium 启动后立即崩。
排查:
```bash
# 检查 chromium 路径
ls -la /home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome

# 检查缺哪些 lib
ldd /home/ubuntu/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome 2>&1 | grep "not found"
```

### Q3: snap chromium 跑不起来

症状:`chrome: /lib/x86_64-linux-gnu/libm.so.6: version 'GLIBC_2.38' not found`
原因:snap chromium 149.0.7827.53 要求 GLIBC 2.38,但系统是 Ubuntu 22.04 的 GLIBC 2.35。
**解决**:**不要用 snap chromium**,只能用 Playwright 自带 chromium。

### Q4: 截图全黑

排查:
```bash
# 截图前是否等字体加载
await page.wait_for_timeout(800)

# viewport 是否正确
print(await page.viewport_size())  # 应该是 {'width': 1080, 'height': 1440}
```

### Q5: 单张 slide 截不全(底部截断)

症状:slide 总高度超过 1440px,被裁。
解决:
- 减少 stack 内 block 数量(3-4 个最合适)
- 缩小 padding(60 → 40)
- 缩小字号(Lead 32→28、Body 24→20)
- 用 `page.locator(".slide").screenshot()` 而不是 `page.screenshot(full_page=True)`,前者只截元素实际高度

### Q6: cp 报 `Permission denied`

症状:`cp -f screenshots/slide-01.png ...` 报 Permission denied
原因:1Panel 部署目录的文件是 root:root 644,ubuntu 用户没有写权限
**解决**:`sudo cp -f ...`,然后 `sudo chown -R root:root ... && sudo chmod 644 ...`

### Q7: curl 验 200 但 `<qqimg>` 发不出图

症状:`curl -sI` 返回 200 但图发不出去
原因:nginx 对 HEAD 请求的 rewrite 处理路径跟 GET 不一样
**解决**:验 200 用 GET(`curl -s`),不要用 HEAD(`curl -sI`)

### Q8: `<qqimg>` 发出去 QQ 显示 "Image path must be inside QQ Bot media storage"

症状:QQ 服务端拒收 base64 上传
**解决**:改用公网 URL 形式,见 Step 6

## 性能参考(VM-16-11 ubuntu)

- 12 张 1080×1440 PNG 截图耗时:**~15 秒**
- 文件大小:60-150KB / 张,12 张共 ~1.2 MB
- 部署 cp + chmod:< 5 秒
- curl 12 张验 200:< 10 秒
- 12 张 `<qqimg>` 发到 QQ:< 30 秒

总流程 ~1 分钟搞定 12 张图 + 发送。

## 反例(什么不能用这套)

- ❌ 单张海报 / 朋友圈图 / 表情包(用 AI 生图更合适)
- ❌ 商业演示 / Keynote / PPT(用 minimax-pptx)
- ❌ 视频内容(用 minimax-video 或 doubao-seedance)
- ❌ 需要复杂插画 / 3D 渲染的内容(HTML + CSS 表达不了)

## 关联资源

- 模板:`wechat_helper/greenbook-creator/references/cartographer-template/`
- 设计系统:`wechat_helper/greenbook-creator/references/style-cartographer.md`
- AI 生图风格:`wechat_helper/greenbook-creator/scripts/styles/cartographer.txt`
- 12 页骨架示例:OpenRouter × Coding Agents(`openrouter-cartographer/`)
- QQ Bot 发图踩坑:见 MEMORY.md "QQ Bot `<qqimg>` 发送图片踩坑" 章节
- Playwright 截图踩坑:见 MEMORY.md "12 页知识图解 HTML+Playwright 管线" 章节