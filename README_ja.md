# TVer 字幕ダウンロードツール

TVer動画URLから日本語VTT字幕ファイルを自動取得・ダウンロードするツールです。

## 機能

- TVer動画URLから字幕を自動抽出
- 動画のエピソード番号を自動取得
- 複数のVTT字幕セグメントを1つの完全なファイルに結合
- 3つの使用モードをサポート：
  - **CLIモード**: コマンドラインで単一URL処理
  - **バッチモード**: テキストファイルから複数のURLを一括処理
  - **対話モード**: インタラクティブにURLを入力
- スマートファイル命名：`{video_id}_{episode_number}.vtt`
- 出力ディレクトリの自動作成
- 充実したエラー処理とメッセージ

## インストール

### 1. プロジェクトをクローンまたはダウンロード

```bash
cd /path/to/Tver
```

### 2. 依存関係をインストール

```bash
pip install -r requirements.txt
```

必要な依存関係は`requests`のみです。

## 使用方法

### 🌟 推奨：簡易版ツールの使用

TVer APIの認証メカニズムが複雑なため、**簡易版ツール**の使用を推奨します。ブラウザから取得したm3u8 URLを直接使用できます。

#### ステップ 1: ブラウザから字幕m3u8 URLを取得

1. TVer動画ページを開く（例：`https://tver.jp/episodes/ep8ec3bhfj`）
2. ブラウザの開発者ツールを開く（`F12`キー）
3. **Network**タブに切り替え
4. ページをリフレッシュして動画を再生
5. Networkタブで`manifest.m3u8`を検索
6. `manifest.m3u8`ファイルをクリックして、レスポンス内容を表示
7. `SUBTITLES`を含む行を見つける：
   ```
   #EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="captions",NAME="日本語",LANGUAGE="ja",URI="https://tracks.streaks.jp/.../captions/.../index.m3u8?offset=900000&ts=..."
   ```
8. その行のURI（`index.m3u8`の完全なURL）をコピー

#### ステップ 2: ツールで字幕をダウンロード

```bash
python3 tver_subtitle_simple.py "<m3u8_url>" <出力ファイル名>
```

**例：**

```bash
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/tver-tbs/a80ce643991e4dff80cd55f9b7054182/captions/5e921703781b43fd96e717594abafa6b/index.m3u8?offset=900000&ts=1761095525" \
  ep8ec3bhfj_01.vtt
```

**パラメータ説明：**
- `<m3u8_url>`: ブラウザからコピーした字幕m3u8 URL（引用符で囲む必要があります）
- `<出力ファイル名>`: 出力ファイル名、推奨形式：`{video_id}_{エピソード番号}.vtt`
  - 例：`ep8ec3bhfj_01.vtt` はビデオIDが ep8ec3bhfj の第1話を表します

**オプションパラメータ：**
```bash
python3 tver_subtitle_simple.py "<m3u8_url>" <出力ファイル名> --output-dir ./my_subtitles
```

#### ステップ 3: 結果を確認

字幕ファイルは`subtitles/`ディレクトリ（デフォルト）に保存され、以下のような出力が表示されます：

```
============================================================
📥 字幕のダウンロードを開始
📌 出力ファイル: ep8ec3bhfj_01.vtt
============================================================

📥 字幕インデックスをダウンロード中...
📝 94個の字幕セグメントを発見
📥 94個の字幕セグメントを並列ダウンロード中...
🔄 字幕セグメントを結合中...
✅ 結合完了、合計713個の字幕

============================================================
✅ 字幕ダウンロード成功！
📁 保存場所: subtitles/ep8ec3bhfj_01.vtt
📊 ファイルサイズ: 35518文字
============================================================
```

### 完全版ツール（上級者向け）

**注意:** 現在、TVer APIの認証問題により、完全版ツールは正常に動作しない可能性があります。簡易版ツールの使用を推奨します。

#### CLIモード - 単一URL

```bash
python tver_subtitle.py https://tver.jp/episodes/ep8ec3bhfj
```

#### バッチ処理モード

テキストファイル（例：`urls.txt`）を作成し、1行に1つのURLを記述：

```
https://tver.jp/episodes/ep8ec3bhfj
https://tver.jp/episodes/ep9xample1
https://tver.jp/episodes/ep9xample2
# これはコメントで、無視されます
```

その後実行：

```bash
python tver_subtitle.py --batch urls.txt
```

#### 対話モード

パラメータなしでプログラムを実行：

```bash
python tver_subtitle.py
```

プロンプトに従ってURLを入力し、`q`または`quit`で終了します。

#### 高度なオプション

**カスタム出力ディレクトリ**

```bash
python tver_subtitle.py URL --output-dir ./my_subtitles
```

**既存ファイルをスキップ**

```bash
python tver_subtitle.py --batch urls.txt --skip-existing
```

**ヘルプを表示**

```bash
python tver_subtitle.py --help
```

## 出力形式

字幕ファイルは`subtitles/`ディレクトリ（デフォルト）に保存され、ファイル命名形式は：

```
{video_id}_{episode_number}.vtt
```

例：
- `ep8ec3bhfj_01.vtt` - ビデオIDは ep8ec3bhfj、第1話
- `ep9xample1_05.vtt` - ビデオIDは ep9xample1、第5話

ファイル内容は標準VTT形式：

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

## プロジェクト構成

```
Tver/
├── tver_subtitle_simple.py   # 簡易版ツール（推奨）
├── tver_subtitle.py           # 完全版ツール
├── tver/                      # コアパッケージ
│   ├── __init__.py
│   ├── api_client.py         # TVer及びStreaks APIクライアント
│   ├── subtitle_downloader.py # 字幕ダウンロードと結合
│   ├── url_parser.py         # URL解析と検証
│   ├── file_manager.py       # ファイル管理
│   ├── config.py             # 設定定数
│   └── exceptions.py         # カスタム例外
├── requirements.txt          # 依存関係
├── subtitles/                # 出力ディレクトリ（自動作成）
├── README.md                 # プロジェクトドキュメント（英語・中国語）
├── README_ja.md              # プロジェクトドキュメント（日本語）
└── USAGE.md                  # 使用ガイド
```

## 動作原理

### 簡易版ツール（推奨）

1. **インデックスダウンロード**: 字幕m3u8インデックスファイルをダウンロード
2. **セグメント解析**: すべてのVTT字幕セグメントのURLを抽出
3. **並列ダウンロード**: すべてのVTTセグメントを並列ダウンロード（最大10並列）
4. **結合**: すべてのセグメントを順番に結合
5. **保存**: 指定ディレクトリに保存

### 完全版ツール

1. **URL解析**: TVer URLからビデオIDを抽出
2. **プラットフォーム認証**: TVerプラットフォーム認証トークンを取得
3. **メタデータ取得**: APIを呼び出してビデオのエピソード番号とref_idを取得
4. **字幕URL取得**: Streaks APIを通じて字幕トラックURLを取得
5. **インデックスダウンロード**: 字幕m3u8インデックスファイルをダウンロード
6. **並列ダウンロード**: すべてのVTT字幕セグメントを並列ダウンロード
7. **結合**: すべてのセグメントを1つの完全なVTTファイルに結合
8. **保存**: 指定ディレクトリに保存

## エラー処理

プログラムはエラー原因を明確に表示します：

| エラータイプ | エラーメッセージ |
|---------|---------|
| 無効なURL | "無効なTVer URL形式" |
| ビデオが存在しない | "ビデオが存在しないか削除されています" |
| 字幕なし | "このビデオには利用可能な字幕がありません" |
| ネットワークタイムアウト | "リクエストタイムアウト、再試行中..." |
| アクセス拒否 | "アクセスが拒否されました。日本のIPアドレスが必要な可能性があります" |
| ファイル書き込み失敗 | "出力ディレクトリへの書き込み権限がありません" |

## 注意事項

1. **ネットワークアクセス**: TVerは日本国外のIPアクセスを制限する可能性があります。403エラーが発生した場合は、日本のVPNまたはプロキシを使用してください
2. **API変更**: TVerはいつでもAPI構造を変更する可能性があります。問題が発生した場合は報告してください
3. **字幕のみ**: このツールは字幕ファイルのみをダウンロードし、ビデオコンテンツはダウンロードしません
4. **合法的使用**: ダウンロードした字幕は個人学習目的でのみ使用してください

## よくある質問

### Q: なぜ「アクセスが拒否されました」と表示されるのですか？
A: TVerは日本国外のIPアクセスを制限する可能性があります。日本のVPNまたはプロキシを使用してみてください。

### Q: m3u8 URLは期限切れになりますか？
A: はい、URLのタイムスタンプ（`ts`パラメータ）には有効期限がある可能性があります。URLを取得後、できるだけ早くダウンロードすることをお勧めします。

### Q: 特定のエピソード範囲の字幕をダウンロードするには？
A: 対応するURLを含むバッチファイルを作成し、バッチモードを使用してください。

### Q: 字幕ファイルのエンコーディングは？
A: すべての字幕ファイルはUTF-8エンコーディングを使用しています。

### Q: ファイル命名形式をカスタマイズできますか？
A: 現在のバージョンは固定形式`{video_id}_{episode_number}.vtt`を使用しています。カスタマイズが必要な場合は`tver/file_manager.py`を変更してください。

## バッチダウンロード

複数のビデオの字幕をダウンロードする場合：

**シェルスクリプトの例 (batch_download.sh):**

```bash
#!/bin/bash

# 第1話
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/.../ep1/index.m3u8?..." \
  series_01.vtt

# 第2話
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/.../ep2/index.m3u8?..." \
  series_02.vtt

# 第3話
python3 tver_subtitle_simple.py \
  "https://tracks.streaks.jp/.../ep3/index.m3u8?..." \
  series_03.vtt
```

その後実行：
```bash
chmod +x batch_download.sh
./batch_download.sh
```

## トラブルシューティング

問題が発生した場合は、以下を確認してください：

1. m3u8 URLが完全か（すべての`?`以降のパラメータを含む）
2. URLを引用符で囲んでいるか
3. ネットワーク接続が正常か
4. Pythonバージョンが3.6以上か
5. requestsライブラリがインストールされているか（`pip install requests`）

## ライセンス

このプロジェクトは学習および研究目的でのみ使用してください。

## 貢献

IssueやPull Requestの提出を歓迎します！

## 更新履歴

### v1.0.0 (2024)
- 初版リリース
- CLI、バッチ、対話の3つのモードをサポート
- VTT字幕セグメントの自動結合
- 充実したエラー処理
- 簡易版ツールの追加（推奨）

## 技術サポート

問題や提案がある場合は、プロジェクトのREADME.mdを参照するか、Issueを提出してください。

---

**🌟 ヒント**: 簡易版ツール（`tver_subtitle_simple.py`）の使用を強く推奨します。より安定して信頼性が高いです！
