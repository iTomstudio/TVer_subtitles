#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVer字幕下载工具 - 主程序
支持CLI、交互式和批量处理模式
"""

import sys
import argparse
from typing import Dict

from tver.url_parser import extract_video_id, parse_batch_file
from tver.api_client import TVerAPIClient
from tver.subtitle_downloader import download_and_merge_subtitles
from tver.file_manager import save_subtitle, generate_filename, check_file_exists
from tver.exceptions import (
    TVerSubtitleError,
    InvalidURLError,
    APIError,
    SubtitleNotFoundError,
    DownloadError,
    MergeError,
    FileOperationError,
)


def process_single_url(
    url: str,
    skip_existing: bool = False,
    output_dir: str = "subtitles"
) -> bool:
    """
    处理单个URL的完整流程

    Args:
        url: TVer视频URL
        skip_existing: 是否跳过已存在的文件
        output_dir: 输出目录

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"\n{'=' * 60}")
        print(f"🎬 处理视频: {url}")
        print(f"{'=' * 60}")

        # 1. 提取视频ID
        video_id = extract_video_id(url)
        print(f"📌 视频ID: {video_id}")

        # 2. 初始化API客户端并获取字幕URL和集数
        print(f"\n🔐 初始化API客户端...")
        client = TVerAPIClient()

        subtitle_url, episode_number = client.get_subtitle_url(video_id)

        # 3. 检查文件是否已存在
        if skip_existing and check_file_exists(video_id, episode_number, output_dir):
            filename = generate_filename(video_id, episode_number)
            print(f"⏭️  字幕已存在,跳过: {filename}")
            return True

        # 4. 下载并合并字幕
        print(f"\n📥 开始下载字幕...")
        subtitle_content = download_and_merge_subtitles(subtitle_url)

        # 5. 保存文件
        filename = generate_filename(video_id, episode_number)
        file_path = save_subtitle(subtitle_content, filename, output_dir)

        print(f"\n{'=' * 60}")
        print(f"✅ 字幕下载成功!")
        print(f"📁 保存位置: {file_path}")
        print(f"📊 文件大小: {len(subtitle_content)} 字符")
        print(f"{'=' * 60}")

        return True

    except InvalidURLError as e:
        print(f"\n❌ 无效的TVer URL: {str(e)}")
        return False
    except SubtitleNotFoundError as e:
        print(f"\n📝 {str(e)}")
        return False
    except APIError as e:
        print(f"\n❌ API错误: {str(e)}")
        return False
    except (DownloadError, MergeError) as e:
        print(f"\n❌ 下载错误: {str(e)}")
        return False
    except FileOperationError as e:
        print(f"\n❌ 文件操作错误: {str(e)}")
        return False
    except TVerSubtitleError as e:
        print(f"\n❌ 错误: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ 未预期的错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def process_batch_file(
    file_path: str,
    skip_existing: bool = False,
    output_dir: str = "subtitles"
) -> Dict[str, int]:
    """
    批量处理URL文件

    Args:
        file_path: 包含URL列表的文本文件路径
        skip_existing: 是否跳过已存在的文件
        output_dir: 输出目录

    Returns:
        统计字典 {"success": N, "failed": N, "skipped": N}
    """
    stats = {"success": 0, "failed": 0, "skipped": 0}

    try:
        # 读取URL列表
        urls = parse_batch_file(file_path)

        print(f"\n{'=' * 60}")
        print(f"📦 批量处理模式")
        print(f"📄 文件: {file_path}")
        print(f"📊 共 {len(urls)} 个URL")
        print(f"{'=' * 60}")

        # 逐个处理
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] 处理中...")

            success = process_single_url(url, skip_existing, output_dir)

            if success:
                # 检查是否是跳过的
                try:
                    video_id = extract_video_id(url)
                    # 这里无法准确判断是否跳过,简化处理
                    stats["success"] += 1
                except:
                    stats["success"] += 1
            else:
                stats["failed"] += 1

        # 显示统计
        print(f"\n{'=' * 60}")
        print(f"📊 批量处理完成")
        print(f"✅ 成功: {stats['success']}")
        print(f"❌ 失败: {stats['failed']}")
        print(f"{'=' * 60}")

        return stats

    except FileNotFoundError as e:
        print(f"\n❌ {str(e)}")
        return stats
    except InvalidURLError as e:
        print(f"\n❌ {str(e)}")
        return stats
    except Exception as e:
        print(f"\n❌ 批量处理错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return stats


def interactive_mode(output_dir: str = "subtitles"):
    """
    交互模式

    Args:
        output_dir: 输出目录
    """
    print(f"\n{'=' * 60}")
    print(f"📺 TVer字幕下载工具 - 交互模式")
    print(f"{'=' * 60}")
    print(f"输入TVer视频URL开始下载,输入 'q' 或 'quit' 退出")
    print(f"{'=' * 60}\n")

    while True:
        try:
            # 获取用户输入
            url = input("请输入TVer URL: ").strip()

            # 检查退出命令
            if url.lower() in ['q', 'quit', 'exit']:
                print("\n👋 再见!")
                break

            # 跳过空输入
            if not url:
                continue

            # 处理URL
            process_single_url(url, skip_existing=False, output_dir=output_dir)

        except KeyboardInterrupt:
            print("\n\n👋 用户中断,退出程序")
            break
        except EOFError:
            print("\n\n👋 输入结束,退出程序")
            break


def main():
    """主入口,解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="📺 TVer字幕下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 单个URL
  python tver_subtitle.py https://tver.jp/episodes/ep8ec3bhfj

  # 批量处理
  python tver_subtitle.py --batch urls.txt

  # 交互模式
  python tver_subtitle.py

  # 自定义输出目录
  python tver_subtitle.py URL --output-dir ./my_subtitles

  # 跳过已存在的文件
  python tver_subtitle.py --batch urls.txt --skip-existing
        """
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="TVer视频URL"
    )

    parser.add_argument(
        "--batch", "-b",
        metavar="FILE",
        help="包含URL列表的文本文件路径"
    )

    parser.add_argument(
        "--output-dir", "-o",
        default="subtitles",
        help="输出目录 (默认: subtitles)"
    )

    parser.add_argument(
        "--skip-existing", "-s",
        action="store_true",
        help="跳过已存在的文件"
    )

    args = parser.parse_args()

    # 判断模式
    if args.batch:
        # 批量处理模式
        process_batch_file(args.batch, args.skip_existing, args.output_dir)
    elif args.url:
        # 单URL模式
        success = process_single_url(args.url, args.skip_existing, args.output_dir)
        sys.exit(0 if success else 1)
    else:
        # 交互模式
        interactive_mode(args.output_dir)


if __name__ == "__main__":
    main()
