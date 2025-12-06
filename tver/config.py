#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置常量
包含所有API端点、HTTP头、超时设置等配置
"""

# API端点
TVER_PLATFORM_CREATE_URL = "https://platform-api.tver.jp/v2/api/platform_users/browser/create"
TVER_PLATFORM_API_BASE = "https://platform-api.tver.jp/service/api/v1"
TVER_STREAKS_CONFIG_URL = "https://player.tver.jp/player/streaks_info_v2.json"
STREAKS_PLAYBACK_API_BASE = "https://playback.api.streaks.jp/v1"

# HTTP请求头配置 - 用于API请求
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "ja,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://tver.jp",
    "Referer": "https://tver.jp/",
}

# HTTP请求头配置 - 用于VTT字幕下载
VTT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/vtt,*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ja,en;q=0.9",
}

# 文件配置
OUTPUT_DIR = "subtitles"
BATCH_FILE_COMMENT_PREFIX = "#"

# 网络配置
REQUEST_TIMEOUT = 30  # 请求超时时间(秒)
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 1  # 重试延迟(秒)

# 并发下载配置
MAX_CONCURRENT_DOWNLOADS = 10  # 最大并发下载VTT段数量
