#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕下载器
处理字幕索引下载、VTT段下载和合并
"""

import re
import requests
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from .config import (
    VTT_HEADERS,
    REQUEST_TIMEOUT,
    MAX_CONCURRENT_DOWNLOADS,
)
from .exceptions import DownloadError, MergeError


def download_subtitle_index(m3u8_url: str) -> str:
    """
    下载字幕索引m3u8文件

    Args:
        m3u8_url: 字幕索引URL

    Returns:
        m3u8文件内容

    Raises:
        DownloadError: 下载失败
    """
    try:
        response = requests.get(m3u8_url, headers=VTT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.RequestException as e:
        raise DownloadError(f"下载字幕索引失败: {str(e)}")


def parse_subtitle_segments(m3u8_content: str, base_url: str) -> List[str]:
    """
    解析m3u8文件,提取所有VTT段URL

    Args:
        m3u8_content: m3u8文件内容
        base_url: 基础URL(用于构建完整URL)

    Returns:
        VTT段URL列表

    Raises:
        MergeError: 解析失败
    """
    segment_urls = []

    # 提取基础URL和查询参数
    parsed_url = urlparse(base_url)
    base_path = parsed_url.path.rsplit('/', 1)[0] + '/'
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # 解析查询参数(offset和ts需要附加到每个段URL)
    query_params = parse_qs(parsed_url.query)
    query_string = ''
    if query_params:
        offset = query_params.get('offset', [''])[0]
        ts = query_params.get('ts', [''])[0]
        if offset and ts:
            query_string = f"?offset={offset}&ts={ts}"

    # 解析m3u8文件
    lines = m3u8_content.strip().split('\n')
    for line in lines:
        line = line.strip()

        # 找到.vtt文件行 (可能包含查询参数，也可能不包含)
        if '.vtt' in line and not line.startswith('#'):
            # 检查是否已经包含完整URL
            if line.startswith('http://') or line.startswith('https://'):
                segment_urls.append(line)
            else:
                # 相对路径，需要构建完整URL
                # 如果行中已有查询参数，直接使用；否则添加
                if '?' in line:
                    # 已有查询参数，直接拼接
                    segment_url = base_domain + base_path + line
                else:
                    # 没有查询参数，添加
                    segment_url = base_domain + base_path + line
                segment_urls.append(segment_url)

    if not segment_urls:
        raise MergeError("m3u8文件中未找到VTT段")

    print(f"📝 找到 {len(segment_urls)} 个字幕段")
    return segment_urls


def download_vtt_segment(url: str) -> tuple[str, str]:
    """
    下载单个VTT段

    Args:
        url: VTT段URL

    Returns:
        (URL, VTT内容) 元组

    Raises:
        DownloadError: 下载失败
    """
    try:
        response = requests.get(url, headers=VTT_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return url, response.text
    except requests.RequestException as e:
        raise DownloadError(f"下载VTT段失败 {url}: {str(e)}")


def merge_vtt_segments(segments: List[str]) -> str:
    """
    合并多个VTT段为单个文件

    Args:
        segments: VTT段内容列表(按顺序)

    Returns:
        合并后的VTT内容

    Raises:
        MergeError: 合并失败
    """
    if not segments:
        raise MergeError("没有VTT段可供合并")

    merged_lines = []
    cue_counter = 1

    for i, segment in enumerate(segments):
        lines = segment.strip().split('\n')

        if i == 0:
            # 第一个段:保留WEBVTT头和X-TIMESTAMP-MAP
            header_end = 0
            for j, line in enumerate(lines):
                if line.strip() == '' and j > 0:
                    header_end = j
                    break
                if line.startswith('WEBVTT') or line.startswith('X-TIMESTAMP-MAP'):
                    merged_lines.append(line)

            # 添加空行分隔头部和内容
            if header_end > 0:
                merged_lines.append('')

            # 处理第一个段的字幕条目
            in_cue = False
            cue_lines = []

            for line in lines[header_end + 1:]:
                line = line.strip()

                if not line:
                    # 空行表示一个cue结束
                    if in_cue and cue_lines:
                        # 重新编号并添加
                        merged_lines.append(str(cue_counter))
                        merged_lines.extend(cue_lines[1:])  # 跳过原始编号
                        merged_lines.append('')
                        cue_counter += 1
                        cue_lines = []
                        in_cue = False
                elif '-->' in line:
                    # 时间戳行
                    in_cue = True
                    cue_lines = ['', line]  # 占位符用于编号
                elif in_cue:
                    # 字幕文本
                    cue_lines.append(line)
                elif line.isdigit():
                    # 原始编号,跳过
                    continue

        else:
            # 后续段:只处理字幕条目,跳过头部
            in_cue = False
            cue_lines = []
            skip_header = True

            for line in lines:
                line = line.strip()

                # 跳过头部(WEBVTT, X-TIMESTAMP-MAP等)
                if skip_header:
                    if line.startswith('WEBVTT') or line.startswith('X-TIMESTAMP-MAP') or line.startswith('#'):
                        continue
                    if not line:
                        continue
                    skip_header = False

                if not line:
                    # 空行表示一个cue结束
                    if in_cue and cue_lines:
                        merged_lines.append(str(cue_counter))
                        merged_lines.extend(cue_lines[1:])
                        merged_lines.append('')
                        cue_counter += 1
                        cue_lines = []
                        in_cue = False
                elif '-->' in line:
                    # 时间戳行
                    in_cue = True
                    cue_lines = ['', line]
                elif in_cue:
                    # 字幕文本
                    cue_lines.append(line)
                elif line.isdigit():
                    # 原始编号,跳过
                    continue

            # 处理最后一个cue
            if in_cue and cue_lines:
                merged_lines.append(str(cue_counter))
                merged_lines.extend(cue_lines[1:])
                merged_lines.append('')
                cue_counter += 1

    print(f"✅ 合并完成,共 {cue_counter - 1} 条字幕")
    return '\n'.join(merged_lines)


def download_and_merge_subtitles(subtitle_url: str) -> str:
    """
    完整流程:下载索引 → 解析 → 并发下载段 → 合并

    Args:
        subtitle_url: 字幕索引m3u8 URL

    Returns:
        合并后的VTT内容

    Raises:
        DownloadError: 下载失败
        MergeError: 合并失败
    """
    print(f"📥 下载字幕索引...")
    # 1. 下载索引
    m3u8_content = download_subtitle_index(subtitle_url)

    # 2. 解析段列表
    segment_urls = parse_subtitle_segments(m3u8_content, subtitle_url)

    # 3. 并发下载所有段
    print(f"📥 并发下载 {len(segment_urls)} 个字幕段...")
    segments_dict = {}

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS) as executor:
        future_to_url = {
            executor.submit(download_vtt_segment, url): url
            for url in segment_urls
        }

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                url, content = future.result()
                # 根据URL中的段号排序(例如: 0.vtt, 1.vtt, ...)
                segment_num = int(re.search(r'/(\d+)\.vtt', url).group(1))
                segments_dict[segment_num] = content
            except Exception as e:
                raise DownloadError(f"下载段失败: {str(e)}")

    # 4. 按顺序合并
    segments = [segments_dict[i] for i in sorted(segments_dict.keys())]

    print(f"🔄 合并字幕段...")
    merged_content = merge_vtt_segments(segments)

    return merged_content
