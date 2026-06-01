#!/usr/bin/env python3
"""微信公众号草稿发布 API 脚本

使用方式：
  python wechat_api.py get_token --appid APPID --secret SECRET
  python wechat_api.py upload_content_image --token TOKEN --image IMAGE_PATH
  python wechat_api.py upload_cover --token TOKEN --image IMAGE_PATH
  python wechat_api.py create_draft --token TOKEN --title TITLE --content CONTENT --thumb_media_id ID
  python wechat_api.py publish_draft --token TOKEN --media_id MEDIA_ID
  python wechat_api.py check_publish --token TOKEN --publish_id PUBLISH_ID
  python wechat_api.py list_drafts --token TOKEN [--offset 0] [--count 20]
  python wechat_api.py get_draft --token TOKEN --media_id MEDIA_ID
  python wechat_api.py delete_draft --token TOKEN --media_id MEDIA_ID
  python wechat_api.py one_click_publish --title TITLE --html_file HTML_FILE --cover_image COVER_PATH [--appid APPID --secret SECRET]
"""

import argparse
import json
import os
import re
import sys
import time

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests==2.31.0", file=sys.stderr)
    sys.exit(1)

WECHAT_API_BASE = "https://api.weixin.qq.com"

# ============================================================
# 凭证安全加载（从 OpenClaw secrets 或环境变量）
# ============================================================

SECRETS_FILE = os.path.expanduser("~/.openclaw/wechat-secrets.json")


def load_credentials():
    """
    按优先级加载微信凭证：
    1. 环境变量 WECHAT_APPID / WECHAT_APPSECRET
    2. ~/.openclaw/wechat-secrets.json（OpenClaw secrets file provider）
    """
    appid = os.environ.get("WECHAT_APPID")
    secret = os.environ.get("WECHAT_APPSECRET")
    if appid and secret:
        return appid, secret

    if os.path.isfile(SECRETS_FILE):
        try:
            with open(SECRETS_FILE, "r") as f:
                data = json.load(f)
            appid = data.get("WECHAT_APPID") or data.get("appid")
            secret = data.get("WECHAT_APPSECRET") or data.get("appsecret")
            if appid and secret:
                return appid, secret
        except (json.JSONDecodeError, IOError):
            pass

    return None, None


# ============================================================
# Token 管理
# ============================================================

_token_cache = {}

def get_token(appid, secret):
    """获取 access_token"""
    url = f"{WECHAT_API_BASE}/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    if "access_token" not in data:
        print(json.dumps({"success": False, "error": data}, ensure_ascii=False))
        return None
    result = {
        "success": True,
        "access_token": data["access_token"],
        "expires_in": data.get("expires_in", 7200)
    }
    _token_cache["token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 7200) - 300
    return result


def get_cached_token():
    """获取缓存的 token（未过期）"""
    if "token" in _token_cache and time.time() < _token_cache.get("expires_at", 0):
        return _token_cache["token"]
    return None

# ============================================================
# 图片上传
# ============================================================

def upload_content_image(token, image_path):
    """上传正文图片，返回微信URL"""
    url = f"{WECHAT_API_BASE}/cgi-bin/media/uploadimg"
    params = {"access_token": token}
    if not os.path.exists(image_path):
        return {"success": False, "error": f"图片文件不存在: {image_path}"}
    with open(image_path, "rb") as f:
        files = {"media": (os.path.basename(image_path), f)}
        resp = requests.post(url, params=params, files=files, timeout=30)
    data = resp.json()
    if "url" not in data:
        return {"success": False, "error": data}
    return {"success": True, "url": data["url"]}


def upload_cover(token, image_path):
    """上传封面图，获取永久素材 media_id"""
    url = f"{WECHAT_API_BASE}/cgi-bin/material/add_material"
    params = {"access_token": token, "type": "image"}
    if not os.path.exists(image_path):
        return {"success": False, "error": f"图片文件不存在: {image_path}"}
    with open(image_path, "rb") as f:
        files = {"media": (os.path.basename(image_path), f)}
        resp = requests.post(url, params=params, files=files, timeout=30)
    data = resp.json()
    if "media_id" not in data:
        return {"success": False, "error": data}
    return {"success": True, "media_id": data["media_id"], "url": data.get("url", "")}

# ============================================================
# 草稿管理
# ============================================================

def create_draft(token, title, content, thumb_media_id, author="", digest="",
                 content_source_url="", need_open_comment=0, only_fans_can_comment=0,
                 show_cover_pic=1):
    """新增草稿"""
    url = f"{WECHAT_API_BASE}/cgi-bin/draft/add"
    params = {"access_token": token}
    article = {
        "article_type": "news",
        "title": title,
        "content": content,
        "thumb_media_id": thumb_media_id,
        "need_open_comment": need_open_comment,
        "only_fans_can_comment": only_fans_can_comment,
        "show_cover_pic": show_cover_pic
    }
    if author:
        article["author"] = author
    if digest:
        article["digest"] = digest
    if content_source_url:
        article["content_source_url"] = content_source_url

    body = {"articles": [article]}
    # 使用 ensure_ascii=False 避免中文被转义成 \uXXXX
    resp = requests.post(url, params=params, data=json.dumps(body, ensure_ascii=False).encode("utf-8"), 
                         headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30)
    data = resp.json()
    if "media_id" not in data:
        return {"success": False, "error": data}
    return {"success": True, "media_id": data["media_id"]}


def list_drafts(token, offset=0, count=20):
    """获取草稿列表"""
    url = f"{WECHAT_API_BASE}/cgi-bin/draft/batchget"
    params = {"access_token": token}
    body = {"offset": offset, "count": count, "no_content": 1}
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    if "item" not in data:
        return {"success": False, "error": data}
    return {"success": True, "total_count": data.get("total_count", 0), "item_count": data.get("item_count", 0), "items": data["item"]}


def get_draft(token, media_id):
    """获取草稿详情"""
    url = f"{WECHAT_API_BASE}/cgi-bin/draft/get"
    params = {"access_token": token}
    body = {"media_id": media_id}
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    if "news_item" not in data:
        return {"success": False, "error": data}
    return {"success": True, "news_item": data["news_item"]}


def delete_draft(token, media_id):
    """删除草稿"""
    url = f"{WECHAT_API_BASE}/cgi-bin/draft/delete"
    params = {"access_token": token}
    body = {"media_id": media_id}
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    return {"success": data.get("errcode", -1) == 0, "errmsg": data.get("errmsg", "")}


def update_draft(token, media_id, index, title, content, thumb_media_id, author="",
                 digest="", content_source_url=""):
    """更新草稿"""
    url = f"{WECHAT_API_BASE}/cgi-bin/draft/update"
    params = {"access_token": token}
    article = {
        "article_type": "news",
        "title": title,
        "content": content,
        "thumb_media_id": thumb_media_id
    }
    if author:
        article["author"] = author
    if digest:
        article["digest"] = digest
    if content_source_url:
        article["content_source_url"] = content_source_url

    body = {"media_id": media_id, "index": index, "articles": article}
    # 使用 ensure_ascii=False 避免中文被转义成 \uXXXX
    resp = requests.post(url, params=params, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                         headers={"Content-Type": "application/json; charset=utf-8"}, timeout=30)
    data = resp.json()
    return {"success": data.get("errcode", -1) == 0, "errmsg": data.get("errmsg", "")}

# ============================================================
# 发布管理
# ============================================================

def publish_draft(token, media_id):
    """发布草稿"""
    url = f"{WECHAT_API_BASE}/cgi-bin/freepublish/submit"
    params = {"access_token": token}
    body = {"media_id": media_id}
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    if data.get("errcode", 0) != 0:
        return {"success": False, "error": data}
    return {"success": True, "publish_id": data.get("publish_id", ""), "msg": data.get("errmsg", "")}


def check_publish(token, publish_id):
    """查询发布状态"""
    url = f"{WECHAT_API_BASE}/cgi-bin/freepublish/get"
    params = {"access_token": token}
    body = {"publish_id": publish_id}
    resp = requests.post(url, params=params, json=body, timeout=30)
    data = resp.json()
    return {"success": True, "data": data}

# ============================================================
# HTML 图片处理
# ============================================================

def replace_html_images(token, html_content, image_dir=None):
    """替换 HTML 中的外部图片 URL 为微信 URL

    扫描 HTML 中的 <img src="..."> 标签，上传本地图片到微信，替换为微信 URL。
    对于已存在的微信域名 URL（mmbiz.qpic.cn）跳过。
    """
    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
    matches = img_pattern.findall(html_content)

    url_mapping = {}
    for img_url in matches:
        # 跳过微信域名的图片
        if "mmbiz.qpic.cn" in img_url or "mmbiz.qlogo.cn" in img_url:
            continue

        # 尝试上传本地文件
        local_path = None
        if image_dir and not img_url.startswith(("http://", "https://")):
            local_path = os.path.join(image_dir, img_url)
        elif image_dir:
            # 从URL中提取文件名，尝试在本地目录找
            filename = img_url.split("/")[-1].split("?")[0]
            candidate = os.path.join(image_dir, filename)
            if os.path.exists(candidate):
                local_path = candidate

        if local_path and os.path.exists(local_path):
            result = upload_content_image(token, local_path)
            if result.get("success"):
                url_mapping[img_url] = result["url"]
                html_content = html_content.replace(img_url, result["url"])
                print(f"  上传成功: {os.path.basename(local_path)} -> {result['url'][:60]}...")
            else:
                print(f"  上传失败: {os.path.basename(local_path)} - {result.get('error')}", file=sys.stderr)

    return html_content, url_mapping

# ============================================================
# 一键发布
# ============================================================

def one_click_publish(appid, secret, title, html_file, cover_image, author="",
                      digest="", content_source_url=""):
    """一键发布：获取token → 上传图片 → 上传封面 → 创建草稿"""
    # Step 1: 获取 token
    print("Step 1: 获取 access_token...")
    token_result = get_token(appid, secret)
    if not token_result or not token_result.get("success"):
        return {"success": False, "error": "获取 token 失败", "detail": token_result}
    token = token_result["access_token"]
    print(f"  Token 获取成功，有效期 {token_result['expires_in']} 秒")

    # Step 2: 读取 HTML 并处理图片
    print("Step 2: 读取文章并上传正文图片...")
    if not os.path.exists(html_file):
        return {"success": False, "error": f"HTML 文件不存在: {html_file}"}
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    image_dir = os.path.dirname(html_file)
    html_content, url_mapping = replace_html_images(token, html_content, image_dir)
    if url_mapping:
        print(f"  共替换 {len(url_mapping)} 张正文图片")
    else:
        print("  未发现需要上传的正文图片")

    # Step 3: 上传封面图
    print("Step 3: 上传封面图...")
    if not os.path.exists(cover_image):
        return {"success": False, "error": f"封面图不存在: {cover_image}"}
    cover_result = upload_cover(token, cover_image)
    if not cover_result.get("success"):
        return {"success": False, "error": "封面图上传失败", "detail": cover_result}
    thumb_media_id = cover_result["media_id"]
    print(f"  封面图上传成功，media_id: {thumb_media_id}")

    # Step 4: 创建草稿
    print("Step 4: 创建草稿...")
    draft_result = create_draft(
        token=token,
        title=title,
        content=html_content,
        thumb_media_id=thumb_media_id,
        author=author,
        digest=digest,
        content_source_url=content_source_url
    )
    if not draft_result.get("success"):
        return {"success": False, "error": "草稿创建失败", "detail": draft_result}
    print(f"  草稿创建成功！media_id: {draft_result['media_id']}")

    return {
        "success": True,
        "draft_media_id": draft_result["media_id"],
        "cover_media_id": thumb_media_id,
        "image_mapping": url_mapping,
        "message": "草稿已创建，可在公众号后台草稿箱中查看"
    }

# ============================================================
# CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="微信公众号草稿发布工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 全局参数：凭证可从 secrets 自动加载
    parser.add_argument("--appid", default=None, help="公众号 AppID（可选，未提供则从 ~/.openclaw/wechat-secrets.json 读取）")
    parser.add_argument("--secret", default=None, help="公众号 AppSecret（可选，同 appid）")

    # get_token
    p = subparsers.add_parser("get_token", help="获取 access_token")

    # upload_content_image
    p = subparsers.add_parser("upload_content_image", help="上传正文图片")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--image", required=True, help="图片文件路径")

    # upload_cover
    p = subparsers.add_parser("upload_cover", help="上传封面图（永久素材）")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--image", required=True, help="封面图文件路径")

    # create_draft
    p = subparsers.add_parser("create_draft", help="创建草稿")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--title", required=True, help="文章标题")
    p.add_argument("--content", required=True, help="正文HTML内容")
    p.add_argument("--thumb_media_id", required=True, help="封面图素材ID")
    p.add_argument("--author", default="", help="作者")
    p.add_argument("--digest", default="", help="摘要")
    p.add_argument("--content_source_url", default="", help="原文链接")
    p.add_argument("--need_open_comment", type=int, default=0, help="是否打开评论 0/1")
    p.add_argument("--only_fans_can_comment", type=int, default=0, help="仅粉丝可评论 0/1")

    # publish_draft
    p = subparsers.add_parser("publish_draft", help="发布草稿")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--media_id", required=True, help="草稿 media_id")

    # check_publish
    p = subparsers.add_parser("check_publish", help="查询发布状态")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--publish_id", required=True, help="发布ID")

    # list_drafts
    p = subparsers.add_parser("list_drafts", help="获取草稿列表")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--offset", type=int, default=0, help="偏移量")
    p.add_argument("--count", type=int, default=20, help="数量")

    # get_draft
    p = subparsers.add_parser("get_draft", help="获取草稿详情")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--media_id", required=True, help="草稿 media_id")

    # delete_draft
    p = subparsers.add_parser("delete_draft", help="删除草稿")
    p.add_argument("--token", required=True, help="access_token")
    p.add_argument("--media_id", required=True, help="草稿 media_id")

    # one_click_publish
    p = subparsers.add_parser("one_click_publish", help="一键发布到草稿箱")
    p.add_argument("--title", required=True, help="文章标题")
    p.add_argument("--html_file", required=True, help="排版HTML文件路径")
    p.add_argument("--cover_image", required=True, help="封面图文件路径")
    p.add_argument("--author", default="", help="作者")
    p.add_argument("--digest", default="", help="摘要")
    p.add_argument("--content_source_url", default="", help="原文链接")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    # 自动加载凭证（优先级：命令行参数 > 环境变量 > secrets 文件）
    if not args.appid or not args.secret:
        auto_appid, auto_secret = load_credentials()
        if auto_appid and auto_secret:
            args.appid = args.appid or auto_appid
            args.secret = args.secret or auto_secret

    result = None

    if args.command == "get_token":
        result = get_token(args.appid, args.secret)
    elif args.command == "upload_content_image":
        result = upload_content_image(args.token, args.image)
    elif args.command == "upload_cover":
        result = upload_cover(args.token, args.image)
    elif args.command == "create_draft":
        result = create_draft(
            token=args.token, title=args.title, content=args.content,
            thumb_media_id=args.thumb_media_id, author=args.author,
            digest=args.digest, content_source_url=args.content_source_url,
            need_open_comment=args.need_open_comment,
            only_fans_can_comment=args.only_fans_can_comment
        )
    elif args.command == "publish_draft":
        result = publish_draft(args.token, args.media_id)
    elif args.command == "check_publish":
        result = check_publish(args.token, args.publish_id)
    elif args.command == "list_drafts":
        result = list_drafts(args.token, args.offset, args.count)
    elif args.command == "get_draft":
        result = get_draft(args.token, args.media_id)
    elif args.command == "delete_draft":
        result = delete_draft(args.token, args.media_id)
    elif args.command == "one_click_publish":
        result = one_click_publish(
            appid=args.appid, secret=args.secret, title=args.title,
            html_file=args.html_file, cover_image=args.cover_image,
            author=args.author, digest=args.digest,
            content_source_url=args.content_source_url
        )

    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
