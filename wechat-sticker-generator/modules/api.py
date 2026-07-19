import os
import sys
import json
import base64
from PIL import Image

from modules.config import load_config, get_api_key
from modules.constants import STYLE_MAPPING


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# gpt-image-2 provider
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 本机 ~/.openclaw/provider-auth.json 里的 tokenrouter key 不在
# gpt-image-2 的 group (返 503 No available channel ... default),
# 所以复用 image-provider-constraint skill 自带的独立 JUAPI 凭证。
# 那个 skill 里 config.json 的 base_url=https://www.tokenrouter.tech/v1,
# key 是 sk-TpPN... 那个,能进 gpt-image-2 group。
#
# 注意 1: 该 skill 自带的 shell wrapper (gpt_image_2.sh) 只解 b64_json,
# 但 tokenrouter 对 gpt-image-2 返 url (Amazon S3 预签名),所以我们不走它,
# 直接调 + 自己处理 url/b64_json 两种响应。
#
# 注意 2: gpt-image-2 的 generations 不支持原生参考图输入,
# 角色一致性靠 prompt 文本里的 character_prompt。
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_GPT_IMAGE_2_DEFAULT_BASE_URL = "https://www.tokenrouter.tech/v1"
_GPT_IMAGE_2_DEFAULT_MODEL = "gpt-image-2"
_GPT_IMAGE_2_SUPPORTED_SIZES = {"1024x1024", "1024x1536", "1536x1024", "auto"}
_IMAGE_PROVIDER_CONSTRAINT_CONFIG = os.path.expanduser(
    "~/.openclaw/workspace/skills/image-provider-constraint/config.json"
)


def _normalize_gpt_size(size):
    """把 '1024*1024' / '1024x1024' / 'auto' / None 统一成 gpt-image-2 支持的 size。"""
    if not size:
        return "1024x1024"
    s = str(size).strip().lower().replace("*", "x")
    return s if s in _GPT_IMAGE_2_SUPPORTED_SIZES else "1024x1024"


def _load_juapi_image_credentials():
    """从 image-provider-constraint skill 的 config.json 读 base_url + api_key。
    如果文件不在/字段缺,返回 (None, None)。
    """
    if not os.path.isfile(_IMAGE_PROVIDER_CONSTRAINT_CONFIG):
        return None, None
    try:
        with open(_IMAGE_PROVIDER_CONSTRAINT_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("base_url"), data.get("api_key")
    except Exception as e:
        print(f"[!] failed to read { _IMAGE_PROVIDER_CONSTRAINT_CONFIG}: {e}", file=sys.stderr)
        return None, None


def _gpt_image_2_request_json(endpoint, body, headers, timeout=180):
    """POST 一个 JSON body 到 gpt-image-2 端点, 返回 (img_bytes, err_str)。"""
    import requests

    try:
        resp = requests.post(endpoint, json=body, headers=headers, timeout=timeout)
    except requests.RequestException as e:
        return None, f"gpt-image-2 request failed: {e}"

    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}: {resp.text[:600]}"

    try:
        data = resp.json()
    except ValueError:
        return None, f"non-JSON response: {resp.text[:300]}"

    items = data.get("data") if isinstance(data, dict) else None
    if not items or not isinstance(items, list):
        return None, f"no 'data' array in response: {str(data)[:300]}"

    item = items[0]
    if not isinstance(item, dict):
        return None, f"unexpected data item: {str(item)[:200]}"

    # 优先用 b64_json(OpenAI 标准), 回退到 url(tokenrouter 代理返预签名 S3 URL)
    if "b64_json" in item and item["b64_json"]:
        try:
            return base64.b64decode(item["b64_json"]), None
        except Exception as e:
            return None, f"failed to decode b64_json: {e}"

    if "url" in item and item["url"]:
        try:
            r = requests.get(item["url"], timeout=60)
            r.raise_for_status()
            return r.content, None
        except Exception as e:
            return None, f"failed to download image from url: {e}"

    return None, f"no b64_json or url in data[0]: {str(item)[:200]}"


def _gpt_image_2_generate(
    prompt,
    output_image_path,
    api_key=None,
    model=None,
    api_base_url=None,
    size=None,
    reference_image_path=None,
    **_unused,
):
    """gpt-image-2 generate: POST /v1/images/generations。"""
    import requests

    if reference_image_path:
        print(
            f"[*] Note: gpt-image-2 /v1/images/generations 不支持原生参考图,"
            f"忽略 reference_image_path={reference_image_path}; 角色一致性靠 prompt 文本。",
            file=sys.stderr,
        )

    base_url, juapi_key = _load_juapi_image_credentials()
    base_url = api_base_url or base_url or _GPT_IMAGE_2_DEFAULT_BASE_URL
    api_key = api_key or juapi_key

    if not api_key:
        return False, (
            "gpt-image-2 缺凭据: 请设置 TOKENROUTER_API_KEY 环境变量, "
            f"或在 {_IMAGE_PROVIDER_CONSTRAINT_CONFIG} 填 api_key。"
        )

    model = model or _GPT_IMAGE_2_DEFAULT_MODEL
    size_str = _normalize_gpt_size(size)

    body = {
        "model": model,
        "prompt": prompt,
        "size": size_str,
        "n": 1,
        # 明确要 b64_json;某些代理不逼它会返 url
        "response_format": "b64_json",
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(
        f"[*] Generating image with gpt-image-2 "
        f"(model={model}, size={size_str}, endpoint={base_url}/images/generations)..."
    )

    img_bytes, err = _gpt_image_2_request_json(
        f"{base_url.rstrip('/')}/images/generations",
        body=body,
        headers=headers,
        timeout=180,
    )
    if err:
        return False, err

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_image_path)) or ".", exist_ok=True)
        with open(output_image_path, "wb") as f:
            f.write(img_bytes)
    except OSError as e:
        return False, f"failed to write image: {e}"

    print(f"[✓] Image saved: {output_image_path} ({len(img_bytes)} bytes)")
    return True, None


def _gpt_image_2_edit(
    prompt,
    output_image_path,
    reference_image_path,
    api_key=None,
    model=None,
    api_base_url=None,
    size=None,
):
    """gpt-image-2 edit: POST /v1/images/edits (multipart/form-data)。用于真人转 Q 版。"""
    import requests

    if not reference_image_path or not os.path.exists(reference_image_path):
        return False, f"reference_image not found: {reference_image_path}"

    base_url, juapi_key = _load_juapi_image_credentials()
    base_url = api_base_url or base_url or _GPT_IMAGE_2_DEFAULT_BASE_URL
    api_key = api_key or juapi_key

    if not api_key:
        return False, (
            "gpt-image-2 缺凭据: 请设置 TOKENROUTER_API_KEY 环境变量, "
            f"或在 {_IMAGE_PROVIDER_CONSTRAINT_CONFIG} 填 api_key。"
        )

    model = model or _GPT_IMAGE_2_DEFAULT_MODEL
    size_str = _normalize_gpt_size(size)

    headers = {"Authorization": f"Bearer {api_key}"}

    print(
        f"[*] Editing image with gpt-image-2 "
        f"(model={model}, size={size_str}, src={reference_image_path})..."
    )

    try:
        with open(reference_image_path, "rb") as f:
            src_bytes = f.read()
        files = {
            "image": (os.path.basename(reference_image_path), src_bytes, "image/png"),
        }
        form = {
            "model": model,
            "prompt": prompt,
            "size": size_str,
            "n": 1,
            "response_format": "b64_json",
        }
        resp = requests.post(
            f"{base_url.rstrip('/')}/images/edits",
            headers=headers,
            files=files,
            data=form,
            timeout=180,
        )
    except requests.RequestException as e:
        return False, f"gpt-image-2 edit request failed: {e}"

    if resp.status_code != 200:
        return False, f"HTTP {resp.status_code}: {resp.text[:600]}"

    try:
        body = resp.json()
    except ValueError:
        return False, f"non-JSON response: {resp.text[:300]}"

    items = body.get("data") if isinstance(body, dict) else None
    if not items:
        return False, f"no 'data' array in edit response: {str(body)[:300]}"

    item = items[0]
    if "b64_json" in item and item["b64_json"]:
        try:
            img_bytes = base64.b64decode(item["b64_json"])
        except Exception as e:
            return False, f"failed to decode b64_json: {e}"
    elif "url" in item and item["url"]:
        try:
            r = requests.get(item["url"], timeout=60)
            r.raise_for_status()
            img_bytes = r.content
        except Exception as e:
            return False, f"failed to download edit image from url: {e}"
    else:
        return False, f"no b64_json or url in edit data[0]: {str(item)[:200]}"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_image_path)) or ".", exist_ok=True)
        with open(output_image_path, "wb") as f:
            f.write(img_bytes)
    except OSError as e:
        return False, f"failed to write image: {e}"

    print(f"[✓] Edited image saved: {output_image_path} ({len(img_bytes)} bytes)")
    return True, None


def _gemini_generate_image(
    prompt,
    output_image_path,
    reference_image_path=None,
    api_key=None,
    model=None,
    size=None,
):
    """调用 Gemini API 生成图像"""
    print(f"[*] Generating image with Gemini...")

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print(
            "Error: google-genai not installed. Run: pip install google-genai",
            file=sys.stderr,
        )
        return False

    try:
        client = genai.Client(api_key=api_key)

        if reference_image_path and os.path.exists(reference_image_path):
            with open(reference_image_path, "rb") as f:
                image_data = f.read()

            import imghdr

            img_type = imghdr.what(reference_image_path)
            mime_type = f"image/{img_type}" if img_type else "image/jpeg"

            contents = [
                types.Part.from_bytes(data=image_data, mime_type=mime_type),
                prompt,
            ]
        else:
            contents = prompt

        image_config = None
        if size and "*" in size:
            w, h = map(int, size.split("*"))
            if w > h:
                image_config = types.ImageConfig(aspect_ratio="16:9")
            elif h > w:
                image_config = types.ImageConfig(aspect_ratio="9:16")
            else:
                image_config = types.ImageConfig(aspect_ratio="1:1")

        config = types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
        if image_config:
            config = types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"], image_config=image_config
            )

        response = client.models.generate_content(
            model=model or "gemini-2.5-flash-image",
            contents=contents,
            config=config,
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data
                with open(output_image_path, "wb") as f:
                    f.write(image_data)
                print(f"[✓] Image saved: {output_image_path}")
                return True

        print("Error: No image in response", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        return False


def _qwen_wanx_generate(
    prompt, output_image_path, model=None, api_base_url=None, api_key=None, size=None
):
    """wanx 系列模型的图像生成（使用 ImageSynthesis API）"""
    import dashscope
    import json
    import requests

    if api_key:
        dashscope.api_key = api_key
    if api_base_url:
        dashscope.base_url = api_base_url

    normalized_model = (model or "wan2.6-t2i").strip().lower()

    try:
        if normalized_model.startswith("wan2."):
            from dashscope.aigc.image_generation import ImageGeneration
            from dashscope.api_entities.dashscope_response import Message

            message = Message(role="user", content=[{"text": prompt}])
            response = ImageGeneration.call(
                model=model or "wan2.6-t2i",
                api_key=api_key,
                messages=[message],
                negative_prompt="",
                prompt_extend=True,
                watermark=False,
                n=1,
                size=size or "1024*1024",
            )

            if response.status_code == 200:
                resp_dict = json.loads(str(response))
                content = (
                    resp_dict.get("output", {})
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", [])
                )
                for item in content:
                    image_url = item.get("image")
                    if image_url:
                        img_response = requests.get(image_url)
                        if img_response.status_code == 200:
                            with open(output_image_path, "wb") as f:
                                f.write(img_response.content)
                            print(f"[✓] Image saved: {output_image_path}")
                            return True
        else:
            from dashscope import ImageSynthesis

            response = ImageSynthesis.call(
                model=model or "wan2.6-t2i",
                prompt=prompt,
                n=1,
                size=size or "1024*1024",
            )

            if response.status_code == 200 and response.output and response.output.results:
                image_url = response.output.results[0].url
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    with open(output_image_path, "wb") as f:
                        f.write(img_response.content)
                    print(f"[✓] Image saved: {output_image_path}")
                    return True
        print(f"Error from Qwen API: {response.message}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        return False


def _qwen_image_generate(
    prompt,
    output_image_path,
    model=None,
    api_base_url=None,
    reference_image_path=None,
    api_key=None,
    size=None,
):
    """qwen-image 系列模型的图像生成（使用 MultiModalConversation API）"""
    import dashscope
    from dashscope import MultiModalConversation

    if api_key:
        dashscope.api_key = api_key
    if api_base_url:
        dashscope.base_http_api_url = api_base_url
    else:
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"

    try:
        content = [{"text": prompt}]

        if reference_image_path and os.path.exists(reference_image_path):
            with open(reference_image_path, "rb") as f:
                image_data = f.read()
            import imghdr

            img_type = imghdr.what(reference_image_path) or "png"
            content.insert(
                0,
                {
                    "image": f"data:image/{img_type};base64,{base64.b64encode(image_data).decode('utf-8')}"
                },
            )

        messages = [{"role": "user", "content": content}]

        response = MultiModalConversation.call(
            model=model or "qwen-image-2.0-pro",
            messages=messages,
            stream=False,
            watermark=False,
            prompt_extend=True,
            negative_prompt="透明格子背景，伪透明背景，噪点，杂质，杂色，颗粒感，地面阴影，投影，光影伪造，边框，网格线，白色边框，黑色边框，分割线，画框，低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有 AI 感，构图混乱，文字模糊，扭曲，背景污染，渐变背景，花纹背景，阴影效果，发光效果",
            size=size or "1024*1024",
        )

        if response.status_code == 200:
            resp_dict = json.loads(str(response))
            if (
                resp_dict.get("output")
                and resp_dict["output"].get("choices")
                and resp_dict["output"]["choices"][0].get("message")
            ):
                message = resp_dict["output"]["choices"][0]["message"]
                if message.get("content"):
                    for item in message["content"]:
                        if item.get("image"):
                            image_url = item["image"]
                            import requests

                            img_response = requests.get(image_url)
                            if img_response.status_code == 200:
                                with open(output_image_path, "wb") as f:
                                    f.write(img_response.content)
                                print(f"[✓] Image saved: {output_image_path}")
                                return True
                            else:
                                print(
                                    f"Error downloading image: {img_response.status_code}",
                                    file=sys.stderr,
                                )
                                return False
            print("Error: No image in response", file=sys.stderr)
            return False
        else:
            print(
                f"Error from Qwen API: HTTP {response.status_code} - {response.message}",
                file=sys.stderr,
            )
            return False
    except Exception as e:
        print(f"Error generating image: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return False


def _qwen_generate_image(
    prompt,
    output_image_path,
    reference_image_path=None,
    api_key=None,
    model=None,
    api_base_url=None,
    size=None,
):
    """调用千问 API 生成图像"""
    print(f"[*] Generating image with Qwen (model: {model})...")

    try:
        import dashscope
    except ImportError:
        print(
            "Error: dashscope not installed. Run: pip install dashscope",
            file=sys.stderr,
        )
        return False

    dashscope.api_key = api_key
    normalized_model = (model or "").strip().lower()
    is_wanx_model = normalized_model.startswith("wan")

    if is_wanx_model:
        return _qwen_wanx_generate(
            prompt, output_image_path, model, api_base_url, api_key, size
        )
    else:
        return _qwen_image_generate(
            prompt,
            output_image_path,
            model,
            api_base_url,
            reference_image_path,
            api_key,
            size,
        )


def generate_image(
    prompt, output_image_path, reference_image_path=None, provider=None, size=None
):
    """调用图片生成 API 生成图像，支持 Gemini 和 千问（直接传入 prompt 字符串）"""
    config = load_config()

    if not provider:
        provider = config.get("default_provider", "gemini")

    provider_config = config["providers"].get(provider, {})
    api_key = provider_config.get("api_key")

    if not api_key:
        if provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
        elif provider == "qwen":
            api_key = os.environ.get("DASHSCOPE_API_KEY")
        elif provider == "gpt-image-2":
            api_key = os.environ.get("TOKENROUTER_API_KEY") or os.environ.get(
                "OPENAI_API_KEY"
            )

        if not api_key:
            api_key, provider = get_api_key()
            if not api_key:
                return False

    print(f"=== Image Generation ({provider.upper()}) ===")
    print(f"[*] Output path: {output_image_path}")
    if reference_image_path:
        print(f"[*] Reference image: {reference_image_path}")

    model = provider_config.get("model")
    if not model:
        if provider == "gemini":
            model = "gemini-3.1-flash-image-preview"
        elif provider == "qwen":
            model = "qwen-image-2.0-pro"
        elif provider == "gpt-image-2":
            model = "gpt-image-2"
        else:
            model = "gpt-image-2"
    api_base_url = provider_config.get("api_base_url", "")

    print(f"[*] Using model: {model}")
    if size:
        print(f"[*] Image size: {size}")

    if provider == "gpt-image-2":
        ok, err = _gpt_image_2_generate(
            prompt=prompt,
            output_image_path=output_image_path,
            api_key=api_key,
            model=model,
            api_base_url=api_base_url,
            size=size,
            reference_image_path=reference_image_path,
        )
        if not ok:
            print(f"Error generating image: {err}", file=sys.stderr)
        return ok

    if provider == "qwen":
        return _qwen_generate_image(
            prompt,
            output_image_path,
            reference_image_path,
            api_key,
            model,
            api_base_url,
            size,
        )
    else:
        return _gemini_generate_image(
            prompt, output_image_path, reference_image_path, api_key, model, size
        )


def remote_draw_trigger(
    prompt_path, output_image_path, reference_image_path=None, provider=None, size=None
):
    """调用图片生成 API 生成图像（从文件读取 prompt）"""
    print(f"[*] Reading prompt: {prompt_path}")
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt = f.read()
    return generate_image(
        prompt, output_image_path, reference_image_path, provider, size
    )


def _process_reference_image(image_data, output_path, target_size=512):
    """后处理 reference image：缩放到标准尺寸（512x512）"""
    try:
        from io import BytesIO

        img = Image.open(BytesIO(image_data))

        if img.mode != "RGB":
            img = img.convert("RGB")

        width, height = img.size
        print(f"[*] Generated image size: {width}x{height}")

        if width != height:
            min_dim = min(width, height)
            left = (width - min_dim) // 2
            upper = (height - min_dim) // 2
            right = left + min_dim
            lower = upper + min_dim
            img = img.crop((left, upper, right, lower))
            print(f"[*] Cropped to square: {min_dim}x{min_dim}")

        if img.size != (target_size, target_size):
            img = img.resize((target_size, target_size), Image.Resampling.LANCZOS)

        img.save(output_path, "PNG")
        print(f"[✓] Reference image saved: {target_size}x{target_size}")
        return True

    except Exception as e:
        print(f"[!] Reference image post-processing failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def transform_photo_to_chibi(photo_path, prompt, output_path, provider=None):
    """将真人照片转换为角色定妆图"""
    print(f"=== Transforming Photo to Sticker Character ===")
    print(f"[*] Input photo: {photo_path}")
    print(f"[*] Output: {output_path}")

    if not os.path.exists(photo_path):
        print(f"Error: Photo not found: {photo_path}", file=sys.stderr)
        return False

    config = load_config()

    if not provider:
        provider = config.get("default_provider", "gemini")

    provider_config = config["providers"].get(provider, {})
    api_key = provider_config.get("api_key")

    if not api_key:
        if provider == "gemini":
            api_key = os.environ.get("GEMINI_API_KEY")
        elif provider == "qwen":
            api_key = os.environ.get("DASHSCOPE_API_KEY")
        elif provider == "gpt-image-2":
            api_key = os.environ.get("TOKENROUTER_API_KEY") or os.environ.get(
                "OPENAI_API_KEY"
            )

        if not api_key:
            api_key, provider = get_api_key()
            if not api_key:
                return False

    # 分支 1: gpt-image-2 走 /v1/images/edits(multipart 参考图编辑)
    if provider == "gpt-image-2":
        if not model:
            model = "gpt-image-2"
        if not api_base_url:
            api_base_url = provider_config.get("api_base_url", "")
        print(f"[*] Transforming with gpt-image-2 (/v1/images/edits)...")
        ok, err = _gpt_image_2_edit(
            prompt=prompt,
            output_image_path=output_path,
            reference_image_path=photo_path,
            api_key=api_key,
            model=model,
            api_base_url=api_base_url,
            size="1024x1024",
        )
        if not ok:
            print(f"Error transforming photo: {err}", file=sys.stderr)
            return False

        # 跟 gemini 分支保持一致:对结果做 _process_reference_image 标准化(裁方+缩 512)
        try:
            with open(output_path, "rb") as f:
                img_data = f.read()
            if _process_reference_image(img_data, output_path):
                return True
            return True  # 即使后处理失败,raw 已写入,也算成功
        except Exception as e:
            print(f"[!] post-process warning: {e}", file=sys.stderr)
            return True

    # 分支 2: Gemini(原逻辑)
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        print(
            "Error: google-genai not installed. Run: pip install google-genai",
            file=sys.stderr,
        )
        return False

    with open(photo_path, "rb") as f:
        photo_data = f.read()

    import imghdr

    img_type = imghdr.what(photo_path)
    mime_type = f"image/{img_type}" if img_type else "image/jpeg"

    print(f"[*] Transforming with gemini-3.1-flash-image-preview...")
    print(f"[*] Letting Gemini identify and transform the main person...")

    try:
        client = genai.Client(api_key=api_key)

        contents = [types.Part.from_bytes(data=photo_data, mime_type=mime_type), prompt]

        response = client.models.generate_content(
            model=model or "gemini-3.1-flash-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image_data = part.inline_data.data

                processed = _process_reference_image(image_data, output_path)
                if processed:
                    return True
                else:
                    with open(output_path, "wb") as f:
                        f.write(image_data)
                    print(f"[✓] Character reference saved: {output_path}")
                    return True

        print("Error: No image in response", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error transforming photo: {e}", file=sys.stderr)
        return False


def draw_character_reference(prompt, output_path, provider=None):
    """生成角色定妆参考图（不带动作，纯外观展示）"""
    print(f"=== Generating Character Reference Image ===")
    return generate_image(prompt, output_path, provider=provider)
