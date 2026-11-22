import argparse
import json
import os
from pathlib import Path
import re
import shutil
from html import escape

ROOT = Path(__file__).resolve().parent
args = argparse.ArgumentParser()
args.add_argument("--output", type=Path, default=ROOT / "site")
OUT = args.parse_args().output.resolve()
DATA = ROOT / "content"
def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

settings = read(DATA / "settings.json")
sections = [(row["slug"], row["title"], row["description"], []) for row in read(DATA / "sections.json")]
categories_by_section = {row[0]:row[3] for row in sections}
entries = {}
for collection in ("pages","programs","consulting","projects","insights","instructors"):
    for path in sorted((DATA / collection).glob("*.json")):
        item = read(path)
        section = item["section"] if collection == "pages" else "about" if collection == "instructors" else collection
        route = (section,item["category"],item["slug"])
        if not all(re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", part) for part in route):
            raise ValueError(f"Invalid URL fields in {path}")
        if route in entries:
            raise ValueError(f"Duplicate route: {route}")
        entries[route] = item
        categories_by_section[section].append((item["category"],item["category_title"],item["slug"],item["title"],item["summary"],[(block["heading"],block["text"]) for block in item.get("body",[])]))

def unique_categories(categories):
    return list({cat[0]:cat for cat in categories}.values())

theme = {"navy":"", "teal":":root{--navy:#104f48}"}
fonts = {"noto":"", "system":":root{font-family:system-ui,'Malgun Gothic',sans-serif}"}

BRAND = '<i></i><span>ARAIN <b>SIGHT</b><small>아라인사이트</small></span>'
MOBILE = """<script>
const mobileMenu = document.querySelector('.mobile');
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && mobileMenu.open) {
    mobileMenu.open = false;
    mobileMenu.querySelector('summary').focus();
  }
});
</script>"""
OUT.mkdir(parents=True,exist_ok=True)
(OUT / "style.css").write_text((ROOT / "style.css").read_text(encoding="utf-8") + "\n" + theme[settings["theme"]] + fonts[settings["font"]],encoding="utf-8")
shutil.copytree(ROOT / "images", OUT / "images", dirs_exist_ok=True)

def url(current, *route):
    return Path(os.path.relpath(OUT.joinpath(*route, "index.html"), current)).as_posix()

def href(path, label, cls=""):
    styling = f' class="{cls}"' if cls else ""
    return f'<a{styling} href="{path}">{escape(label)}</a>'

def render_header(current):
    logo = f'<a class="brand" href="{url(current)}" aria-label="아라인사이트 홈">{BRAND}</a>'
    desktop = []
    mobile = []
    for slug, title, _, categories in sections:
        category_links = "".join(href(url(current,slug,cat), name) for cat,name,*_ in unique_categories(categories))
        top = href(url(current,slug),title,"navcta" if slug=="contact" else "")
        desktop.append(f'<div class="nav-item">{top}<details class="submenu"><summary aria-label="{title} 하위 메뉴">⌄</summary><div>{category_links}</div></details></div>')
        mobile.append(f'<details><summary>{title}</summary><div>{href(url(current,slug),title+" 전체")}{category_links}</div></details>')
    return f'<header class="shell top">{logo}<nav aria-label="주 메뉴">{"".join(desktop)}</nav><details class="mobile"><summary>메뉴</summary><div>{"".join(mobile)}</div></details></header>'

def cards(current, rows, kind=""):
    elements = []
    for index, (route,title,description,tag) in enumerate(rows):
        item = entries.get(route,{})
        picture = photo(current,item["image"],"thumb",item.get("image_alt","")) if item.get("image") else ""
        category = f' data-tag="{escape(tag)}" data-title="{escape(title)}"' if tag else ""
        elements.append(f'<article{category} class="crop-{index+1}">{picture}<h2>{escape(title)}</h2><p>{escape(description)}</p>{href(url(current,*route),"자세히 보기 ↗","read-more")}</article>')
    return '<div class="inner-grid">'+"".join(elements)+'</div>'

def asset(current, value):
    if not isinstance(value,str) or not value.startswith("/images/"):
        raise ValueError(f"Invalid CMS image: {value}")
    path = (OUT / value.lstrip("/")).resolve()
    if not path.is_relative_to(OUT / "images") or not path.is_file():
        raise ValueError(f"Missing or invalid CMS image: {value}")
    from urllib.parse import quote
    return quote(Path(os.path.relpath(path,current)).as_posix())

def photo(current, value, cls="", alt="", lazy=True):
    return f'<img class="{cls}" src="{asset(current,value)}" alt="{escape(alt,quote=True)}"'+(' loading="lazy"' if lazy else '')+'>'

def crumb(current, trail):
    links = [href(url(current),"홈")]
    links += [href(url(current,*route),title) for route,title in trail[:-1]]
    links += [f'<span aria-current="page">{escape(trail[-1][1])}</span>']
    return '<nav aria-label="현재 위치" class="crumb">'+' <span aria-hidden="true">/</span> '.join(links)+'</nav>'

def write(route, trail, title, description, body):
    current = OUT.joinpath(*route)
    current.mkdir(parents=True,exist_ok=True)
    css = Path(os.path.relpath(OUT / "style.css",current)).as_posix()
    meta = escape(f"{title} | 아라인사이트",quote=True)
    desc = escape(description,quote=True)
    page = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{meta}</title><meta name="description" content="{desc}"><meta property="og:title" content="{meta}"><meta property="og:description" content="{desc}"><meta property="og:type" content="website">
<link rel="stylesheet" href="{css}"></head><body>
<a class="skip" href="#main">본문 바로가기</a>{render_header(current)}
<main id="main" class="shell inner">{crumb(current,trail)}<header class="page-title"><h1>{escape(title)}</h1><p>{escape(description)}</p></header>{body}</main>
<footer class="shell"><a class="brand" href="{url(current)}">{BRAND}</a><p>기업과 교육기관을 위한 AI 실무교육 · 마케팅 · 컨설팅</p>{href(url(current,"contact"),"문의하기 ↗")}</footer>{MOBILE}</body></html>'''
    (current / "index.html").write_text(page,encoding="utf-8")

def filters(categories):
    options = ''.join(f'<option value="{escape(cat[1])}">{escape(cat[1])}</option>' for cat in unique_categories(categories))
    return f'''<div class="filter"><label>분야 <select id="category"><option value="">전체</option>{options}</select></label>
<label>제목 검색 <input id="query" type="search"></label><p id="filter-count" role="status"></p></div>
<script>
const category = document.querySelector('#category');
const query = document.querySelector('#query');
const entries = document.querySelectorAll('article[data-tag]');
function filter() {{
  let count = 0;
  for (const entry of entries) {{
    entry.hidden = Boolean(category.value && entry.dataset.tag !== category.value) ||
      !entry.dataset.title.toLowerCase().includes(query.value.trim().toLowerCase());
    if (!entry.hidden) count++;
  }}
  document.querySelector('#filter-count').textContent = count ? count + '개 항목' : '조건에 맞는 항목이 없습니다.';
}}
category.addEventListener('change',filter);
query.addEventListener('input',filter);
filter();
</script>'''

def contact_panel(kind):
    return f'''<p class="notice" id="contact-status"><strong>접수 준비 중</strong> · {escape(settings["contact_status"])}</p>
<section class="contact-fields" aria-labelledby="contact-items">
<h2 id="contact-items">상담 신청에 필요한 항목</h2>
<dl><dt>상담 유형</dt><dd>{escape(kind)}</dd><dt>기관·담당자</dt><dd>기관명, 담당자명, 이메일, 휴대전화</dd>
<dt>교육 정보</dt><dd>교육 대상 및 인원, 희망 일정</dd><dt>요청사항</dt><dd>문의 내용, 개인정보 수집·이용 동의</dd></dl></section>'''

related = {"corporate":("corporate-ai","custom-training","기업 AI 교육"),"marketing":("marketing-md","practical-training","AI 마케팅·MD"),"career":("young-careers","job-portfolio","청년 취업")}
for slug,title,description,categories in sections:
    current = OUT / slug
    parent = [((slug,),title)]
    show_entries = slug in ("projects","insights")
    rows = [((slug,cat,entry),name,summary,cat_title) if show_entries else ((slug,cat),cat_title,summary,"")
            for cat,cat_title,entry,name,summary,_ in (categories if show_entries else unique_categories(categories))]
    faq = ""
    if slug == "contact":
        questions = [read(path) for path in sorted((DATA / "faq").glob("*.json"))]
        faq = '<section class="article-body"><h2>자주 묻는 질문</h2>'+''.join(f'<details><summary>{escape(item["title"])}</summary><p>{escape(item["answer"])}</p></details>' for item in questions)+'</section>'
    write((slug,),parent,title,description,(filters(categories) if show_entries else "")+cards(current,rows,slug)+faq)
    for index,(category,cat_title,entry,name,summary,blocks) in enumerate(categories):
        current = OUT / slug / category
        middle = [*parent,((slug,category),cat_title)]
        listing = cards(current,[((slug,category,other),other_name,other_summary,"") for cat,_,other,other_name,other_summary,_ in categories if cat==category])
        write((slug,category),middle,cat_title,summary,listing)
        current = current / entry
        sections_html = ''.join(f'<section><h2>{escape(label)}</h2><p>{escape(value)}</p></section>' for label,value in blocks)
        extra = ""
        item = entries[(slug,category,entry)]
        if slug == "projects" and item.get("sample"):
            extra += '<p class="notice">샘플 프로젝트</p>'
        if slug == "insights":
            date = item.get("date","")
            label = "게시 예시 · " if item.get("sample") else ""
            extra += '<p class="notice">'+escape(label + (date or "게시일 미정"))+'</p>'
        if item.get("image"):
            extra += f'<figure class="inner-photo">{photo(current,item["image"],alt=item.get("image_alt",""))}</figure>'
        if item.get("gallery"):
            extra += '<div class="inner-grid">'+''.join(photo(current,image,alt=name+" 추가 사진") for image in item["gallery"])+'</div>'
        extra += f'<div class="article-body">{sections_html}</div>'
        if slug == "projects" and category in related:
            pslug,pentry,ptitle = related[category]
            if ("programs",pslug,pentry) in entries:
                extra += href(url(current,"programs",pslug,pentry),"관련 프로그램 · "+ptitle,"button plain")
        if slug in ("projects","insights") and len(categories)>1:
            ncat,_,nentry,ntitle,*_ = categories[(index+1)%len(categories)]
            label = "다음 프로젝트" if slug=="projects" else "관련 인사이트"
            extra += f'<div class="related">{href(url(current,slug,ncat,nentry),label+" · "+ntitle,"read-more")}</div>'
        if slug in ("programs","consulting"):
            contact_route = ("education","custom-request") if slug=="programs" else ("consulting","project-request")
            extra += href(url(current,"contact",*(contact_route if ("contact",*contact_route) in entries else ())),"상담 안내 보기 ↗","button")
        if slug=="contact":
            extra += contact_panel(cat_title)
        write((slug,category,entry),[*middle,((slug,category,entry),name)],name,summary,extra)
home = (ROOT / "home.html").read_text(encoding="utf-8")
home = re.sub(r'<header class="shell top">.*?</header>',render_header(OUT),home,count=1,flags=re.S)
for slug,*_ in sections:
    home = home.replace(f'href="#{slug}"',f'href="./{slug}/index.html"')
def replace_fragment(pattern, html):
    global home
    home = re.sub(pattern,lambda _:html,home,count=1,flags=re.S)

def listing(slug, limit=None):
    section_entries = categories_by_section[slug]
    if slug == "insights":
        section_entries = sorted(section_entries,key=lambda row:entries[(slug,row[0],row[2])].get("date") or "",reverse=True)
    return cards(OUT,[((slug,cat,entry),title,summary,"") for cat,_,entry,title,summary,_ in section_entries[:limit]],slug)

original_headline = 'AI를 배우는 시간을 넘어, 실무의 변화를 만듭니다.'
headline = settings["headline"]
marked_headline = 'AI를 배우는 시간을 넘어,<br><em>실무의 변화를</em><br>만듭니다.' if headline == original_headline else escape(headline)
replace_fragment(r'(<h1 id="headline">).*?</h1>',f'<h1 id="headline">{marked_headline}</h1>')
replace_fragment(r'<p class="intro">.*?</p>',f'<p class="intro">{escape(settings["intro"])}</p>')
hero_image = photo(OUT,settings["hero_image"],"hero-img",settings.get("hero_alt",""),lazy=False) if settings.get("hero_image") else ""
replace_fragment(r'<figure>.*?</figure>',f'<figure>{hero_image}<figcaption><span>아라인사이트 · 실무교육</span><span>{escape(settings.get("hero_caption",""))}</span></figcaption></figure>')
replace_fragment(r'<div class="expert-grid">.*?</div></section>',listing("programs",5)+'</section>')
replace_fragment(r'<div class="program-grid">.*?</div><aside',listing("programs",5)+'<aside')
replace_fragment(r'<article class="feature">.*?</article>',listing("projects",3))
replace_fragment(r'<div class="insight-grid">.*?</div></section>',listing("insights",3)+'</section>')
replace_fragment(r'<h2>우리 조직에 필요한 교육,.*?</h2>',f'<h2>{escape(settings["contact_heading"])}</h2>')
home = home.replace('./contact/education/custom-request/index.html', './contact/index.html')
home = re.sub(r'<script>.*?</script>',MOBILE,home,count=1,flags=re.S)
(OUT / "index.html").write_text(home,encoding="utf-8")
print(f"Built {len(list(OUT.rglob('index.html')))} pages in {OUT}")
