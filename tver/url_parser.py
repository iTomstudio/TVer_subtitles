#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL解析器
处理TVer URL验证、视频ID提取和批量文件解析
"""

import re
from pathlib import Path
from typing import List

from .exceptions import InvalidURLError
from .config import BATCH_FILE_COMMENT_PREFIX


def validate_tver_url(url: str) -> bool:
    """
    验证是否为有效的TVer URL

    Args:
        url: 待验证的URL

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^https?://tver\.jp/episodes/[a-z0-9]+$'
    return bool(re.match(pattern, url.strip()))


def extract_video_id(url: str) -> str:
    """
    从URL提取视频ID

    Args:
        url: TVer视频URL

    Returns:
        视频ID (例如: ep8ec3bhfj)

    Raises:
        InvalidURLError: 如果URL格式无效
    """
    if not validate_tver_url(url):
        raise InvalidURLError(f"无效的TVer URL格式: {url}")

    # 提取 /episodes/ 后面的部分
    match = re.search(r'/episodes/([a-z0-9]+)', url)
    if not match:
        raise InvalidURLError(f"无法从URL提取视频ID: {url}")

    return match.group(1)


def parse_batch_file(file_path: str) -> List[str]:
    """
    从文本文件读取URL列表

    Args:
        file_path: 批量URL文件路径

    Returns:
        URL列表

    Raises:
        FileNotFoundError: 如果文件不存在
        InvalidURLError: 如果文件为空
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"批量文件不存在: {file_path}")

    urls = []
    with open(path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # 去除首尾空白
            line = line.strip()

            # 跳过空行和注释行
            if not line or line.startswith(BATCH_FILE_COMMENT_PREFIX):
                continue

            # 验证URL格式
            if validate_tver_url(line):
                urls.append(line)
            else:
                print(f"警告: 跳过第{line_num}行的无效URL: {line}")

    if not urls:
        raise InvalidURLError(f"批量文件中没有有效的URL: {file_path}")

    return urls
