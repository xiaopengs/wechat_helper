# Prompt 哲学:严守原意 vs 走 LLM 美化

> 来源:`image-provider-constraint` skill(2026-06-17 试用,功能等价 image-provider-constraint v1,内容融合 gpt-image-2 OpenAI 官方调用规范)
> 适用:`greenbook-creator` + `gen_media.sh` 生图流水线
> 决策原则:**当用户 prompt 越具体,wrapper 越不该动它**

---

## 核心立场

> **Prompt 是用户的资产,wrapper 是调用的脚手架。**
> wrapper 的职责是"忠实搬运 + 处理故障",不是"改写成更漂亮的样子"。

这一节吸收自 image-provider-constraint 的 Non-negotiable Rules(它严守这一条):

- 不扩展短 prompt
- 不"美化"用户原意
- 不注入额外主题/风格/情绪/构图/限制词
- 不为了"看起来更好"加修饰词
- 用户的具体程度就是 prompt 的具体程度,不要反推

---

## 何时用 `--from-article`(LLM 美化)

**当用户给的是素材,而不是 prompt**:
- 用户说:"帮我把这篇文章做成 5 张图"
- 用户丢了一个 markdown 进来,没写 prompt
- 用户说:"我想要一个 X 风格的封面,主题是 Y"

这种场景,LLM 把"用户意图"翻译成"模型可执行的 prompt",是有价值的。

**Gen-media 用法**:
```bash
gen_media.sh generate \
  --from-article /path/to/source.md \
  --image-desc "封面图:深色科技风,bash 提示符居中..." \
  --style tech-dark \
  --out cover.png
```

**但注意**:`--image-desc` 是用户**给 LLM 的指引**,不是 wrapper 给 LLM 的修饰 — 这个 `--image-desc` 必须由用户自己写,或者来自用户原文。

---

## 何时用 `--prompt`(严守原意)

**当用户给的是 prompt,不是素材**:
- 用户写了 5 段话描述他想要的画面
- 用户引用了别人写的 prompt(从设计系统 / reference 里抄的)
- 用户在 `references/style-ai-tech.md` 选了一个 `base_prompt`,改了 `content_block`,直接传过来

这种场景,**LLM 改写会破坏用户的精心设计**。

**Gen-media 用法**:
```bash
gen_media.sh generate \
  --prompt "用户原 prompt 全文,一字不动" \
  --style tech-dark \
  --out cover.png
```

**关键**:`--prompt` 和 `--from-article` **互斥**,不能同时用。脚本应该报错而不是默默把 `--prompt` 丢掉。

---

## 决策表

| 用户给的是 | 工具行为 | 命令 |
| :-- | :-- | :-- |
| 素材(文章/主题/方向) + 没写 prompt | LLM 翻译成 prompt(可加轻度风格修饰,但不要"美化") | `--from-article` |
| 完整 prompt(用户自己写的) | 一字不动传给模型 | `--prompt` |
| 半截 prompt(用户写了开头,让你补) | 提示用户补全,不要替用户补 | 报错或交互确认 |
| base_prompt + 替换 content_block | wrapper 严禁改 base_prompt | `--prompt` 直传 |
| 风格 / 配色明确写在 prompt 里 | wrapper 严禁再加 `--style` 修饰 | 直传,跳过 `--style` |

---

## 故障降级的"哲学一致"原则

> **降级时,宁可不修饰,也不要为了"看起来好"加东西。**

`gen_media.sh` 在以下场景降级到 PIL:
- TokenRouter 503(任何形式)
- Image Provider 不可用
- 余额不足

PIL 兜底生成的封面:
- ✅ 深色背景 + 主副标题(对齐规格)
- ✅ 品牌色高亮关键词
- ❌ **不**加额外装饰(锯齿/几何/同人插画风)以"显得不是 PIL"
- ❌ **不**替换标题文字以"显得更 AI 化"

降级产物是"最小可用",不是"伪装 AI 产物"。

---

## 实际案例:01 综述封面

`workflow 到 loop 拆解与实战 · 第 01 篇` 的封面生成踩了两次 tokenrouter 故障:

| 阶段 | 走法 | 结果 |
| :-- | :-- | :-- |
| 1. `gen_media.sh generate --prompt "..."` | 严守原意 | 503 (moderation 解析失败) |
| 2. `image-provider-constraint` 走 OpenAI 兼容 API | 严守原意 | 503 (channel routing 失败) |
| 3. PIL 兜底 `make_cover_agent_loop_01.py` | 最小可用 | ✅ 69KB,深色科技风,主副标题 |

**降级时没动过的内容**:
- 主标题:「从自研到大厂默认」(用户原文,8 字)
- 副标题:「workflow 到 loop 拆解与实战 · 第 01 篇」(系列前缀,不变)
- 配色:深蓝 #0a0e27 + 蓝 #1a73e8 + 橙 #ff6b35(系列统一色板)
- 视觉元素:中央 `$` + 闪烁光标 + 5 个智能体小圆(对应"5 种协调模式"线索)

**没有做**:
- 没把「从自研到大厂默认」改成更"AI 化"的标题
- 没加额外的同人插画/几何装饰
- 没为了"显得不土"换配色

---

## 跟现有规则的配合

| 现有规则 | 配合方式 |
| :-- | :-- |
| 规则 0:数据先行,官方源校验 | prompt 里的数字必须用户原文,不要 LLM 改写或"约/左右"模糊化 |
| 规则 1:每页一个信息原子 | base_prompt 里的 content_block 变量化,只换内容不换结构 |
| 规则 2:钩子前置 | prompt 第一句严格按用户原文,LLM 严禁"补"钩子 |
| 规则 3:Prompt 一致性 + 统一配色 | base_prompt 由用户维护,wrapper 严禁偷偷改 |

**新增规则 4(草案):Prompt 严守原意**
- 用户给 prompt,就走 `--prompt` 直传
- 用户给素材,就走 `--from-article` 翻译
- wrapper 严禁在两者之间"智能选择"
- 故障降级时,产物严守"最小可用"原则

---

## 为什么不直接装 image-provider-constraint

实测发现:
- 它跟我们的 `gen_media.sh` 功能高度重叠(都调 gpt-image-2)
- 它默认走 `api.openai.com/v1`,需要 OpenAI 官方 key(我们目前没有,只有 tokenrouter)
- 即便配上 tokenrouter 凭据,tokenrouter 自己的 moderation 503 故障还是会触发,**不解决问题**
- 它的"严守原意"哲学有价值,但**作为设计原则比作为 skill 装上更有用**

**结论**:
- ✅ 吸收它的 prompt 哲学到这份文档 + 我们的 SKILL.md
- ❌ 不装 skill(避免项目污染)
- ❌ 不改 `gen_media.sh` 强制走它(避免破坏现有生图流水线)
- ✅ 如果以后有 OpenAI 官方 key,可以用它的 `gpt_image_2.sh` 走官方 API(纯 shell + curl,跨平台)

---

## 自检清单(每次生图前)

- [ ] 用户给的是 prompt 还是素材?
- [ ] 如果是 prompt:走 `--prompt` 直传,一字不动
- [ ] 如果是素材:走 `--from-article`,`--image-desc` 必须是用户给的或用户原文
- [ ] base_prompt 是否由用户维护,wrapper 没有改过
- [ ] 配色 / 字号 / 布局在 prompt 里明确,wrapper 不要加 `--style` 修饰
- [ ] 数字在 prompt 里是原文(没"约/左右"模糊化)
- [ ] 故障降级时,产物严守"最小可用",不要"为了好看"加东西
