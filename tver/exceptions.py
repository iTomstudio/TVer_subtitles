#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义异常类
定义所有TVer字幕下载相关的异常
"""


class TVerSubtitleError(Exception):
    """基础异常类"""
    pass


class InvalidURLError(TVerSubtitleError):
    """无效的TVer URL"""
    pass


class APIError(TVerSubtitleError):
    """API请求失败"""
    pass


class SubtitleNotFoundError(TVerSubtitleError):
    """未找到字幕轨道"""
    pass


class DownloadError(TVerSubtitleError):
    """下载失败"""
    pass


class MergeError(TVerSubtitleError):
    """VTT合并失败"""
    pass


class FileOperationError(TVerSubtitleError):
    """文件操作失败"""
    pass
