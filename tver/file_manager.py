#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件管理器
处理输出目录创建、文件命名和保存
"""

from pathlib import Path
from typing import Union

from .config import OUTPUT_DIR
from .exceptions import FileOperationError


def ensure_output_directory(dir_path: str = OUTPUT_DIR) -> Path:
    """
    确保输出目录存在

    Args:
        dir_path: 输出目录路径

    Returns:
        Path对象

    Raises:
        FileOperationError: 创建目录失败
    """
    try:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError:
        raise FileOperationError(f"没有权限创建输出目录: {dir_path}")
    except Exception as e:
        raise FileOperationError(f"创建输出目录失败: {str(e)}")


def generate_filename(video_id: str, episode_number: Union[str, int]) -> str:
    """
    生成字幕文件名

    Args:
        video_id: 视频ID (例如: ep8ec3bhfj)
        episode_number: 集数 (例如: 1, "1", "01")

    Returns:
        文件名 (例如: ep8ec3bhfj_01.vtt)
    """
    # 确保集数是两位数格式
    if isinstance(episode_number, int):
        ep_str = f"{episode_number:02d}"
    else:
        # 如果已经是字符串,尝试转换为整数再格式化
        try:
            ep_num = int(episode_number)
            ep_str = f"{ep_num:02d}"
        except ValueError:
            # 如果无法转换,直接使用原始字符串
            ep_str = str(episode_number)

    return f"{video_id}_{ep_str}.vtt"


def save_subtitle(
    content: str,
    filename: str,
    output_dir: str = OUTPUT_DIR
) -> Path:
    """
    保存字幕文件

    Args:
        content: 字幕内容
        filename: 文件名
        output_dir: 输出目录

    Returns:
        完整文件路径

    Raises:
        FileOperationError: 保存失败
    """
    try:
        # 确保输出目录存在
        dir_path = ensure_output_directory(output_dir)

        # 完整文件路径
        file_path = dir_path / filename

        # 写入文件(UTF-8编码)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path

    except PermissionError:
        raise FileOperationError(f"没有权限写入文件: {filename}")
    except Exception as e:
        raise FileOperationError(f"保存字幕文件失败: {str(e)}")


def check_file_exists(
    video_id: str,
    episode_number: Union[str, int],
    output_dir: str = OUTPUT_DIR
) -> bool:
    """
    检查字幕文件是否已存在

    Args:
        video_id: 视频ID
        episode_number: 集数
        output_dir: 输出目录

    Returns:
        True if exists, False otherwise
    """
    filename = generate_filename(video_id, episode_number)
    file_path = Path(output_dir) / filename
    return file_path.exists()


def get_file_path(
    video_id: str,
    episode_number: Union[str, int],
    output_dir: str = OUTPUT_DIR
) -> Path:
    """
    获取字幕文件的完整路径

    Args:
        video_id: 视频ID
        episode_number: 集数
        output_dir: 输出目录

    Returns:
        Path对象
    """
    filename = generate_filename(video_id, episode_number)
    return Path(output_dir) / filename
