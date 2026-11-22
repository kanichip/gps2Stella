# GPS2STELLA

**スマートフォンのGPS測位データをStellariumの観測地点へ自動反映するWindows用ツール**

GPS2STELLAは、スマートフォンで測位した緯度・経度・標高をインターネット経由で受信し、Stellariumの観測地点を自動的に設定するPythonプログラムです。

スマートフォンとPCが同じLAN上にある必要はありません。GPS受信機をPCに接続することなく、遠征先の観測地点を簡単に設定できます。

Seestarなどのスマート望遠鏡を使った天体撮影や、Stellariumによる星空シミュレーションを想定しています。

## システム構成

```text
NCP Finder (iPhone / Android)
        │
        │ スマートフォンでGPS測位
        │ HTTPS POST
        ▼
gps.ballota.jp
GPS Relay API (PHP + SQLite)
        │
        │ 6桁キーでGPS座標取得
        │ HTTPS POST
        ▼
GPS2STELLA (Windows / Python)
        │
        │ Stellarium Remote Control API
        │ HTTP / localhost:8090
        ▼
Stellarium
観測地点を自動設定
```

## 主な機能

- **GPS測位データ取得**：6桁のキーコードを入力してGPS Relay APIから位置情報を取得
- **Stellariumとの自動連携**：緯度・経度・標高をRemote Control APIで転送
- **接続確認**：StellariumのAPIに接続できるかを確認
- **反映結果の検証**：設定した緯度・経度をStellariumから再取得して照合
- **エラー処理**：期限切れキー、接続失敗、タイムアウトなどを表示
- **EXE単体実行**：PyInstallerでビルドすればPythonをインストールしていないPCでも実行可能

## 動作環境

| 項目 | 内容 |
|---|---|
| OS | Windows 11（動作確認環境） |
| 言語 | Python 3 |
| Pythonライブラリ | requests |
| Stellarium | 26.3で動作確認済み |
| Stellarium 25.4 | 対応想定・実機検証前 |
| Remote Controlポート | 8090 |
| GPS中継サーバー | gps.ballota.jp |
| 通信方式 | HTTPS / HTTP |
| GPS受信機 | 不要 |

## インストール

### Pythonで実行する場合

Python 3をインストールし、必要なライブラリを追加します。

```powershell
pip install requests
```

リポジトリの `main.py` を実行します。

```powershell
python main.py
```

### EXEで実行する場合

GitHub Releasesなどから `GPS2STELLA.exe` を入手し、任意のフォルダに保存して実行します。

EXE版ではPythonのインストールは不要です。

## Stellarium側の準備

GPS2STELLAはStellariumのRemote Controlプラグインを利用します。

1. Stellariumを起動します。
2. 設定画面（F2）を開きます。
3. 「プラグイン」から「Remote Control」を選択します。
4. プラグインを有効にします。
5. 必要に応じてStellariumを再起動します。
6. Remote ControlのHTTPサーバーを起動します。
7. ポート番号を `8090` に設定します。

接続確認用URL：

`http://localhost:8090/api/main/status`

このURLにアクセスしてJSON形式のデータが表示されれば、Remote Control APIが動作しています。

## 使い方

### 1. スマートフォンでGPS測位

NCP Finderを開き、「測位データ送信」ボタンを押します。

GPSによる測位が完了すると、GPS Relay APIへ測位データが送信され、6桁のキーコードが表示されます。

キーコードの有効期間は10分間です。

### 2. GPS2STELLAを起動

Python版：

```powershell
python main.py
```

EXE版：

```powershell
.\GPS2STELLA.exe
```

### 3. キーコードを入力

```text
=== Stellarium GPS Location ===
6桁キーを入力: 253743

GPSデータ取得中...
緯度 : 34.235908
経度 : 132.630600
標高 : 6 m

Stellariumへ転送中...

Stellarium観測地点変更完了！
地点名 : GPS Location
緯度   : 34.235908...
経度   : 132.630600...
標高   : 6 m
```

※ 数値は表示例です。

GPS Relay APIから座標を取得すると、Stellariumの現在の観測地点が変更されます。

### 4. Stellariumで確認

Stellariumで観測地点ウィンドウ（F6）を開きます。

以下が反映されていれば成功です。

- 緯度
- 経度
- 標高
- 地点名：GPS Location

## GPS中継API

GPS2STELLAは、GPS Relay APIから測位データを取得します。

**エンドポイント**

`https://gps.ballota.jp/api.php?action=receive`

リクエスト：

```json
{
  "code": "253743"
}
```

レスポンス：

```json
{
  "status": "ok",
  "latitude": 34.235908,
  "longitude": 132.630600,
  "altitude": 6.0
}
```

GPS Relay APIの仕様：

| 項目 | 内容 |
|---|---|
| キーコード | 6桁の数字 |
| 有効期限 | 発行から10分 |
| 取得成功後 | サーバー上のデータを削除 |
| 複数端末 | キーごとに個別管理 |
| 通信 | HTTPS |

一度取得に成功したキーコードは再利用できません。

## Stellarium Remote Control API

GPS2STELLAは、Stellariumの以下のAPIを利用します。

| API | 用途 |
|---|---|
| `GET /api/main/status` | 接続確認・現在の観測地点取得 |
| `POST /api/location/setlocationfields` | 観測地点の設定 |

標準の接続先：

`http://localhost:8090`

Stellarium側のポートを変更した場合は、`main.py` の `STELLARIUM_API` を変更してください。

## EXEのビルド

PyInstallerを使用して、単一EXEファイルを作成できます。

### 必要なライブラリ

```powershell
pip install pyinstaller requests
```

### ビルドコマンド

```powershell
python -m PyInstaller --noconfirm --clean --onefile --console --name GPS2STELLA main.py
```

ビルド成功後、次の場所に実行ファイルが生成されます。

```text
dist/
└── GPS2STELLA.exe
```

`build_exe.bat` がある場合は、バッチファイルを実行するだけでもビルドできます。

## エラーと対処方法

| エラー | 原因・対処方法 |
|---|---|
| キーが存在しないか期限切れ | NCP Finderで再度測位データを送信 |
| HTTP 429 | APIのアクセス回数制限。時間をおいて再試行 |
| 通信タイムアウト | インターネット接続やAPIサーバーを確認 |
| Stellariumに接続できない | Stellariumの起動とRemote Control設定を確認 |
| 観測地点の反映失敗 | APIポート番号とStellariumの状態を確認 |

## 注意事項

### 測位精度

スマートフォンのGPS測位精度は、衛星の受信状況や周辺環境によって変動します。

屋内、建物の近く、山間部などでは精度が低下する場合があります。

### 標高

スマートフォンが返す高度は端末や測位条件によって精度が異なります。

高度が取得できない場合、GPS Relay APIから `null` が返ることがあります。

### 観測地点の保存

GPS2STELLAは、Stellariumの現在の観測地点を変更します。

地点リストへの永続的な登録を行うものではありません。

### GPSデータのワンタイム取得

GPS中継サーバーでは、測位データの取得成功後にレコードが削除されます。

そのため、GPS2STELLAが取得した後にStellariumへの接続で失敗した場合、同じキーで再取得することはできません。

## 動作確認

| テスト | 結果 |
|---|---|
| GPS Relay APIへの接続 | OK |
| 6桁キーによるGPS取得 | OK |
| 緯度・経度・標高の取得 | OK |
| Stellarium 26.3への位置設定 | OK |
| Stellariumからの反映確認 | OK |
| スマートフォン実測データでの連携 | OK |
| Stellarium 25.4 | 未検証 |

## 関連プロジェクト

**NCP Finder**

スマートフォンのセンサーを利用し、天の北極方向への簡易的な仮合わせを支援するWebアプリです。GPS測位データの送信機能を搭載しています。

**gps-Relay-api**

PHPとSQLiteで動作するGPS測位データ中継APIです。6桁キーを使って測位データを一時的に保持・受け渡しします。

## ライセンス

ライセンス未設定。

---

GPS2STELLAは、Seestarなどのスマート望遠鏡を遠征先で使用する際、Stellariumの観測地点設定を簡単にする目的で開発しました。
