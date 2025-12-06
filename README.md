# TVer 字幕下载工具

一个自动化工具，用于从 TVer 视频URL获取并下载日语VTT字幕文件。

## 功能特性

- 从 TVer 视频URL自动提取字幕
- 自动获取视频集数信息
- 合并多个VTT字幕段为单个完整文件
- 支持三种使用模式：
  - **CLI模式**: 命令行单个URL处理
  - **批量模式**: 从文本文件读取多个URL批量处理
  - **交互模式**: 交互式输入URL
- 智能文件命名：`{video_id}_{episode_number}.vtt`
- 自动创建输出目录
- 完善的错误处理和提示

## 安装

### 1. 克隆或下载项目

```bash
cd /path/to/Tver
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

仅需要一个依赖：`requests`

## 使用方法

### CLI模式 - 单个URL

```bash
python tver_subtitle.py https://tver.jp/episodes/ep8ec3bhfj
```

### 批量处理模式

创建一个文本文件（例如 `urls.txt`），每行一个URL：

```
https://tver.jp/episodes/ep8ec3bhfj
https://tver.jp/episodes/ep9xample1
https://tver.jp/episodes/ep9xample2
# 这是注释，会被忽略
```

然后运行：

```bash
python tver_subtitle.py --batch urls.txt
```

### 交互模式

不带任何参数运行程序：

```bash
python tver_subtitle.py
```

然后按提示输入URL，输入 `q` 或 `quit` 退出。

### 高级选项

#### 自定义输出目录

```bash
python tver_subtitle.py URL --output-dir ./my_subtitles
```

#### 跳过已存在的文件

```bash
python tver_subtitle.py --batch urls.txt --skip-existing
```

#### 查看帮助

```bash
python tver_subtitle.py --help
```

## 输出格式

字幕文件会保存在 `subtitles/` 目录下（默认），文件命名格式：

```
{video_id}_{episode_number}.vtt
```

示例：
- `ep8ec3bhfj_01.vtt` - 视频ID为 ep8ec3bhfj，第1话
- `ep9xample1_05.vtt` - 视频ID为 ep9xample1，第5话

## 项目结构

```
Tver/
├── tver_subtitle.py          # 主程序入口
├── tver/                      # 核心包
│   ├── __init__.py
│   ├── api_client.py         # TVer和Streaks API客户端
│   ├── subtitle_downloader.py # 字幕下载和合并
│   ├── url_parser.py         # URL解析和验证
│   ├── file_manager.py       # 文件管理
│   ├── config.py             # 配置常量
│   └── exceptions.py         # 自定义异常
├── requirements.txt          # 依赖项
├── subtitles/                # 输出目录（自动创建）
└── README.md                 # 本文档
```

## 工作原理

1. **URL解析**: 从TVer URL提取视频ID
2. **平台认证**: 获取TVer平台认证令牌
3. **元数据获取**: 调用API获取视频集数和ref_id
4. **字幕URL获取**: 通过Streaks API获取字幕轨道URL
5. **下载索引**: 下载字幕m3u8索引文件
6. **并发下载**: 并发下载所有VTT字幕段
7. **合并**: 合并所有段为单个完整VTT文件
8. **保存**: 保存到指定目录

## 错误处理

程序会清晰地显示错误原因：

| 错误类型 | 错误消息 |
|---------|---------|
| 无效URL | "无效的TVer URL格式" |
| 视频不存在 | "视频不存在或已下架" |
| 无字幕 | "该视频没有可用字幕" |
| 网络超时 | "请求超时，正在重试..." |
| 访问被拒 | "访问被拒绝，可能需要日本IP地址" |
| 文件写入失败 | "没有权限写入输出目录" |

## 注意事项

1. **网络访问**: TVer可能限制非日本IP访问，如遇到403错误，可能需要使用日本VPN或代理
2. **API变更**: TVer可能随时更改API结构，如遇问题请报告
3. **仅字幕**: 本工具仅下载字幕文件，不下载视频内容
4. **合法使用**: 请仅将下载的字幕用于个人学习目的

## 常见问题

### Q: 为什么提示"访问被拒绝"？
A: TVer可能限制非日本IP访问，尝试使用日本VPN或代理。

### Q: 如何下载特定集数范围的字幕？
A: 创建包含对应URL的批量文件，然后使用批量模式。

### Q: 字幕文件编码是什么？
A: 所有字幕文件均使用UTF-8编码。

### Q: 可以自定义文件命名格式吗？
A: 当前版本使用固定格式 `{video_id}_{episode_number}.vtt`，如需自定义请修改 `tver/file_manager.py`。

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v1.0.0 (2024)
- 初始版本
- 支持CLI、批量和交互三种模式
- 自动合并VTT字幕段
- 完善的错误处理
