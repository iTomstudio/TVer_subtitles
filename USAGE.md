# TVer 字幕下载工具 - 使用指南

## 快速开始

由于TVer的API可能需要特定的认证机制，我们提供了一个**简化版工具**，让您可以直接使用从浏览器获取的m3u8 URL下载字幕。

## 方法：使用简化版工具 (推荐)

### 步骤 1: 从浏览器获取字幕 m3u8 URL

1. 打开TVer视频页面（例如：`https://tver.jp/episodes/ep8ec3bhfj`）
2. 打开浏览器开发者工具（按 `F12` 键）
3. 切换到 **Network** 标签
4. 刷新页面并播放视频
5. 在Network标签中搜索 `manifest.m3u8`
6. 点击 `manifest.m3u8` 文件，查看响应内容
7. 找到包含 `SUBTITLES` 的行，类似：
   ```
   #EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="captions",NAME="日本語",LANGUAGE="ja",URI="https://tracks.streaks.jp/.../captions/.../index.m3u8?offset=900000&ts=..."
   ```
8. 复制该行中的 URI（即 `index.m3u8` 的完整URL）

### 步骤 2: 使用工具下载字幕

```bash
python3 tver_subtitle_simple.py "<m3u8_url>" <output_filename>
```

**示例：**

```bash
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/tver-tbs/a80ce643991e4dff80cd55f9b7054182/captions/5e921703781b43fd96e717594abafa6b/index.m3u8?offset=900000&ts=1761095525" \
  ep8ec3bhfj_01.vtt
```

**参数说明：**
- `<m3u8_url>`: 从浏览器复制的字幕m3u8 URL（需要用引号包裹）
- `<output_filename>`: 输出文件名，建议格式：`{video_id}_{集数}.vtt`
  - 例如：`ep8ec3bhfj_01.vtt` 表示视频ID为ep8ec3bhfj的第1集

**可选参数：**
```bash
python3 tver_subtitle_simple.py "<m3u8_url>" <output_filename> --output-dir ./my_subtitles
```

### 步骤 3: 查看结果

字幕文件会保存在 `subtitles/` 目录（默认），您将看到类似输出：

```
============================================================
📥 开始下载字幕
📌 输出文件: ep8ec3bhfj_01.vtt
============================================================

📥 下载字幕索引...
📝 找到 94 个字幕段
📥 并发下载 94 个字幕段...
🔄 合并字幕段...
✅ 合并完成,共 713 条字幕

============================================================
✅ 字幕下载成功!
📁 保存位置: subtitles/ep8ec3bhfj_01.vtt
📊 文件大小: 35518 字符
============================================================
```

## 输出格式

下载的字幕文件为标准VTT格式，包含：
- WEBVTT头部
- 时间戳映射
- 按顺序编号的字幕条目
- 时间码和字幕文本

示例内容：
```vtt
WEBVTT
X-TIMESTAMP-MAP=MPEGTS:900000,LOCAL:00:00:00.000

1
00:00:04.671 --> 00:00:08.308
（勝男）強いて言うなら
全体的に おかずが茶色すぎるかな

2
00:00:08.308 --> 00:00:10.643
もうちょっと彩りを入れた方がいい
```

## 批量下载

如需下载多个视频的字幕：

1. 为每个视频获取对应的m3u8 URL
2. 创建一个shell脚本或逐个运行命令

**示例脚本 (batch_download.sh):**

```bash
#!/bin/bash

# 第1集
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/.../ep1/index.m3u8?..." \
  series_01.vtt

# 第2集
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/.../ep2/index.m3u8?..." \
  series_02.vtt

# 第3集
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/.../ep3/index.m3u8?..." \
  series_03.vtt
```

然后运行：
```bash
chmod +x batch_download.sh
./batch_download.sh
```

## 常见问题

### Q: 为什么不能直接使用视频URL？
A: TVer的API认证机制较为复杂且可能随时变更。使用m3u8 URL的方法更稳定可靠。

### Q: m3u8 URL会过期吗？
A: 是的，URL中的时间戳(`ts`参数)可能有有效期。建议获取URL后尽快下载。

### Q: 如何确定集数编号？
A: 集数信息需要手动确定。建议按照视频页面上显示的集数命名文件。

### Q: 下载失败怎么办？
A: 常见原因：
1. m3u8 URL已过期 - 重新从浏览器获取
2. 网络连接问题 - 检查网络连接
3. URL复制不完整 - 确保完整复制URL（包括所有参数）

## 高级功能

### 自定义输出目录

```bash
python3 tver_subtitle_simple.py "<m3u8_url>" filename.vtt --output-dir ./custom_dir
```

### 查看帮助信息

```bash
python3 tver_subtitle_simple.py --help
```

## 技术细节

工具的工作流程：
1. 下载m3u8索引文件
2. 解析出所有VTT字幕段的URL（通常有几十到上百个段）
3. 并发下载所有VTT段（最多10个并发）
4. 按顺序合并所有段
5. 重新编号字幕条目
6. 保存为单个VTT文件

## 注意事项

1. **合法使用**：请仅将下载的字幕用于个人学习目的
2. **网络要求**：某些TVer内容可能需要日本IP地址访问
3. **编码格式**：所有字幕文件使用UTF-8编码
4. **文件覆盖**：如果目标文件已存在，将会被覆盖

## 故障排除

如遇到问题，请检查：
1. m3u8 URL是否完整（包括所有`?`后的参数）
2. 是否用引号包裹URL
3. 网络连接是否正常
4. Python版本是否为3.6+
5. requests库是否已安装（`pip install requests`）

## 项目文件结构

```
Tver/
├── tver_subtitle_simple.py   # 简化版工具（推荐使用）
├── tver_subtitle.py           # 完整版工具（需要API修复）
├── tver/                      # 核心库
│   ├── subtitle_downloader.py # 字幕下载和合并逻辑
│   ├── file_manager.py        # 文件管理
│   └── ...
├── subtitles/                 # 默认输出目录
├── requirements.txt           # 依赖项
└── USAGE.md                   # 本文档
```

## 获取帮助

如有问题或建议，请查看项目README.md或提交Issue。
