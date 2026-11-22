# ジュネス新大久保101 - 公式紹介・毎日更新ブログ

東京都新宿区大久保2-21-10 ジュネスŌKUBO 101のレンタルスペース公式案内サイトです。

## URL

- 公開サイト: https://jeunesse-okubo.onrender.com/
- ブログ: https://jeunesse-okubo.onrender.com/blog/
- 公式予約: https://upnow.jp/goodspace/jeunesse

## 毎日自動投稿

GitHub Actionsで日本時間の毎朝9時12分に実行する設定です。GitHub側の都合で遅延する場合があります。

1. Pythonの scripts/blog.py daily が日本の日付を確認します。
2. 記事がまだない場合、その日のテーマで新しい記事を生成します。
3. data/posts.json、個別HTMLページ、記事一覧、sitemap.xml、feed.xmlを更新します。
4. GitHub Actionsが更新をコミット・プッシュします。
5. Renderで自動デプロイされます。同じ日の二重投稿は防止します。

OpenAI APIを使う場合は、GitHubリポジトリのSettings > Secrets and variables > Actionsに、OPENAI_API_KEYを登録してください。別途API利用料が発生する場合があります。生成モデルはgpt-4.1-miniです。

APIキー未設定時や通信障害時には、36の事前準備テーマと6つの切り口を組み合わせた編集テンプレートを使用し、記事を生成します。これはAIによる自由生成ではありません。記事品質を定期的に確認し、独自性や事実関係を改善してください。

GitHub Actionsでワークフローが有効か、必要なcontents: write権限があるか確認してください。GitHub Modelsは2026年7月に終了したため利用しません。

## ビルド

Render static site。Publish Pathはpublic、Auto Deployはyes。

Build Command:
    python3 scripts/blog.py build && mkdir -p public && cp index.html styles.css app.js favicon.svg robots.txt sitemap.xml feed.xml public/ && cp -R data blog public/

ローカルプレビュー:
    python3 scripts/blog.py build
    python3 -m http.server 8000

## 情報の扱い

最大30名、約45㎡、65型テレビ、プロジェクター、Wi-Fi、ボードゲーム等は物件の予約サイトに記載されている情報です。21時から翌9時は10名以下という利用制限があります。

掲載画像は予約プラットフォームの画像URLを参照しています。過去画像に撤去済みハンモックが写ることがあるため、最新写真への更新が望まれます。画像の著作権・使用権も運営者側でご確認ください。料金・キャンペーン・空室・備品は常に公式予約ページを優先してください。

SEO成果を保証するものではなく、自動生成記事だけを量産するよりも、現地での体験や写真に基づく記事の拡充が重要です。
