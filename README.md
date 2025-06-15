# Keyword Analyze

LINE Messaging API、Zenserp API、Google Sheetsを使用したキーワード分析ツール

## 機能

- LINEでキーワードを受信
- Zenserp APIを使用してGoogle検索結果を取得
- 検索結果をGoogleスプレッドシートに記録
- スプレッドシートのURLをLINEで返信

## セットアップ

1. リポジトリをクローン
```bash
git clone https://github.com/t-hamamura/keyword-analyze.git
cd keyword-analyze
```

2. 仮想環境を作成して有効化
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
.\venv\Scripts\activate  # Windowsの場合
```

3. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
- `.env.example` を `.env` にコピー
- 各APIキーと設定値を入力

5. Google Sheets APIの設定
- Google Cloud Consoleでプロジェクトを作成
- Google Sheets APIを有効化
- サービスアカウントを作成し、認証情報をダウンロード
- ダウンロードしたJSONファイルをプロジェクトのルートディレクトリに配置

## 使用方法

1. アプリケーションを起動
```bash
uvicorn app.main:app --reload
```

2. LINE Messaging APIの設定
- LINE Developersコンソールでチャネルを作成
- Webhook URLを設定（例：https://your-domain.com/webhook）
- チャネルアクセストークンとチャネルシークレットを取得し、.envファイルに設定

3. キーワードの送信
- LINEアプリからボットにキーワードを送信
- 自動的に検索結果がスプレッドシートに記録され、URLが返信されます

## デプロイ（Render）

1. Renderで新しいWebサービスを作成
2. GitHubリポジトリと連携
3. 環境変数を設定
4. ビルドコマンドとスタートコマンドを設定
   - ビルドコマンド: `pip install -r requirements.txt`
   - スタートコマンド: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 注意事項

- Zenserp APIの無料プランは月間50リクエストまで
- APIキーは必ず環境変数で管理
- 本番環境では適切なセキュリティ設定を行うこと
