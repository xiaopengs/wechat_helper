---
name: wechat-draft-publish
description: 微信公众号草稿发布技能。将排版好的HTML文章一键发布到公众号草稿箱，支持封面图上传、正文图片上传、草稿创建、草稿发布全流程。当用户需要将文章发布到微信公众号草稿箱、创建公众号草稿、或完成"文章→草稿→发布"链路时使用。
dependency:
  python:
    - requests==2.31.0
---

# 微信公众号草稿发布技能

## 任务目标

本 Skill 用于：将排版好的公众号文章一键发布到微信草稿箱

能力包含：
- Access Token 获取与管理
- 正文图片上传（转微信可识别URL）
- 封面图上传（获取永久素材 media_id）
- 草稿创建
- 草稿发布（可选）
- 草稿管理（查询、删除）

触发条件：
- 用户要求将文章发布到公众号草稿箱
- 用户要求创建公众号草稿
- 用户提供了排版好的HTML文章和封面图，需要完成发布流程

## 前置准备

### 凭证配置

需要在 `./SECRET.md` 或环境变量中配置以下信息：
- **WECHAT_APPID**: 微信公众号开发者ID（AppID）
- **WECHAT_APPSECRET**: 微信公众号开发者密钥（AppSecret）

获取方式：
1. 登录微信公众平台 https://mp.weixin.qq.com
2. 进入「设置与开发」→「基本配置」
3. 获取 AppID 和 AppSecret

**重要限制**：
- 个人公众号没有接口权限，必须是已认证的服务号/订阅号
- 素材管理接口需要已认证的非个人公众号
- IP白名单需在公众平台后台配置

### 依赖说明
```
requests==2.31.0
```

## 🧾 推送前自检清单（jerry推文专用）

在调用 `create_draft` 之前，必须逐条确认：

- [ ] **正文不含标题** — 公众号自带标题，HTML 第一行直接是正文
- [ ] **无多余空白行** — 段落间距统一 18px，section 之间不叠加空 section
- [ ] **插图位简化** — 未上传实图时用 `（插图：xxx）` 一行，不做大框
- [ ] **无互动引导区** — 不出现"你怎么看"/"欢迎评论"
- [ ] **参考信息紧凑** — `·` 前缀小字灰，一行一条
- [ ] **分隔线用品牌色块** — `#1a73e8 4px`，不用 `#eeeeee 2px`
- [ ] **分隔处加段落号** — 蓝条下方 `01`−`06`
- [ ] **关键词着色正确** — 术语用蓝、强调用橙

参考排版模板详见 `wechat-layout-guide.md`。

## 完整发布流程

### Step 1: 获取 Access Token

```python
python scripts/wechat_api.py get_token
```

- 从凭证配置读取 AppID 和 AppSecret
- 调用微信接口获取 access_token
- Token 有效期 7200 秒，建议缓存复用
- 返回：`{"access_token": "xxx", "expires_in": 7200}`

### Step 2: 上传正文图片

```python
python scripts/wechat_api.py upload_content_image --token TOKEN --image IMAGE_PATH
```

- 将文章正文中的图片逐张上传到微信
- 使用 `/cgi-bin/media/uploadimg` 接口
- 返回的 URL 可在正文中使用（微信域名内有效）
- 图片限制：jpg/png格式，1MB以下
- 返回：`{"url": "http://mmbiz.qpic.cn/..."}`

**关键约束**：正文中的图片 URL 必须来自此接口，外部图片 URL 会被微信过滤！

### Step 3: 上传封面图

```python
python scripts/wechat_api.py upload_cover --token TOKEN --image IMAGE_PATH
```

- 使用 `/cgi-bin/material/add_material?type=image` 接口上传封面
- 获取永久素材 media_id（用于草稿创建）
- 图片限制：bmp/png/jpeg/jpg/gif，2MB以下
- 返回：`{"media_id": "xxx", "url": "http://..."}`

### Step 4: 替换正文图片URL

```python
python scripts/wechat_api.py replace_images --html HTML_FILE --mapping MAPPING_FILE
```

- 将正文中所有外部图片URL替换为微信返回的URL
- mapping 文件格式：`{"原始URL": "微信URL", ...}`
- 输出替换后的HTML文件

### Step 5: 创建草稿

```python
python scripts/wechat_api.py create_draft --token TOKEN --title TITLE --content CONTENT --thumb_media_id THUMB_MEDIA_ID [--author AUTHOR] [--digest DIGEST] [--content_source_url URL]
```

- 使用 `/cgi-bin/draft/add` 接口创建草稿
- 参数说明：
  - `title`: 文章标题（必填）
  - `content`: 正文HTML，必须少于2万字符，小于1MB（必填）
  - `thumb_media_id`: 封面图永久素材ID（必填）
  - `author`: 作者名（可选）
  - `digest`: 摘要，不填则取正文前54字（可选）
  - `content_source_url`: 原文链接/"阅读原文"URL（可选）
  - `need_open_comment`: 是否打开评论，0/1（可选，默认0）
  - `only_fans_can_comment`: 仅粉丝可评论，0/1（可选，默认0）
  - `show_cover_pic`: 是否显示封面，0/1（可选，默认1）
- 返回：`{"media_id": "草稿media_id"}`

### Step 6: 发布草稿（可选）

```python
python scripts/wechat_api.py publish_draft --token TOKEN --media_id MEDIA_ID
```

- 使用 `/cgi-bin/freepublish/submit` 接口
- 发布后会从草稿箱移除
- 发布需审核，审核通过才会正式上线
- 返回：`{"publish_id": "xxx"}`

### Step 7: 查询发布状态（可选）

```python
python scripts/wechat_api.py check_publish --token TOKEN --publish_id PUBLISH_ID
```

- 使用 `/cgi-bin/freepublish/get` 接口
- 返回发布状态和文章URL

## 一键发布流程

提供一键完成从图片上传到草稿创建的全流程：

```python
python scripts/wechat_api.py one_click_publish --title TITLE --html_file HTML_FILE --cover_image COVER_PATH [--author AUTHOR]
```

自动执行 Step 1-5，一步到位创建草稿。

## API接口参考

详细API文档见 [references/wechat-api-reference.md](references/wechat-api-reference.md)

## 草稿管理

### 获取草稿列表
```python
python scripts/wechat_api.py list_drafts --token TOKEN [--offset 0] [--count 20]
```

### 获取草稿详情
```python
python scripts/wechat_api.py get_draft --token TOKEN --media_id MEDIA_ID
```

### 删除草稿
```python
python scripts/wechat_api.py delete_draft --token TOKEN --media_id MEDIA_ID
```

### 更新草稿
```python
python scripts/wechat_api.py update_draft --token TOKEN --media_id MEDIA_ID --index 0 --title TITLE --content CONTENT --thumb_media_id THUMB_MEDIA_ID
```

## 注意事项

### 关键约束
1. **服务端调用**：所有接口必须在服务端调用，不可前端直接请求
2. **正文图片**：content 中的图片 URL 必须来自 uploadimg 接口，外部URL会被过滤
3. **封面图**：thumb_media_id 必须是永久素材ID，不是临时素材
4. **内容限制**：content 必须 < 2万字符、< 1MB，且会去除 JS
5. **字符编码**：title 和 author 传正常字符串，不要 Unicode 转义
6. **草稿生命周期**：发布后草稿会从草稿箱移除，不是永久存储
7. **账号类型**：必须是已认证的服务号/订阅号，个人公众号无接口权限
8. **IP白名单**：需在公众平台后台配置服务器IP

### 错误处理
- `40001`: access_token 无效或过期 → 重新获取
- `40007`: invalid media_id → 检查素材ID是否正确
- `45009`: 接口调用超过限制 → 等待后重试
- `48001`: api unauthorized → 检查公众号类型和权限

### Token管理建议
- Token 有效期 7200 秒（2小时）
- 建议缓存到文件，过期前复用
- 每日获取Token有次数限制（2000次），避免频繁刷新

## 资源索引

### 脚本文件
- [wechat_api.py](wechat_api.py): 微信公众号API调用脚本

### 参考文档
- [wechat-api-reference.md](wechat-api-reference.md): 微信公众号API完整参考
- [wechat-layout-guide.md](wechat-layout-guide.md): 微信公众号排版兼容规范（必读，避免样式被过滤）
- 微信官方文档: https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html
- MCP参考项目: https://github.com/kakaxi3019/wechat_oa_mcp

## 使用示例

### 示例1：一键发布HTML文章到草稿箱

```
用户：把这篇排版好的文章发布到公众号草稿箱
操作：
1. 确认文章HTML文件路径和封面图路径
2. 确认AppID和AppSecret已配置
3. 执行一键发布命令
4. 返回草稿media_id，告知用户可在公众号后台查看
```

### 示例2：分步执行（更灵活的控制）

```
用户：帮我把图片上传到微信，然后创建草稿
操作：
1. 获取access_token
2. 逐张上传正文图片，记录URL映射
3. 上传封面图，获取thumb_media_id
4. 替换正文中的图片URL
5. 创建草稿
6. 返回结果
```

### 示例3：发布已有草稿

```
用户：把草稿 media_id_xxx 发布出去
操作：
1. 获取access_token
2. 调用发布接口
3. 查询发布状态
4. 返回发布结果和文章URL
```
