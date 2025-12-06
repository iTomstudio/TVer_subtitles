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
            # TVer平台认证需要发送device_type参数
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            response = self._make_request(
                'POST',
                TVER_PLATFORM_CREATE_URL,
                headers=headers,
                data='device_type=pc'
            )
            data = response.json()

            if 'result' not in data:
                raise APIError("平台认证响应格式错误")

            result = data['result']
            self.platform_uid = result.get('platform_uid')
            self.platform_token = result.get('platform_token')

            if not self.platform_uid or not self.platform_token:
                raise APIError("平台认证响应缺少必要字段")

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

            # Streaks配置是按项目ID组织的字典
            # 例如: {"tver-ntv": {"api_key": {...}}, "tver-tbs": {...}}
            if not data or not isinstance(data, dict):
                raise APIError("Streaks配置响应格式错误")

            # 保存整个配置字典
            self.streaks_api_key = data
            # streaks_project_id将在get_playback_info中从视频元数据获取
            self.streaks_project_id = None

            print(f"✅ 获取Streaks配置成功 (包含{len(data)}个项目)")

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
        # 确保已初始化会话
        if not self.platform_uid or not self.platform_token:
            self.initialize_session()

        # 使用平台API端点
        url = f"{TVER_PLATFORM_API_BASE}/callEpisode/{video_id}"
        params = {
            'platform_uid': self.platform_uid,
            'platform_token': self.platform_token,
            'require_data': 'mylist,later[epefy106ur],good[epefy106ur],resume[epefy106ur]',
        }
        headers = {
            'x-tver-platform-type': 'web',
        }

        try:
            response = self._make_request('GET', url, headers=headers, params=params)
            data = response.json()

            if 'result' not in data or 'episode' not in data['result']:
                raise APIError("视频元数据响应格式错误")

            episode_content = data['result']['episode'].get('content', {})

            # 获取版本号以便获取更多信息
            version = episode_content.get('version', '5')

            # 从静态JSON获取更详细的信息
            video_info_url = f"https://statics.tver.jp/content/episode/{video_id}.json"
            video_info_response = self._make_request(
                'GET',
                video_info_url,
                params={'v': version},
                headers={'Referer': 'https://tver.jp/'}
            )
            video_info = video_info_response.json()

            # 提取必要信息
            ref_id = video_info.get('streaks', {}).get('videoRefID', '')
            if ref_id and not ref_id.startswith('ref:'):
                ref_id = f"ref:{ref_id}"

            metadata = {
                'episode_number': str(video_info.get('no', '1')),
                'ref_id': ref_id,
                'title': episode_content.get('title', ''),
                'series_name': episode_content.get('seriesTitle', ''),
                'project_id': video_info.get('streaks', {}).get('projectID', ''),
            }

            if not metadata['ref_id']:
                raise APIError("视频元数据中缺少videoRefID")

            print(f"✅ 获取视频元数据成功: {metadata['series_name']} 第{metadata['episode_number']}话")

            return metadata

        except (KeyError, ValueError) as e:
            raise APIError(f"解析视频元数据失败: {str(e)}")

    def get_playback_info(self, ref_id: str, project_id: str) -> Dict:
        """
        获取播放信息(包括字幕轨道URL)

        Args:
            ref_id: 从视频元数据获取的video_id (已包含ref:前缀)
            project_id: Streaks项目ID

        Returns:
            包含以下字段的字典:
            - subtitle_url: 字幕m3u8索引URL

        Raises:
            APIError: 获取播放信息失败
            SubtitleNotFoundError: 未找到字幕轨道
        """
        if not self.streaks_api_key or not self.streaks_project_id:
            self.get_streaks_config()

        # 根据月份选择API密钥(yt-dlp的逻辑)
        import datetime
        key_idx = datetime.datetime.now().month % 6 or 6

        # 从streaks配置中获取项目特定的API密钥
        project_config = self.streaks_api_key.get(project_id, {})
        if not project_config:
            raise APIError(f"未找到项目{project_id}的Streaks配置")

        api_keys = project_config.get('api_key', {})
        if isinstance(api_keys, dict):
            api_key = api_keys.get(f'key0{key_idx}', list(api_keys.values())[0] if api_keys else '')
        else:
            raise APIError(f"项目{project_id}的API密钥格式错误")

        url = f"{STREAKS_PLAYBACK_API_BASE}/projects/{project_id}/medias/{ref_id}"
        headers = {
            'X-Streaks-Api-Key': api_key,
            'Origin': 'https://tver.jp',
            'Referer': 'https://tver.jp/',
        }

        try:
            response = self._make_request('GET', url, headers=headers)

            # 检查响应内容
            if not response.text:
                raise APIError("Streaks API返回空响应")

            data = response.json()

            # 查找字幕轨道 (字段名是tracks不是text_tracks)
            tracks = data.get('tracks', [])
            if not tracks:
                raise SubtitleNotFoundError("该视频没有可用字幕")

            # 过滤出字幕轨道 (kind=subtitles或captions)
            text_tracks = [t for t in tracks if t.get('kind') in ('subtitles', 'captions')]
            if not text_tracks:
                raise SubtitleNotFoundError("该视频没有可用字幕")

            # 使用第一个字幕轨道(通常是日语字幕)
            # 尝试url或src字段
            subtitle_url = text_tracks[0].get('url') or text_tracks[0].get('src', '')
            if not subtitle_url:
                raise SubtitleNotFoundError("字幕轨道URL为空")

            print(f"✅ 获取字幕轨道URL成功")

            return {
                'subtitle_url': subtitle_url,
            }

        except (KeyError, ValueError) as e:
            raise APIError(f"解析播放信息失败: {str(e)}")
        except SubtitleNotFoundError:
            raise
        except Exception as e:
            raise APIError(f"获取播放信息时发生错误: {type(e).__name__}: {str(e)}")

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
        playback_info = self.get_playback_info(
            metadata['ref_id'],
            metadata['project_id']
        )

        return playback_info['subtitle_url'], metadata['episode_number']
