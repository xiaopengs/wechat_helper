# repo-overview · 开源项目全景（1080×1440 × 6P）

复用 OpenWiki 案例沉淀的小绿书模板：把任意开源项目，按 **封面 / 痛点 / 优势 / 双模式 / 竞品 / 上手** 六页讲清楚，配套一条 300 字"勾引使用"的总导语和六条单图配文。

## 模板结构

```
templates/repo-overview/
├── README.md                  # 本文件，使用说明
├── generate.py                # 参数化 Pillow 生成脚本（数据驱动）
├── data/                      # 选题 / 数据配置（YAML）
│   ├── _schema.yaml           # 字段约定（占位符、取值范围）
│   ├── openwiki.yaml          # ✅ OpenWiki 示例（已验证可跑通）
│   └── …                      # 后续每个新项目一个 .yaml
└── prompts/                   # 文案 / AI 素材 prompt 模板
    ├── topic-intro.md         # 300 字公众号「图片·文字」总导语模板
    ├── captions.md            # P1–P6 单图配文模板（带变量）
    └── visual-prompt-cue.md   # 若改用 gen_media.sh/AI 生图时的视觉 prompt 提示
```

## 怎么用（一句话）

```bash
# 1. 复制示例数据
cp data/openwiki.yaml data/my-project.yaml
# 2. 编辑字段（必填项有 *）
# 3. 生成
python3 templates/repo-overview/generate.py --data templates/repo-overview/data/my-project.yaml --out output/my-project/
```

产物：

- `output/my-project/p1-cover.jpg ~ p6-howto.jpg`（1080×1440 单图）
- `output/my-project/contact-sheet.jpg`（6 宫格缩略图）
- `output/my-project/intro-and-captions.md`（按 `prompts/` 渲染的总导语 + 单图配文）

## 六页固定结构

| 页 | 标题（前定式） | 数据字段 | 视觉要素 |
|---|---|---|---|
| P1 | 封面 · `<NAME>` | `meta.*` + `cover.*` | 中央"百科"图标 + 4 个连接节点（AGENTS.md / CLAUDE.md / Git / CI） |
| P2 | 痛点 · 它解决的，不是「没文档」 | `pains[]` (3 条) | 3 张数字卡 + 一条左→中→右流水线箭头 |
| P3 | 优势 · 真正的护城河：不是生成，是维护 | `advantages[]` (4 条) + `pipeline[]` (4 阶段) | 4 段进度条 + 2×2 优势卡 + 暗色结论条 |
| P4 | 两种模式（默认叫「双模式」） | `modes[]` (2 条) | 左右双卡，每张含 icon + 4 条要点 |
| P5 | 竞品 · 别问谁最好，先看你要给谁写 | `comparisons[]` (3–4 条) | 4 张横长卡，按"给谁写"选型 |
| P6 | 上手 · N 条命令上手 | `quickstart[]` (4 条) + `tips[]` (3 条) + `risk` | 终端样式代码块 + 3 张建议卡 + 风险提示条 |

> 页数/页标题都是固定版式，便于读者形成「这是 repo-overview 系列」的认知。如果某个项目不适合双模式页（比如没有 Personal Mode），把第二张 mode 卡片改成「角色 / 集成」之类同结构的抽象就好。

## 颜色与字体

- **配色**：AI 科技蓝紫（`#4F6BFF → #7A4DFF`），是 skill 默认风格 `default` 的延伸；如果选题不适合蓝紫，跑前加 `--style orange-parenting` 或 `skill-review` 等其它预设（见 skill 的 `references/style-*.md`）。
- **字体**：`/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc` + `-Regular.ttc` + `NotoSansMonoCJK-Regular.ttc`（终端代码用）。
- **尺寸**：固定 1080×1440px（微信「图片·文字」轮播图最佳比例）。

## 数据 schema（精简版，详见 `_schema.yaml`）

```yaml
meta:                     # 项目元数据（封面用）
  name: OpenWiki
  kicker: 开源项目解读 · 2026.07
  stars_text: 12,309 Stars*
  version: v0.2.0
  license: MIT
  source: github.com/<owner>/<repo>

cover:                    # 封面自由字段
  tagline_left: 给 AI 编程助手
  tagline_right: 一份会自动更新的项目百科
  subline: LangChain 团队新开源：让仓库知识可读、可审、可持续更新
  central_nodes:           # 4 个连接在中心图标上的"出口"
    - { label: AGENTS.md,  sub: Agent 入口,    color: blue }
    - { label: CLAUDE.md,  sub: 上下文入口,   color: purple }
    - { label: Git / Diff, sub: 变化证据,     color: green }
    - { label: CI / PR,    sub: 持续维护,     color: orange }

pains:                    # 必填 3 条
  - { num: 01, title: 上下文碎片, desc: …, color: red }
  - { num: 02, title: 文档漂移,   desc: …, color: orange }
  - { num: 03, title: 重复交接,   desc: …, color: purple }

pipeline:                 # 4 阶段（必填，按顺序）
  - { num: 1, name: 读变化,   sub: status / log / diff,  color: blue }
  - { num: 2, name: 做综合,   sub: DeepAgents 工作流,    color: purple }
  - { num: 3, name: 写知识,   sub: Markdown + OKF,       color: cyan }
  - { num: 4, name: 提审查,   sub: CI 自动开 PR,        color: green }

advantages:               # 4 条"难被替代的细节"
  - { title: 本地 Markdown,    desc: 输出就在仓库里，能 diff、review、回滚,         color: blue }
  - { title: 保护人工内容,    desc: AGENTS.md / CLAUDE.md 只改自己的标记区块,       color: purple }
  - { title: 避免空转,        desc: 内容快照没变化，就不刷新更新时间元数据,         color: green }
  - { title: 跨 Git 平台,     desc: GitHub / GitLab / Bitbucket 流水线示例,         color: orange }

modes:                    # 2 条双模式（项目相关，可重命名 label）
  - { label: CODE MODE,    title: 项目知识库,
      icon: code,
      bullets: [输出：当前仓库 openwiki/, 输入：代码 + Git 变化证据, …],
      color: blue,  pale: pale_blue }
  - { label: PERSONAL MODE, title: 个人知识库,
      icon: brain,
      bullets: [输出：~/.openwiki/wiki/, 来源：Git、Gmail、Notion、Slack, …],
      color: purple, pale: pale_purple }
  shared_footer: Markdown + Google Open Knowledge Format（OKF）v0.1

comparisons:              # 3–4 个竞品（必须含本项目自己作对照）
  - { name: OpenWiki,         best_for: 给 Agent 写项目内 Wiki,
      features: 本地文件 · Git 可审查 · CI 维护,
      color: blue }
  - { name: DeepWiki,         best_for: 最快看懂陌生仓库, …
      color: purple }
  - { name: GitBook / Mintlify, best_for: 给客户与团队发布文档, …
      color: orange }
  - { name: Context7,         best_for: 给 Agent 查第三方库 API, …
      color: green }
  closing: 知识留在项目里，能和代码一起被审查与迭代

quickstart:               # 必填 3–4 条命令
  - { n: 01, cmd: npm install -g openwiki,         desc: 安装 CLI }
  - { n: 02, cmd: cd your-repo && openwiki --init, desc: 生成项目 Wiki }
  - { n: 03, cmd: openwiki --update,              desc: 按 Git 变化更新 }
  - { n: 04, cmd: openwiki personal --init,       desc: 可选：初始化个人 Wiki }

tips:                     # 3 条使用建议
  - { title: 先写边界,  desc: 在 openwiki/INSTRUCTIONS.md 写清范围与优先级, color: blue }
  - { title: PR 审核,   desc: 复制官方 workflow，让更新先开 PR，别直接自动合并, color: green }
  - { title: 看清成本,  desc: 生成质量取决于模型；敏感代码要核对提供商数据政策, color: orange }

risk:
  banner: 早期版本 v0.2.0｜匿名遥测默认开启，可手动关闭
  detail: 生成内容仍需人工审阅；敏感仓库先核对模型提供商的数据政策
```

## 校验清单（生成产物后跑一遍）

1. **尺寸合规**：每张都是 1080×1440px，单图 < 280KB，contact-sheet 缩略图清晰可读
2. **文字没被裁**：从 PDF 风格导出 → 边缘文字没被遮（生成器已留 60px 边距）
3. **数字对得上**：所有数字（Stars、版本、命令时长）都有官方源支撑
4. **没有 AI 腔**：不用「在当今 / 众所周知 / 赋能 / 打造」之类词
5. **配色统一**：6 页主色相同，仅用 4 个强调色（蓝 / 紫 / 绿 / 橘红）轮换
6. **总导语 ≤ 300 字**：公众号「图片·文字」首图说明的字数惯例
7. **footer 来源**：每张图都有官方 URL/文档，便于读者点开核对

## 维护要点

- **不要新建 Python 渲染器**：所有视觉细节都集中在 `generate.py`，新需求改这一份。
- **不要散落颜色常量**：颜色都集中在 `PALETTE` dict，想换配色统一改这里。
- **不要把生成产物 git 进去**：保持 `output/` 在 skill 的 `.gitignore` 内（成品走 `output/repo-overview/<project>/`，是用户的输出库）。
