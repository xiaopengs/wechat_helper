# renwei-writing 接入说明

> 2026-06-13 集成 — 把「人味改稿」作为 wechat_helper 标准流水线的可选步骤（默认开）

## 这是什么

[`renwei-writing/`](./renwei-writing/) 是从 [orange2ai/renwei-writing](https://github.com/orange2ai/renwei-writing) 同步来的 AI agent 写作心法 skill，作者橘子 (Orange) & Cola。

它的全部目的：**改完之后,那个人还在。**

## 在 wechat_helper 流水线里的位置

```
选题讨论 → 初稿写作 → [renwei 改稿] → 三遍审校 → 配图生成 → HTML排版 → 图片上传 → 草稿推送
                            ↑
                  本次集成的新步骤（可选·默认开）
```

| 节点 | 谁负责 | 备注 |
|---|---|---|
| 初稿 | 创作 skill (wechat-creation) | 黑爪爪/Jerry 写 |
| **renwei 改稿** | **renwei-writing skill** | **少动 / 逐处交代 / 作者可回滚** |
| 三遍审校 | 创作 skill | 基本错误 / 表达 / 风格 |

## 三件套约定

renwei 改稿只做三件事：

1. **位置** — 文字背后站着一个具体的人在具体位置说话
2. **代价** — 每个判断都是拿身体付过代价换来的
3. **手迹** — 句尾的「呢」「自己的」、忽长忽短的呼吸,是这个人说话的样子

## 七条改稿原则

1. **只做减法,少动** — 说不出来「原文这里真正打绊了」就不改
2. **毛边先假设是手迹,不是瑕疵** — 删之前问:删掉以后,说话的人还在吗?
3. **不写金句** — 改出对仗/漂亮比喻/「奢侈」「稀有」级词 = 警报
4. **拿不准就白描** — 原文是白描绝对不要往修辞加
5. **改完跑事后检查** — 扫动过的地方(只扫动过的),对照 post-edit-checklist
6. **逐处交代改动** — 拿不准的明确说「这处拿不准,可以还原」
7. **上限是隐形** — 不要追求「改得更好」,追求「清掉拌脚的,其他原样」

## 默认开启 vs opt-in

**默认开启**。理由：

- 原则是「少动」,默认跑也不会乱改
- 每处改动会交代理由,作者能逐处回滚
- 关闭只用在少数场景(Jerry 自己写完心满意足、纯公告、时间紧迫)

**关闭方式**：

- 明确说「跳过改稿」「这遍不要打磨」「原文不动」
- 在 brief 文件里写 `skip_renwei: true`
- 在 agent 调起 Step 7.5 时显式 `RENWEI=off`

## 失败案例(摘自 renwei-writing/references/case-study.md,2026-06-13 凌晨)

作者橘子写 ADHD 观察,AI 磨三遍后「漂亮了」但「人没了」:

| AI 改的 | 看起来 | 实际上 |
|---|---|---|
| 「细小琐碎的事情」→「一个小红点」 | 更有画面 | 换成了 AI 的画面,不是作者的 |
| 「拯救自己的前额叶呢」→「拯救它」 | 更干脆 | 「自己的」和「呢」里有叹气和自嘲,删掉后说话的人消失了 |
| 「是 A 和 B 的循环」→「刚集中,被叫走;刚散掉,又得集中」 | 更锋利 | 把观察者的冷静陈述改成了对仗表演 |
| 自行添加「一天下来…几百次」 | 更具体 | 编造了作者没说的数据 |

**最终被接受版本:只动 3 处,其余全部保留。**

## 文件结构

```
wechat_helper/
└── renwei-writing/
    ├── SKILL.md                          # 心法本体(原理)
    ├── references/
    │   ├── post-edit-checklist.md        # 事后检查清单(验收)
    │   └── case-study.md                 # 一次失败/成功对照
    ├── README.md
    ├── README.en.md
    └── LICENSE.md
```

## 同步上游

上游仓库: <https://github.com/orange2ai/renwei-writing>

```bash
cd wechat_helper/renwei-writing
git pull https://github.com/orange2ai/renwei-writing.git
```

注意：上游可能更新了原理或清单；同步后建议跑一次 case-study 验证流程,再 commit 到 wechat_helper。

## 许可

见 [`renwei-writing/LICENSE.md`](./renwei-writing/LICENSE.md)：开源与个人用途免费,闭源商业用途需商业授权。
