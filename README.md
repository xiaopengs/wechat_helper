# wechat_helper

> 微信公众号内容创作与分析工具集 — OpenClaw Skill

专注于公众号/视频号的全流程内容创作、爆款分析与优化。从选题→创作→审校→排版→发布，让 AI 贯穿每一个环节。

---

## 技能列表

### 🔥 wechat-explosive-analyzer

**公众号/视频号爆款内容六维审核分析器**

对公众号文章或视频号内容进行结构化审核，打分 + 诊断 + 可落地修改方案。

| 维度 | 权重 |
|------|------|
| 标题强度 | 30% |
| 开头钩子 | 20% |
| 选题切口 | 25% |
| 结构与节奏 | 15% |
| 社交货币 | 10% |
| 算法适配 | — |

**触发方式**：
- 提供公众号文章链接（`mp.weixin.qq.com`）
- 提供视频号链接（`weixin.qq.com/sph`）
- 直接粘贴文章草稿或视频脚本
- 要求对比两篇内容（已知爆款 vs 目标内容）

**输出**：爆款潜力判定 / 核心瓶颈 / 六维评分 / 可落地修改方案 / 选题替代方案

→ [查看详情](wechat-explosive-analyzer/)

---

### ✍️ wechat-creation

**公众号全流程创作技能（基于jerry公众号风格）**

从选题讨论→信息搜索→内容创作→三遍审校→爆款优化→配图标注→长文转X，覆盖公众号内容创作完整链路。

**核心能力**：
- 选题讨论：3-4个方向 + 大纲 + 优劣势分析
- 信息搜索：写前必搜，确保内容有据
- 内容创作：初稿撰写 + 三遍审校（基本错误→表达优化→风格检查）
- 爆款优化：5种爆文公式 + 完读率关键检查
- 配图标注：推荐5-8张配图位
- 长文转X：200-500字/1000字+两种格式

**触发方式**：
- 提供创作主题，进入选题讨论
- 提供已有草稿，进入审校优化
- 提供长文章，进入转X流程

**输出**：选题方向 / 初稿 / 审校稿 / 爆款优化稿 / 配图建议 / X平台版本

→ [查看详情](wechat-creation/)

---

### 📤 wechat-draft-publish

**公众号草稿发布技能**

将排版好的HTML文章一键发布到公众号草稿箱，支持封面图上传、正文图片上传、草稿创建、草稿发布全流程。

**核心能力**：
- Access Token 获取与管理
- 正文图片上传（外部URL→微信URL，避免被过滤）
- 封面图上传（获取永久素材 media_id）
- 一键发布：图片处理→封面上传→草稿创建，一步到位
- 草稿管理：查询/更新/删除草稿
- 发布管理：提交发布+状态查询

**使用方式**：
- 一键发布：提供HTML文件+封面图路径，自动完成全流程
- 分步执行：逐步上传图片→创建草稿→发布

**前置条件**：
- 已认证的服务号/订阅号（个人公众号无API权限）
- AppID + AppSecret
- 服务器IP白名单配置

→ [查看详情](wechat-draft-publish/)

---

## 安装方式

从本地安装 skill 文件：

```bash
clawhub install ./wechat-explosive-analyzer.skill
```

从 GitHub 安装：

```bash
clawhub install xiaopengs/agent-skills/wechat-explosive-analyzer
```

---

## 目录结构

```
wechat_helper/
├── wechat-explosive-analyzer/
│   ├── SKILL.md                          # 技能定义 + 工作流
│   └── references/
│       └── content-review-standards.md   # 六维审核标准原文
├── wechat-creation/
│   ├── SKILL.md                          # 创作技能定义 + 工作流
│   ├── assets/                           # jerry历史文章参考
│   └── references/
│       ├── style-guide.md                # 风格规范（10做+10不做）
│       └── templates.md                  # 各类模板
├── wechat-draft-publish/
│   ├── SKILL.md                          # 发布技能定义 + 工作流
│   ├── wechat_api.py                     # 微信API调用脚本
│   ├── wechat-api-reference.md           # API完整参考
│   └── wechat-layout-guide.md            # 排版兼容规范
└── README.md
```

---

## 持续更新

更多技能正在路上：
- 爆款标题批量生成器
- 选题热度追踪器
- 视频号脚本结构模板
- 小红书/微博爆款分析

欢迎 issue 提出需求或贡献 skill。
