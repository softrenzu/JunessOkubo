#!/usr/bin/env python3
"""Build blog pages and publish one new article per Japanese calendar day."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import re
import sys
import urllib.request
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape as xe

ROOT=Path(__file__).resolve().parents[1]
POSTS=ROOT/"data"/"posts.json"
BLOG=ROOT/"blog"
SITE=os.getenv("SITE_URL","https://jeunesse-okubo.onrender.com").rstrip("/")
BOOK="https://upnow.jp/goodspace/jeunesse"
TOPICS=[
("貸切パーティー","人数と利用時間","食事やゲーム","片付け"),
("映画鑑賞会","作品の選び方","座る位置","音量への配慮"),
("ボードゲーム会","ルールの確認","チーム分け","休憩"),
("誕生日会","主役の好み","サプライズ演出","片付け"),
("歓送迎会","参加者の案内","当日の進行","記念撮影"),
("推し活イベント","テーマ設定","映像の準備","著作権の確認"),
("女子会","人数と持ち物","食事と会話","時間配分"),
("交流会","自己紹介","話題の準備","座席配置"),
("ワークショップ","目的の整理","資料と設備","振り返り"),
("写真撮影会","撮影テーマ","照明と背景","備品の原状回復"),
("動画撮影会","撮影の順番","照明と音","撤収の段取り"),
("食事会","食事の手配","テーブルの配置","ゴミ処理"),
("勉強会","議題の共有","資料の投影","休憩"),
("ミニ上映会","再生機材","画面の見え方","上映権"),
("オフ会","参加者への案内","当日の流れ","記念写真"),
("同窓会","出欠確認","交流の時間","写真の共有"),
("カードゲーム会","ゲームの選択","席の配置","時間管理"),
("小規模ミーティング","議題設定","説明の順番","議事録"),
("記念日パーティー","テーマの検討","写真と演出","片付け"),
("クイズ大会","問題づくり","進行と採点","表彰"),
("撮影ワークショップ","構図の検討","小道具","データの整理"),
("週末の集まり","集合時間","食事の確認","退出時間"),
("推しの誕生日会","色と装飾","記念撮影","原状回復"),
("新大久保でのオフ会","集合場所","参加者の連絡","周辺への配慮"),
("ホームパーティー","企画内容","食事とゲーム","掃除"),
("プレゼン練習","発表時間","画面の確認","講評"),
("小規模セミナー","目的と参加者","設備と資料","質疑"),
("映画の感想会","題材の選択","感想の共有","休憩"),
("ゲーム初心者の会","ルール説明","経験の差","休憩"),
("サークルの集まり","出席人数","進行と役割分担","夜間ルール"),
("友人同士の撮影企画","撮りたい写真","背景の用意","撤収"),
("交流パーティー","参加者への案内","会話のきっかけ","片付け"),
("小さな祝賀会","お祝いの目的","食事と進行","写真撮影"),
("読書会","本の共有","話す順番","感想"),
("イベント幹事の準備","役割分担","時間割","退出手順"),
("新大久保での集まり","駅とアクセス","会場選び","参加者への案内")
]
ANGLES=["最初に決めたい3つのこと","幹事が確認するポイント","当日の段取り","参加者が楽しむための工夫","初めてでも進めやすい準備","会場づくりのコツ"]
def esc(s): return html.escape(str(s),quote=True)
def read(): return json.loads(POSTS.read_text(encoding="utf-8"))
def fallback(topic,angle,today,index):
    name,a,b,c=topic
    return {"date":today,"slug":today+"-idea-"+str(index),"category":"IDEAS",
      "title":name+"｜"+angle,
      "summary":name+"を計画するときに役立つ「"+a+"」「"+b+"」「"+c+"」を紹介します。",
      "intro":name+"を楽しく開催するには、会場を予約するだけでなく、当日の流れを少し決めておくことが役立ちます。今回は"+angle+"をテーマに、貸切スペースでの集まりの準備を整理します。",
      "sections":[
       {"heading":"まずは"+a+"を確認","body":"集まる目的に合わせて、最初に"+a+"を考えましょう。参加者がわかりやすいよう、日時・場所・予定を早めに共有します。全員が同じ時間に集まれるとは限らないため、開始直後の進行には余裕を持たせると安心です。"},
       {"heading":"次に"+b+"を準備","body":b+"については、参加者の好みや経験も考慮しておきましょう。ジュネス新大久保には65型テレビ、プロジェクター、Wi-Fi、ボードゲームなどが掲載されています。使いたい設備やオプションは、予約前に最新の掲載内容と利用条件を確認してください。"},
       {"heading":"最後に"+c+"を意識","body":c+"を意識した時間割にしておくと、イベントの終了時も慌てずにすみます。周囲に配慮して音量を管理し、ゴミと片付けの規定を確認しましょう。最大30名で利用できますが、21時から翌9時までは10名以下での利用が必要です。"}],
      "closing":"利用条件や料金は変更されることがあります。ジュネス新大久保の空室情報は公式予約ページでご確認ください。"}
def ai_post(topic,angle,today,index):
    token=os.getenv("OPENAI_API_KEY","").strip()
    if not token: return None
    prompt=("新大久保の貸切スペースの日本語ブログを実用的で具体的に執筆する。"
      "JSONオブジェクトのみ返す。キーはtitle,summary,intro,sections,closing。"
      "sectionsはheadingとbodyの組み合わせ4個。各本文は日本語150文字以上。"
      "確認済み施設情報: ジュネス新大久保101。東京都新宿区大久保2-21-10。最大30名、約45㎡、65型テレビ、プロジェクター、Wi-Fi、ボードゲーム。"
      "21時から翌9時は10名以下。ハンモック撤去済み。"
      "料金、空き状況、現在のキャンペーン、イベント、口コミ、ニュース、未確認の設備や近隣店舗の情報を創作しない。"
      "著作権と近隣への配慮を促す。SEO目的の単語の羅列をしない。既存文章の複製は禁止。"
      "読者が実際に役立てられる独自の具体例を入れ、最後に施設の公式upnow予約ページへの自然な案内を入れる。"
      "公式予約先は https://upnow.jp/goodspace/jeunesse。"
      +"テーマ:"+topic[0]+"。角度:"+angle+"。ポイント:"+",".join(topic[1:])+"。")
    try:
        data=json.dumps({"model":os.getenv("OPENAI_MODEL","gpt-4.1-mini"),
          "messages":[{"role":"system","content":"正確性を最優先する日本語のイベント企画ライター。JSONのみ出力。"},
                      {"role":"user","content":prompt}],
          "response_format":{"type":"json_object"}}).encode("utf-8")
        request=urllib.request.Request("https://api.openai.com/v1/chat/completions",
          data=data,headers={"Content-Type":"application/json","Authorization":"Bearer "+token},method="POST")
        with urllib.request.urlopen(request,timeout=80) as response:
            obj=json.loads(json.loads(response.read().decode("utf-8"))["choices"][0]["message"]["content"])
        sections=obj["sections"]
        if not isinstance(sections,list) or not 3<=len(sections)<=6:raise ValueError("sections")
        if any(len(str(s.get("body","")))<70 for s in sections):raise ValueError("too short")
        result={k:str(obj[k])[:1500] for k in ("title","summary","intro","closing")}
        result.update({"date":today,"slug":today+"-idea-"+str(index),"category":"IDEAS",
          "sections":[{"heading":str(s["heading"])[:90],"body":str(s["body"])[:1700]} for s in sections]})
        return result
    except Exception as error:
        print("API failed, using editorial template:",error,file=sys.stderr)
        return None
def shell(title,desc,body,canonical):
    return """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#15362f"><meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}"><link rel="stylesheet" href="/styles.css">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><title>{title} | ジュネス新大久保</title></head>
<body><header><div class="wrap nav"><a class="brand" href="/"><b class="mark">J.</b><span>JEUNESSE<small>SHIN-OKUBO 101</small></span></a>
<nav><a href="/">スペース紹介</a><a href="/blog/">ブログ</a><a href="/#access">アクセス</a></nav><a class="pill dark" href="{book}">予約ページ ↗</a></div></header>
{body}<footer><div class="wrap foot"><a class="brand" href="/"><b class="mark">J.</b><span>JEUNESSE<small>SHIN-OKUBO 101</small></span></a>
<div><a href="/">トップ</a><a href="/blog/">ブログ</a><a href="{book}">予約</a></div><small>© JEUNESSE SHIN-OKUBO. 最新の利用条件を予約ページでご確認ください。</small></div></footer></body></html>""".format(title=esc(title),desc=esc(desc),canonical=esc(canonical),book=BOOK,body=body)
def article(p):
    sections="".join("<section><h2>"+esc(s["heading"])+"</h2><p>"+esc(s["body"])+"</p></section>" for s in p["sections"])
    body=("<main class='article'><div class='crumb'><a href='/'>TOP</a> / <a href='/blog/'>BLOG</a></div>"
        +"<span class='tag'>"+esc(p["category"])+"</span><h1>"+esc(p["title"])+"</h1>"
        +"<time datetime='"+esc(p["date"])+"'>"+esc(p["date"])+"</time>"
        +"<p class='intro'>"+esc(p["intro"])+"</p>"+sections
        +"<p class='ending'>"+esc(p["closing"])+"</p>"
        +"<div class='disclaimer'>記事は一般的な企画のヒントです。設備・利用条件・料金は変更されることがあります。</div>"
        +"<div class='cta'><h2>次の集まりは、ジュネス新大久保で。</h2>"
        +"<p>最新の空室・料金・利用条件は公式予約ページから。</p>"
        +"<a class='pill coral' href='"+BOOK+"' target='_blank' rel='noopener noreferrer'>upnowで予約する ↗</a></div></main>")
    data={"@context":"https://schema.org","@type":"BlogPosting","headline":p["title"],
          "datePublished":p["date"],"description":p["summary"],"inLanguage":"ja"}
    body+="<script type='application/ld+json'>"+json.dumps(data,ensure_ascii=False).replace("<","\\u003c")+"</script>"
    return shell(p["title"],p["summary"],body,SITE+"/blog/"+p["slug"]+".html")
def listing(posts):
    cards=[]
    for p in posts:
        cards.append("<a class='post' href='/blog/"+esc(p["slug"])+".html'>"
          +"<span class='category'>"+esc(p["category"])+"</span><h3>"+esc(p["title"])+"</h3>"
          +"<p>"+esc(p["summary"])+"</p><time datetime='"+esc(p["date"])+"'>"+esc(p["date"])+"</time></a>")
    body="<main><section class='blog-hero'><div class='wrap'><span class='tag'>THE JOURNAL</span><h1>集まる時間を、<em>もっと楽しく。</em></h1><p>パーティー・撮影・イベントの企画に役立つアイデアを毎日更新します。</p></div></section><section class='wrap blog-wrap'><div class='post-grid'>"+''.join(cards)+"</div></section></main>"
    return shell("ブログ記事一覧","ジュネス新大久保のパーティー・撮影・イベントのヒント。",body,SITE+"/blog/")
def build(posts):
    BLOG.mkdir(exist_ok=True)
    posts.sort(key=lambda p:p["date"],reverse=True)
    for p in posts:
        if not re.fullmatch("[a-z0-9-]{1,90}",p["slug"]):raise ValueError("Invalid slug")
        (BLOG/(p["slug"]+".html")).write_text(article(p),encoding="utf-8")
    (BLOG/"index.html").write_text(listing(posts),encoding="utf-8")
    routes=[("/",posts[0]["date"] if posts else None),("/blog/",posts[0]["date"] if posts else None)]
    routes.extend(("/blog/"+p["slug"]+".html",p["date"]) for p in posts)
    sitemap=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path,date in routes:
        sitemap.append("<url><loc>"+xe(SITE+path)+"</loc>"+("<lastmod>"+date+"</lastmod>" if date else "")+"</url>")
    sitemap.append("</urlset>")
    (ROOT/"sitemap.xml").write_text("\n".join(sitemap)+"\n",encoding="utf-8")
    feed=['<?xml version="1.0" encoding="UTF-8"?>','<rss version="2.0"><channel><title>ジュネス新大久保 BLOG</title><link>'+SITE+'</link><description>集まりのアイデア</description><language>ja</language>']
    for p in posts[:40]:
        url=SITE+"/blog/"+p["slug"]+".html"
        feed.append("<item><title>"+xe(p["title"])+"</title><link>"+url+"</link><guid>"+url+"</guid><description>"+xe(p["summary"])+"</description></item>")
    feed.append("</channel></rss>")
    (ROOT/"feed.xml").write_text("\n".join(feed)+"\n",encoding="utf-8")
    print("Built",len(posts),"articles")
def daily():
    today=dt.datetime.now(ZoneInfo("Asia/Tokyo")).date().isoformat()
    posts=read()
    if any(p["date"]==today for p in posts):
        print("Today's post already exists")
        return build(posts)
    delta=(dt.date.fromisoformat(today)-dt.date(2026,11,24)).days
    if delta<0:return build(posts)
    i=delta%len(TOPICS)
    topic=TOPICS[i]
    angle=ANGLES[(delta//len(TOPICS))%len(ANGLES)]
    generated=ai_post(topic,angle,today,i)
    if generated is None:
        print("ARTICLE_SOURCE=editorial_template; OpenAI API key missing or request failed",file=sys.stderr)
        generated=fallback(topic,angle,today,i)
        generated["generation_source"]="editorial_template"
    else:
        print("ARTICLE_SOURCE=openai_api")
        generated["generation_source"]="openai_api"
    posts.insert(0,generated)
    POSTS.write_text(json.dumps(posts,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    build(posts)
if __name__=="__main__":
    command=sys.argv[1] if len(sys.argv)>1 else "build"
    if command not in ("build","daily"):raise SystemExit("Specify build or daily")
    daily() if command=="daily" else build(read())
