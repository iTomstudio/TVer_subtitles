#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TVer API客户端
处理TVer平台API和Streaks API的交互
"""

import time
import requests
from typing import Dict, Optional

from .config import (
    TVER_PLATFORM_CREATE_URL,
    TVER_PLATFORM_API_BASE,
    TVER_STREAKS_CONFIG_URL,
    STREAKS_PLAYBACK_API_BASE,
    DEFAULT_HEADERS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
)
from .exceptions import APIError, SubtitleNotFoundError


class TVerAPIClient:
    """TVer API客户端"""

    def __init__(self):
        """初始化API客户端"""
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        self.platform_uid: Optional[str] = None
        self.platform_token: Optional[str] = None
        self.streaks_api_key: Optional[str] = None
        self.streaks_project_id: Optional[str] = None

    def _make_request(
        self, method: str, url: str, headers: Optional[Dict] = None, **kwargs
    ) -> requests.Response:
        """
        发送HTTP请求(带重试机制)

        Args:
            method: HTTP方法(GET/POST)
            url: 请求URL
            headers: 额外的请求头
            **kwargs: 其他requests参数

        Returns:
            Response对象

        Raises:
            APIError: 请求失败
        """
        if headers:
            kwargs['headers'] = {**self.session.headers, **headers}

        kwargs.setdefault('timeout', REQUEST_TIMEOUT)

        last_error = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = self.session.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.Timeout:
                last_error = f"请求超时"
                if attempt < MAX_RETRIES:
                    print(f"⏱️ {last_error},正在重试 ({attempt}/{MAX_RETRIES})...")
                    time.sleep(RETRY_DELAY)
            except requests.HTTPError as e:
                status_code = e.response.status_code
                if status_code == 403:
                    raise APIError("访问被拒绝,可能需要日本IP地址")
                elif status_code == 404:
                    raise APIError("视频不存在或已下架")
                elif status_code >= 500:
                    last_error = f"服务器错误 ({status_code})"
                    if attempt < MAX_RETRIES:
                        print(f"⚠️ {last_error},正在重试 ({attempt}/{MAX_RETRIES})...")
                        time.sleep(RETRY_DELAY)
                    else:
                        raise APIError(f"TVer服务器错误: {status_code}")
                else:
                    raise APIError(f"HTTP错误: {status_code} - {e.response.text}")
            except requests.RequestException as e:
                raise APIError(f"网络请求失败: {str(e)}")

        raise APIError(f"{last_error},已达最大重试次数")

    def initialize_session(self) -> None:
        """
        初始化浏览器会话,获取平台认证令牌

        Raises:
            APIError: 初始化失败
        """
        try:
            # TVer平台认证需要发送空JSON body
            headers = {
                'Content-Type': 'application/json',
            }
            response = self._make_request(
                'POST',
                TVER_PLATFORM_CREATE_URL,
                headers=headers,
                json={}
            )
            data = response.json()

            if 'result' not in data or 'userID' not in data['result']:
                raise APIError("平台认证响应格式错误")

            result = data['result']
            self.platform_uid = result['userID']
            self.platform_token = result['token']

            print(f"✅ 平台认证成功 (UID: {self.platform_uid[:8]}...)")

        except (KeyError, ValueError) as e:
            raise APIError(f"解析平台认证响应失败: {str(e)}")

    def get_streaks_config(self) -> None:
        """
        获取Streaks API配置

        Raises:
            APIError: 获取配置失败
        """
        try:
            response = self._make_request('GET', TVER_STREAKS_CONFIG_URL)
            data = response.json()

            if 'streaks' not in data:
                raise APIError("Streaks配置响应格式错误")

            streaks = data['streaks']
            self.streaks_api_key = streaks.get('api_key')
            self.streaks_project_id = streaks.get('project_id')

            if not self.streaks_api_key or not self.streaks_project_id:
                raise APIError("Streaks配置缺少必要字段")

            print(f"✅ 获取Streaks配置成功")

        except (KeyError, ValueError) as e:
            raise APIError(f"解析Streaks配置失败: {str(e)}")

    def get_video_metadata(self, video_id: str) -> Dict:
        """
        获取视频元数据(包括集数信息)

        Args:
            video_id: 视频ID (例如: ep8ec3bhfj)

        Returns:
            包含以下字段的字典:
            - episode_number: 集数 (例如: "1", "01")
            - ref_id: 用于Streaks API的video_id
            - title: 视频标题
            - series_name: 系列名称

        Raises:
            APIError: 获取元数据失败
        """
        # 使用新的API端点,不需要平台认证
        url = f"{TVER_PLATFORM_API_BASE}/callEpisodeDetail"
        params = {
            'episode_id': video_id,
        }
        headers = {
            'x-tver-platform-type': 'web',
        }

        try:
            response = self._make_request('GET', url, headers=headers, params=params)
            data = response.json()

            if 'result' not in data or 'episode' not in data['result']:
                raise APIError("视频元数据响应格式错误")

            episode = data['result']['episode']

            # 提取必要信息
            metadata = {
                'episode_number': str(episode.get('episode_number', '1')),
                'ref_id': episode.get('video_id', ''),
                'title': episode.get('title', ''),
                'series_name': episode.get('series', {}).get('title', ''),
            }

            if not metadata['ref_id']:
                raise APIError("视频元数据中缺少video_id")

            print(f"✅ 获取视频元数据成功: {metadata['series_name']} 第{metadata['episode_number']}话")

            return metadata

        except (KeyError, ValueError) as e:
            raise APIError(f"解析视频元数据失败: {str(e)}")

    def get_playback_info(self, ref_id: str) -> Dict:
        """
        获取播放信息(包括字幕轨道URL)

        Args:
            ref_id: 从视频元数据获取的video_id

        Returns:
            包含以下字段的字典:
            - subtitle_url: 字幕m3u8索引URL

        Raises:
            APIError: 获取播放信息失败
            SubtitleNotFoundError: 未找到字幕轨道
        """
        if not self.streaks_api_key or not self.streaks_project_id:
            self.get_streaks_config()

        url = f"{STREAKS_PLAYBACK_API_BASE}/projects/{self.streaks_project_id}/medias/ref:{ref_id}"
        headers = {
            'X-Streaks-Api-Key': self.streaks_api_key,
        }

        try:
            response = self._make_request('GET', url, headers=headers)
            data = response.json()

            # 查找字幕轨道
            text_tracks = data.get('text_tracks', [])
            if not text_tracks:
                raise SubtitleNotFoundError("该视频没有可用字幕")

            # 使用第一个字幕轨道(通常是日语字幕)
            subtitle_url = text_tracks[0].get('url', '')
            if not subtitle_url:
                raise SubtitleNotFoundError("字幕轨道URL为空")

            print(f"✅ 获取字幕轨道URL成功")

            return {
                'subtitle_url': subtitle_url,
            }

        except (KeyError, ValueError) as e:
            raise APIError(f"解析播放信息失败: {str(e)}")

    def get_subtitle_url(self, video_id: str) -> tuple[str, str]:
        """
        获取字幕URL的便捷方法

        Args:
            video_id: 视频ID

        Returns:
            (字幕URL, 集数) 元组

        Raises:
            APIError: API调用失败
            SubtitleNotFoundError: 未找到字幕
        """
        # 1. 获取视频元数据
        metadata = self.get_video_metadata(video_id)

        # 2. 获取播放信息
        playback_info = self.get_playback_info(metadata['ref_id'])

        return playback_info['subtitle_url'], metadata['episode_number']
