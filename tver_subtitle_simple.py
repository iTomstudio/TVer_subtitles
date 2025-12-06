#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVer字幕下载工具 - 简化版
直接使用字幕m3u8 URL进行下载
"""

import sys
import argparse

from tver.subtitle_downloader import download_and_merge_subtitles
from tver.file_manager import save_subtitle
from tver.exceptions import DownloadError, MergeError, FileOperationError


def download_subtitle(m3u8_url: str, output_filename: str, output_dir: str = "subtitles") -> bool:
    """
    从m3u8 URL下载并合并字幕

    Args:
        m3u8_url: 字幕m3u8索引URL
        output_filename: 输出文件名 (例如: ep8ec3bhfj_01.vtt)
        output_dir: 输出目录

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n{'=' * 60}")
        print(f"📥 开始下载字幕")
        print(f"📌 输出文件: {output_filename}")
        print(f"{'=' * 60}\n")

        # 下载并合并字幕
        subtitle_content = download_and_merge_subtitles(m3u8_url)

        # 保存文件
        file_path = save_subtitle(subtitle_content, output_filename, output_dir)

        print(f"\n{'=' * 60}")
        print(f"✅ 字幕下载成功!")
        print(f"📁 保存位置: {file_path}")
        print(f"📊 文件大小: {len(subtitle_content)} 字符")
        print(f"{'=' * 60}")

        return True

    except (DownloadError, MergeError) as e:
        print(f"\n❌ 下载错误: {str(e)}")
        return False
    except FileOperationError as e:
        print(f"\n❌ 文件操作错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主入口"""
    parser = argparse.ArgumentParser(
        description="📺 TVer字幕下载工具 - 简化版 (直接使用m3u8 URL)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python tver_subtitle_simple.py \\
    "https://tracks.streaks.jp/.../captions/.../index.m3u8?offset=900000&ts=..." \\
    ep8ec3bhfj_01.vtt

  python tver_subtitle_simple.py \\
    "https://tracks.streaks.jp/.../captions/.../index.m3u8?offset=900000&ts=..." \\
    ep8ec3bhfj_01.vtt \\
    --output-dir ./my_subtitles

如何获取m3u8 URL:
  1. 打开TVer视频页面
  2. 打开浏览器开发者工具 (F12)
  3. 切换到Network标签
  4. 刷新页面并播放视频
  5. 搜索 "manifest.m3u8"
  6. 打开manifest.m3u8,找到包含 "SUBTITLES" 的行
  7. 复制该行中的 URI (index.m3u8)
        """
    )

    parser.add_argument(
        "m3u8_url",
        help="字幕m3u8索引URL"
    )

    parser.add_argument(
        "output_filename",
        help="输出文件名 (例如: ep8ec3bhfj_01.vtt)"
    )

    parser.add_argument(
        "--output-dir", "-o",
        default="subtitles",
        help="输出目录 (默认: subtitles)"
    )

    args = parser.parse_args()

    success = download_subtitle(args.m3u8_url, args.output_filename, args.output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
