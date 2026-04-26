#!/usr/bin/env python3
"""
推送文章到微信公众号
"""

import os
import requests
import json
from pathlib import Path

# 微信公众号配置（需要用户填写）
WECHAT_APPID = "你的AppID"
WECHAT_APPSECRET = "你的AppSecret"

def get_access_token():
    """获取 access_token"""
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WECHAT_APPID}&secret={WECHAT_APPSECRET}"

    response = requests.get(url)
    result = response.json()

    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"获取 access_token 失败：{result}")

def upload_image(access_token, image_path):
    """上传图片到微信素材库"""
    url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"

    with open(image_path, "rb") as f:
        files = {"media": f}
        response = requests.post(url, files=files)

    result = response.json()

    if "url" in result:
        return result["url"]
    else:
        raise Exception(f"上传图片失败：{result}")

def convert_markdown_to_html(markdown_file):
    """将 Markdown 转换为适配微信公众号的 HTML"""
    # 简单转换（实际使用时建议使用专业库，如 markdown2、html2text 等）
    with open(markdown_file, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    # TODO: 实现完整的 Markdown → HTML 转换
    # 这里只是示例，实际需要处理：标题、段落、列表、代码块、表格、图片等

    html = f"<div>{markdown_content}</div>"

    return html

def create_draft(access_token, title, html_content, author="", digest="", content_source_url=""):
    """创建草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"

    data = {
        "articles": [
            {
                "title": title,
                "author": author,
                "digest": digest,
                "content": html_content,
                "content_source_url": content_source_url,
                "thumb_media_id": "",  # 封面图片的 media_id（需要先上传）
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }
        ]
    }

    response = requests.post(url, json=data)
    result = response.json()

    if result.get("errcode") == 0:
        return result["media_id"]
    else:
        raise Exception(f"创建草稿失败：{result}")

def publish_draft(access_token, media_id):
    """发布草稿"""
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"

    data = {
        "media_id": media_id
    }

    response = requests.post(url, json=data)
    result = response.json()

    if result.get("errcode") == 0:
        return result["publish_id"]
    else:
        raise Exception(f"发布草稿失败：{result}")

def main():
    # 1. 获取 access_token
    print("正在获取 access_token...")
    access_token = get_access_token()
    print(f"access_token 获取成功：{access_token[:10]}...")

    # 2. 转换 Markdown 为 HTML
    markdown_file = "wiki/概念/元一思想.md"  # 示例文件
    print(f"正在转换 Markdown 文件：{markdown_file}")
    html_content = convert_markdown_to_html(markdown_file)

    # 3. 创建草稿
    print("正在创建草稿...")
    media_id = create_draft(
        access_token,
        title="元一思想",
        html_content=html_content,
        author="元一",
        digest="元一思想：AI 时代的知识管理哲学"
    )
    print(f"草稿创建成功：{media_id}")

    # 4. 发布草稿（可选，也可以先手动审核草稿）
    # print("正在发布草稿...")
    # publish_id = publish_draft(access_token, media_id)
    # print(f"草稿发布成功：{publish_id}")

    print("完成！请登录公众号后台查看草稿。")

if __name__ == "__main__":
    main()
