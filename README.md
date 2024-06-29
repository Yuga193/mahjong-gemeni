# Django Mahjong AI

このプロジェクトは、Djangoを使用して麻雀の手牌分析を行うAIアプリケーションです。ユーザーは手牌を入力し、AIが最適な捨て牌を提案します。

## 技術スタック
- **フレームワーク:** Django 3.2
- **言語:** Python 3.8
- **外部API:** Google Generative AI
- **フロントエンド:** HTML, CSS, JavaScript

## セットアップ手順
1. **リポジトリのクローン:**
   ```
   git clone [リポジトリURL]
   cd Django_mahjong
   ```
2. **依存関係のインストール:**
   ```
   pip install -r requirements.txt
   ```
3. **環境変数の設定:**
   `.env` ファイルに `GOOGLE_API_KEY` を設定してください。このキーは、Google Generative AIを使用するために必要です。
   ```
   GOOGLE_API_KEY="あなたのAPIキー"
   ```
4. **データベースのマイグレーション:**
   ```
   python manage.py migrate
   ```
5. **開発サーバーの起動:**
   ```
   python manage.py runserver
   ```
   ブラウザで [http://127.0.0.1:8000/](http://127.0.0.1:8000/) にアクセスしてアプリケーションを使用します。
