#!/bin/bash
# =============================================
# 小绿书发布脚本 (Greenbook Publisher)
# 用于将配图打包上传至公众号素材库并创建草稿
# =============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WECHAT_API="$SKILL_DIR/../wechat-draft-publish/wechat_api.py"

echo "🟢 Greenbook Publisher"
echo "====================="

# 默认值
TITLE="${GREENBOOK_TITLE:-未命名小绿书}"
IMAGES_DIR="${GREENBOOK_IMAGES_DIR:-$SKILL_DIR/_drafts/images}"
COVER_INDEX="${GREENBOOK_COVER_INDEX:-0}"
DRY_RUN="${GREENBOOK_DRY_RUN:-false}"

# 帮助信息
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    echo ""
    echo "用法:"
    echo "  GREENBOOK_TITLE='标题' GREENBOOK_IMAGES_DIR=./images bash publish.sh"
    echo ""
    echo "环境变量:"
    echo "  GREENBOOK_TITLE        标题（必填）"
    echo "  GREENBOOK_IMAGES_DIR   图片目录（必填），按文件名排序"
    echo "  GREENBOOK_COVER_INDEX  封面图索引（默认 0 = 第一张）"
    echo "  GREENBOOK_DRY_RUN      试运行模式（默认 false）"
    exit 0
fi

# 验证
if [[ ! -d "$IMAGES_DIR" ]]; then
    echo "❌ 图片目录不存在: $IMAGES_DIR"
    exit 1
fi

IMAGE_COUNT=$(ls "$IMAGES_DIR"/*.{png,jpg,jpeg,webp} 2>/dev/null | wc -l)
if [[ "$IMAGE_COUNT" -lt 2 ]]; then
    echo "❌ 至少需要 2 张图片（含封面），当前: $IMAGE_COUNT"
    exit 1
fi

echo "📋 标题: $TITLE"
echo "🖼️  图片数量: $IMAGE_COUNT"
echo "📁 图片目录: $IMAGES_DIR"
echo ""

if [[ "$DRY_RUN" == "true" ]]; then
    echo "🔍 试运行模式 - 不实际发布"
    ls -la "$IMAGES_DIR"/*.{png,jpg,jpeg,webp} 2>/dev/null
    exit 0
fi

# TODO: 实际发布流程
# 1. 上传所有图片到公众号素材库
# 2. 创建图文消息草稿
# 3. 预览确认

echo "⚠️  发布 API 尚未集成，请手动在公众号后台操作:"
echo "   1. 进入 微信公众平台 → 图片/文字 → 新建"
echo "   2. 依次上传图片: $IMAGES_DIR"
echo "   3. 为每张图填写配文"
echo "   4. 预览 → 发布"
echo ""
echo "✅ 准备工作完成"
