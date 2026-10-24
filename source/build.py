"""Build the bilingual static website. Python 3 standard library only.
Edit content.json / cases.json / privacy.json / site-config.json, then run this file.
Use --production only after completing the launch configuration.
"""
from pathlib import Path
import json,re,html,sys,shutil,os
from urllib.parse import quote,urlparse
R=Path(__file__).resolve().parent.parent; S=R/'source'; D=R/'dist'
C=json.loads((S/'content.json').read_text(encoding='utf-8')); K=json.loads((S/'site-config.json').read_text(encoding='utf-8'))
CASES=json.loads((S/'cases.json').read_text(encoding='utf-8')); PRIV=json.loads((S/'privacy.json').read_text(encoding='utf-8'))
DIMENSIONS=json.loads((S/'asset-dimensions.json').read_text(encoding='utf-8'))
RESPONSIVE=json.loads((S/'responsive-images.json').read_text(encoding='utf-8'))
for variable,key in [('ORVEN_SITE_URL','site_url'),('ORVEN_FORM_ENDPOINT','form_endpoint'),('ORVEN_TURNSTILE_SITE_KEY','turnstile_site_key')]:
 if os.environ.get(variable):K[key]=os.environ[variable]
PROD='--production' in sys.argv
if PROD:
 required=['site_url','whatsapp','hosting_provider','data_controller','retention_period']
 missing=[x for x in required if not K.get(x)]
 if not K.get('privacy_reviewed'): missing.append('privacy_reviewed')
 if K.get('form_endpoint') and not K.get('form_provider'): missing.append('form_provider')
 if not re.fullmatch(r'https://[^/]+',K.get('site_url','').rstrip('/')): missing.append('valid HTTPS site_url')
 if not re.fullmatch(r'[1-9][0-9]{7,14}',K.get('whatsapp','')): missing.append('E.164 WhatsApp digits without +')
 if missing: sys.exit('Launch blocked: '+', '.join(missing))
 if K.get('analytics'): sys.exit('Analytics requires a reviewed consent implementation before activation.')
ORIGIN=K['site_url'].rstrip('/') if K['site_url'] else 'http://127.0.0.1:8770'
D.mkdir(exist_ok=True)
for temporary in ['og-en.preview.html','og-ar.preview.html','review.html','assets/og-en.png','assets/og-ar.png']:
 temp=D/temporary
 if temp.is_file():temp.unlink()
shutil.copytree(R/'assets',D/'assets',dirs_exist_ok=True)
for f in ['tokens.css','site.css','site.js']: shutil.copy2(R/f,D/f)
def t(x,l): return x.get(l,'') if isinstance(x,dict) else str(x or '')
def e(x): return html.escape(str(x),quote=True)
def L(k,l): return t(C['labels'][k],l)
def path(k,l): return '/'+l+'/'+(('work/'+k+'/') if k in CASES else (k+'/' if k!='home' else ''))
def link(text,url,cls='',external=False,attrs=''):
 return f'<a class="{cls}" href="{e(url)}"'+(' target="_blank" rel="noopener noreferrer"' if external else '')+f' {attrs}>{text}<span class="arrow" aria-hidden="true">↗</span></a>'
def channel(k,l,cls='btn secondary'):
 txt=L(k,l)
 if k=='email': return link(txt,'mailto:'+K['email'],cls)
 if K['whatsapp']:
  msg=t({'en':"Hello ORVEN, I'd like to arrange a suitable time for a call." if k=='call' else "Hello ORVEN, I'd like to discuss a project.",'ar':'مرحبًا ORVEN، أرغب في تنسيق موعد مناسب لمكالمة.' if k=='call' else 'مرحبًا ORVEN، أرغب في مناقشة مشروع.'},l)
  return link(txt,'https://wa.me/'+(K.get('call_number') if k=='call' else K['whatsapp'])+'?text='+quote(msg),cls,True)
 return f'<button class="{cls}" type="button" data-unavailable="{e(L("notReady",l))}">{txt}<span class="arrow" aria-hidden="true">↗</span></button>'
def actions(keys,l):
 out=[]
 for x in keys:
  if x in ['whatsapp','email','call']: out.append(channel(x,l))
  else: out.append(link(L(x,l),path('contact' if x=='start' else 'work',l),'btn' if x=='start' else 'btn secondary'))
 return '<div class="actions">'+''.join(out)+'</div>'
def hero_lines(text):
 # Authored hero lines get a clipping wrapper so CSS can reveal them on load; the text and line breaks stay as written.
 return '<br>'.join(f'<span class="hl"><span style="--i:{i}">{e(x)}</span></span>' for i,x in enumerate(text.split('\n')))
def intro(s,l,i,hero=False):
 tag='h1' if hero else 'h2'
 title=e(t(s['title'],l)).replace('\n','<br>') if not hero else hero_lines(t(s['title'],l))
 return f'<div class="section-head"><div><p class="eyebrow">{i:02d} / {e(t(s.get("label"),l))}</p><{tag}>{title}</{tag}></div>'+ (f'<p class="intro muted">{e(t(s.get("body"),l))}</p>' if s.get('body') else '')+'</div>'
def image_options(src, sizes):
 variants=RESPONSIVE.get(src,[])
 return (' srcset="'+', '.join('/assets/'+x['src']+' '+str(x['width'])+'w' for x in variants)+'" sizes="'+sizes+'" decoding="async"') if variants else ''

# Keep the complete authored CSS in the first response: no render-blocking CSS round trip.
# Source CSS stays editable; only comments and repeated whitespace are removed.
INLINE_CSS=' '.join(re.sub(r'/\*.*?\*/','',(R/f).read_text(encoding='utf-8'),flags=re.S).replace("url('assets/", "url('/assets/") for f in ['tokens.css','site.css'])
INLINE_CSS=re.sub(r'\s+',' ',INLINE_CSS).strip()

def projects(l,home):
 out='<div class="projects-grid">'
 for k,p in C['projects'].items():
  out+=f'<article class="project"><a class="project-image {k}" href="{path(k,l)}" data-cursor="{L("cursorView",l)}" aria-label="{e(p["name"])} — {L("viewCase",l)}"><img src="/assets/{p["cover"][l]}" alt="{e(p["name"])} — {L("screen",l)}" width="1440" height="720" loading="lazy"{image_options(p["cover"][l], "(max-width: 760px) calc(100vw - 40px), (max-width: 1328px) calc((100vw - 176px) / 2), 576px")}></a><p class="project-sector">{e(t(p["sector"],l))}</p><h3>{e(p["name"])}</h3><p class="muted">{e(t(p["homeBody" if home else "body"],l))}</p>'+link(L('exploreCase' if home else 'viewCase',l),path(k,l),'text-link')+'</article>'
 return out+'</div><div class="work-bottom"><p class="muted">'+L('credit',l)+'</p>'+(link(L('allWork',l),path('work',l),'text-link') if home else '')+'</div>'
def review_text(r,l,a,b,cls):
 # Client words stay verbatim in Arabic; the English page adds a labelled faithful translation.
 out=f'<blockquote class="{cls}" lang="ar" dir="rtl">'+''.join('<p>'+e(x)+'</p>' for x in r['original'][a:b])+'</blockquote>'
 if l=='en': out+=('<p class="review-translation-label">'+L('translation',l)+'</p>' if a==0 else '')+'<div class="review-translation" lang="en">'+''.join('<p>'+e(x)+'</p>' for x in r['en'][a:b])+'</div>'
 return out
def review(key,name,sector,cls,l):
 r=C['review'][key];out='<article class="review"><p class="eyebrow">'+L('feedbackSummary',l)+'</p>'+review_text(r,l,0,1,cls)
 if len(r['original'])>1: out+='<details class="review-more"><summary><span class="more">'+L('readFull',l)+'</span><span class="less">'+L('showLess',l)+'</span><span class="sign" aria-hidden="true">+</span></summary>'+review_text(r,l,1,None,cls)+'</details>'
 return out+'<p class="review-name">'+name+'</p><p class="muted">'+t(sector,l)+'</p></article>'
def reviews(l):
 return '<div class="reviews-grid">'+review('spiky','Spiky',{'en':'Fitness & Nutrition Coaching','ar':'التدريب والتغذية'},'review-quote',l)+review('future','Future Interiors',{'en':'Engineering Supervision','ar':'الإشراف الهندسي'},'review-summary',l)+'</div><p class="review-note muted">'+L('credit',l)+'</p>'
def form(l):
 f=C['form']; q=lambda x:e(t(f[x],l)); out='<form id="inquiry" novalidate><div class="form-grid">'
 for key,typ,auto,maxlen in [('name','text','name',120),('contact','text','email',254)]:
  out+=f'<div class="field"><label for="{key}">{q(key)} <span aria-hidden="true">*</span></label><input id="{key}" name="{key}" type="{typ}" autocomplete="{auto}" maxlength="{maxlen}" placeholder="{q(key+"Placeholder")}" required aria-describedby="{key}-error"'+(' dir="auto"' if key=='contact' else '')+f'><p id="{key}-error" class="field-error"></p></div>'
 out+=f'<div class="field full"><label for="service">{q("service")} <span class="muted">({q("optional")})</span></label><select id="service" name="service"><option value="">{q("select")}</option>'
 for v,k in [('website',0),('application',1)]: out+=f'<option value="{v}">{e(t(C["pages"]["home"][2]["items"][k]["title"],l))}</option>'
 out+=f'</select></div><div class="field full"><label for="details">{q("details")} <span aria-hidden="true">*</span></label><textarea id="details" name="details" rows="5" maxlength="5000" placeholder="{q("detailsPlaceholder")}" required aria-describedby="details-error"></textarea><p id="details-error" class="field-error"></p></div></div>'
 out+=f'<div class="honeypot" aria-hidden="true"><label for="company_url">Website</label><input id="company_url" name="company_url" tabindex="-1" autocomplete="off"></div><p class="privacy-note">{q("privacy")} <a href="{path("privacy",l)}">{L("privacy",l)}</a></p>'
 if not K['form_endpoint']: out+='<p class="form-unavailable">'+q('unconfigured')+'</p>'
 out+='<div id="turnstile" class="verification"></div>'
 out+=f'<button class="btn" type="submit">{q("submit")}<span class="arrow" aria-hidden="true">↗</span></button><p id="form-status" role="status" aria-live="polite" tabindex="-1"></p></form>'
 return out
def marquee(l):
 # Trial strip behind content.json "marquee.enabled". Spiky thumbnails stay Arabic; Future Interiors follow the page language.
 m=C.get('marquee',{})
 if not m.get('enabled'):return ''
 items=''.join(f'<li><img src="/assets/thumbs/{x["thumb"].replace("{lang}",l)}" alt="{e(C["projects"][x["project"]]["name"])} — {L("screen",l)}" width="640" height="360" loading="lazy" decoding="async"></li>' for x in m['items'])
 return f'<div class="marquee" role="group" aria-label="{L("marquee",l)}"><div class="marquee-track"><ul class="marquee-set">{items}</ul><ul class="marquee-set" aria-hidden="true">{items}</ul></div></div>'
def render_section(s,l,i,page):
 kind=s['kind']; theme=s.get('theme',''); out=f'<section class="section {kind} {theme}" id="{s.get("id",kind+str(i))}" data-section="{page}-{i:02d}"><div class="wrap">'
 out+=intro(s,l,i,kind=='hero')
 if kind=='hero':
  out+=actions(s.get('actions',[]),l)
  if page=='home': out+='<div class="hero-foot"><span>'+t({'en':'Websites · Web applications','ar':'مواقع إلكترونية · تطبيقات ويب'},l)+'</span><span>'+t({'en':'Built with intention.','ar':'نبني بهدف واضح.'},l)+'</span></div>'
 elif kind=='projects': out+=projects(l,page=='home')
 elif kind=='reviews': out+=reviews(l)
 elif kind=='form': out+=form(l)
 elif kind=='faq':
  out+='<div class="faq-list">'+''.join(f'<details><summary>{e(t(a["title"],l))}<span aria-hidden="true">+</span></summary><p>{e(t(a["body"],l))}</p></details>' for a in s['items'])+'</div>'
 elif kind=='detail':
  out+='<ul class="capabilities">'+''.join('<li>'+e(t(x,l))+'</li>' for x in s['items'])+'</ul>'+link(e(t(s['cta'],l)),path('contact',l),'text-link')
  if s.get('examples'): out+='<div class="examples">'+''.join(link(p['name'],path(k,l),'text-link') for k,p in C['projects'].items())+'</div>'
 elif kind in ['cards','services','process','team','channels']:
  out+=f'<div class="grid {kind}-grid" style="--columns:{min(3,len(s["items"]))}">'
  for j,a in enumerate(s['items']):
   away=bool(a.get('status'))  # e.g. a co-founder who is temporarily unavailable
   member=kind=='team' and not away
   name=f'<span class="away-name">{e(t(a["title"],l))}</span>' if away else f'<span class="member-name">{e(t(a["title"],l))}</span>' if member else e(t(a["title"],l))
   out+=f'<article{" class=\"away\"" if away else " class=\"member\"" if member else ""}><span class="item-number">{j+1:02d}</span><h3>{name}</h3>'
   if 'role' in a: out+='<p class="role">'+e(t(a['role'],l))+'</p>'
   if away: out+='<p class="status"><span class="status-dot" aria-hidden="true"></span>'+e(t(a['status'],l))+'</p>'
   if a.get('body'): out+='<p class="muted">'+e(t(a['body'],l))+'</p>'
   if 'target' in a: out+=link(e(t(a['cta'],l)),'/'+l+'/'+a['target'],'text-link')
   if 'social' in a and K['linkedin'].get(a['social']): out+=link('LinkedIn',K['linkedin'][a['social']],'text-link',True)
   if 'channel' in a:
    out+=channel(a['channel'],l,'text-link channel-link')
    if a['channel']=='call' and K.get('call_number'):out+=link(t({'en':'Call Mohamed El-Hadidy','ar':'اتصل بمحمد الحديدي'},l),'tel:+'+K['call_number'],'text-link phone-link')
   out+='</article>'
  out+='</div>'
  if kind=='services': out+=link(L('allServices',l),path('services',l),'text-link section-link')
  if 'cta' in s: out+=link(e(t(s['cta'],l)),path('contact',l),'text-link section-link')
 elif kind=='cta': out+=actions(['start','whatsapp'],l)
 return out+'</div></section>'
def figure(src,caption,l,cls=''):
 w,h=DIMENSIONS[src]
 return f'<figure class="gallery-figure {cls}"><button class="image-open" type="button" data-image="/assets/{src}" data-caption="{e(caption)}" aria-label="{L("zoom",l)}: {e(caption)}"><img src="/assets/{src}" alt="{e(caption)}" width="{w}" height="{h}" loading="lazy"{image_options(src, "(max-width: 760px) 290px, 360px" if 'portrait' in cls else "(max-width: 760px) calc(100vw - 40px), (max-width: 1328px) calc(100vw - 128px), 1200px" if 'wide' in cls or 'case-cover' in cls else "(max-width: 760px) calc(100vw - 40px), (max-width: 1328px) calc((100vw - 160px) / 2), 584px")}></button><figcaption>{e(caption)}</figcaption></figure>'
def gallery(k,l):
 if k=='spiky':
  out='<div class="gallery-group"><h3>'+t({'en':'The public website','ar':'الموقع التعريفي'},l)+'</h3><p class="muted">'+L('arabicOnly',l)+'</p><div class="gallery-grid">'
  for src,caption,cls in [('spiky-public-mobile-hero-ar.png',{'en':'Mobile coach introduction','ar':'التعريف بالمدرّب على الهاتف'},'portrait'),('spiky-public-mobile-package-ar.png',{'en':'Mobile service package','ar':'باقة الخدمة على الهاتف'},'portrait'),('spiky-public-coach-ar.png',{'en':'Coach introduction','ar':'التعريف بالمدرّب'},'wide coach-crop'),('spiky-public-contact-ar.png',{'en':'Contact and footer','ar':'التواصل وتذييل الموقع'},'wide'),('spiky-public-faq-ar.png',{'en':'Frequently asked questions','ar':'الأسئلة الشائعة'},'wide')]: out+=figure(src,t(caption,l),l,cls)
  out+='</div></div><div class="gallery-group"><h3>'+t({'en':'The Coach Dashboard','ar':'لوحة تحكّم المدرّب'},l)+'</h3><p class="muted">'+t({'en':'A central workspace for managing coaching content, clients, and personalized plans. Names and dates are obscured in the supplied image.','ar':'مساحة مركزية لإدارة المحتوى والمتدرّبين والخطط المخصّصة. حُجبت الأسماء والتواريخ في الصورة الأصلية المقدّمة.'},l)+'</p>'+figure('spiky-dashboard-redacted-ar.png',t({'en':'Original Coach Dashboard · Identifying details obscured','ar':'لوحة تحكّم المدرّب الأصلية · حُجبت البيانات التعريفية'},l),l,'wide')+'</div>'
  out+='<div class="gallery-group"><h3>'+t({'en':'The Client App','ar':'تطبيق المتدرّب'},l)+'</h3><p class="muted">'+t({'en':"A mobile-friendly view of the client's training and nutrition plans.",'ar':'واجهة متوافقة مع الهواتف لمتابعة خطط التدريب والتغذية.'},l)+'</p><div class="gallery-grid client-gallery">'+figure('spiky-client-recipes-ar.png',t({'en':'Reusable recipe library','ar':'مكتبة الوصفات'},l),l,'portrait')+figure('spiky-client-exercise-ar.png',t({'en':'Exercise video and instructions','ar':'فيديو التمرين وتعليماته'},l),l,'portrait')+'</div></div>'
  return out
 out='<p class="muted">'+t({'en':'The Public Website — English & Arabic','ar':'الموقع التعريفي — العربية والإنجليزية'},l)+'</p><div class="gallery-grid future-gallery">'
 for i,caption in enumerate([{'en':'Homepage and services','ar':'الصفحة الرئيسية والخدمات'},{'en':'Selected work and process','ar':'الأعمال وخطوات العمل'},{'en':'Engineer introduction and FAQ','ar':'التعريف بالمهندس والأسئلة الشائعة'},{'en':'Contact and footer','ar':'التواصل وتذييل الموقع'}],1): out+=figure(f'future-public-{l}-{i:02d}.jpg',t(caption,l),l)
 return out+'</div>'
def case(k,l):
 c=CASES[k]; p=C['projects'][k]; out=''
 for i,s in enumerate(c['sections']):
  cl=['case-hero','case-text','case-text','case-features','case-gallery light','case-text','cta'][i]
  out+=f'<section class="section {cl}" data-section="{k}-{i+1:02d}"><div class="wrap"><p class="eyebrow">{i+1:02d} / {e(t(s["label"],l))}</p>'
  if i==0:
   out+=f'<h1>{hero_lines(t(c["title"],l))}</h1><div class="case-intro">{s["html"][l]}</div><div class="case-meta"><p>{e(t(p["sector"],l))}</p><p>{L("completed",l)}</p><p>{L("lead",l)}: {e(t(p["lead"],l))} · {L("cofounder",l)}</p></div><div class="actions">'+link(L('live',l),p['live'],'btn',True)+'</div>'+figure(p['cover'][l],p['name']+' · '+L('screen',l),l,'case-cover '+k)
   if k=='spiky':out+='<p class="muted">'+L('arabicOnly',l)+'</p>'
  elif i==4: out+='<h2>'+L('gallery',l)+'</h2>'+gallery(k,l)
  else:
   content=s['html'][l]; content=re.sub(r'<h3>(.*?)</h3>',r'<h2>\1</h2>',content,count=1)
   out+='<div class="case-prose">'+content+'</div>'
  if i==6:
   out+=actions(['start','whatsapp'],l); other='future-interiors' if k=='spiky' else 'spiky'
   thumb=C['projects'][other]['cover'][l].rsplit('.',1)[0]+'.webp'
   out+=link(L('related',l)+': '+C['projects'][other]['name'],path(other,l),'text-link section-link',attrs=f'data-thumb="/assets/thumbs/{thumb}"')
  out+='</div></section>'
 return out
def privacy(l):
 b=PRIV[l]
 # Pending infrastructure stays visible in the preview; publication is build-gated.
 note=t({'en':'Deployment preview: the form and scheduled retention must pass live verification before intake is enabled.','ar':'معاينة للإطلاق: يلزم اجتياز الاختبار الفعلي للنموذج والاحتفاظ المجدول قبل تفعيل استقبال الاستفسارات.'},l)
 if not PROD: b=b.replace('</h1>','</h1><p class="policy-status">'+note+'</p>',1)
 # Describe the actual implemented site, rather than inventing cookie services.
 b+='<h2>'+t({'en':'Current website settings','ar':'إعدادات الموقع الحالية'},l)+'</h2><p>'+t({'en':'This website does not load advertising trackers or optional analytics. Fonts and portfolio images are served locally. Form entries are not saved in browser storage. Cloudflare Turnstile checks form submissions to help prevent automated abuse. WhatsApp and email open only when you choose them.','ar':'لا يُحمّل هذا الموقع أدوات تتبّع إعلاني أو تحليلات اختيارية. تُقدَّم الخطوط وصور المشروعات من ملفات الموقع، ولا تُحفظ بيانات النموذج في تخزين المتصفح. تتحقّق خدمة Cloudflare Turnstile من طلبات النموذج للمساعدة في منع الإرسال الآلي المسيء. لا تُفتح خدمات واتساب والبريد الإلكتروني إلا عند اختيارك لها.'},l)+'</p>'
 return '<section class="section privacy-page"><div class="wrap prose">'+b+'</div></section>'
def header(k,l):
 nav=''.join(f'<a href="{path(x,l)}"'+(' aria-current="page"' if k==x or (k in CASES and x=='work') else '')+f'>{L(x,l)}</a>' for x in ['work','services','about','contact'])
 other='ar' if l=='en' else 'en'
 return f'<a class="skip" href="#main">{L("skip",l)}</a><header class="site-header"><div class="wrap nav-wrap"><a class="brand" href="{path("home",l)}" aria-label="ORVEN — {L("home",l)}"><img src="/assets/orven-logo-360.webp" alt="ORVEN" width="164" height="82"></a><nav id="primary-nav" aria-label="{t({"en":"Main navigation","ar":"التنقل الرئيسي"},l)}">{nav}</nav><div class="nav-actions"><a class="lang" href="{path(k,other)}" lang="{other}" hreflang="{other}" aria-label="{t({"en":"Switch to Arabic","ar":"التبديل إلى الإنجليزية"},l)}">{ "العربية" if l=="en" else "EN"}</a>'+link(L('start',l),path('contact',l),'btn nav-cta')+f'<button class="menu-toggle" aria-label="{L("menu",l)}" aria-controls="primary-nav" aria-expanded="false"><span></span><span></span></button></div></div></header>'
def footer(l):
 out='<footer><div class="wrap footer-main"><div><a href="'+path('home',l)+'"><img class="footer-logo" src="/assets/orven-logo-360.webp" alt="ORVEN" width="180" height="90" loading="lazy"></a><p class="muted">'+L('footer',l)+'</p></div><nav aria-label="'+t({'en':'Footer navigation','ar':'التنقل في تذييل الصفحة'},l)+'">'+''.join(f'<a href="{path(x,l)}">{L(x,l)}</a>' for x in ['work','services','about','contact'])+'</nav><div class="footer-contact">'+channel('email',l,'text-link')+channel('whatsapp',l,'text-link channel-link')
 if K['instagram']:out+=link('Instagram',K['instagram'],'text-link',True)
 out+='</div></div><div class="wrap founder-links">'
 for key,n in [('hadidy','Mohamed El-Hadidy' if l=='en' else 'محمد الحديدي'),('hamed','Mohamed Hamed' if l=='en' else 'محمد حامد'),('ziad','Ziad Mohamed' if l=='en' else 'زياد محمد')]:
  if K['linkedin'].get(key):out+=link(n+' · LinkedIn',K['linkedin'][key],'text-link',True)
 return out+f'</div><div class="wrap footer-bottom"><p>© 2026 ORVEN. {L("rights",l)}</p><a href="{path("privacy",l)}">{L("privacy",l)}</a></div></footer>'
def metadata(k,l,body):
 title=t(C['titles'][k],l)
 if k in C['pages']: desc=t(C['pages'][k][0]['body'],l)
 elif k in CASES:desc=re.sub('<[^>]+>','',CASES[k]['sections'][0]['html'][l])
 else:desc=t({'en':'How ORVEN handles project inquiries and personal information.','ar':'كيف تتعامل ORVEN مع استفسارات المشروعات والبيانات الشخصية.'},l)
 desc=desc[:200]; url=ORIGIN+path(k,l)
 image=ORIGIN+'/assets/'+(C['projects'][k]['cover'][l] if k in CASES else 'og-'+l+'.jpg')
 tags=f'<title>{e(title)}</title><meta name="description" content="{e(desc)}"><meta name="robots" content="{"index,follow" if PROD else "noindex,nofollow"}"><link rel="canonical" href="{url}">'
 for lang in ['en','ar']:tags+=f'<link rel="alternate" hreflang="{lang}" href="{ORIGIN+path(k,lang)}">'
 tags+=f'<link rel="alternate" hreflang="x-default" href="{ORIGIN+path(k,"en")}">'
 for name,val in [('og:type','website'),('og:site_name','ORVEN'),('og:title',title),('og:description',desc),('og:url',url),('og:image',image),('og:image:alt',title),('og:locale','ar_EG' if l=='ar' else 'en_US'),('og:locale:alternate','en_US' if l=='ar' else 'ar_EG')]:tags+=f'<meta property="{name}" content="{e(val)}">'
 tags+=f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(title)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{image}">'
 graph=[{'@type':'Organization','@id':ORIGIN+'/#organization','name':'ORVEN','url':ORIGIN,'email':K['email'],'logo':ORIGIN+'/assets/orven-original-transparent.png'},{'@type':'WebSite','@id':ORIGIN+'/#website','name':'ORVEN','url':ORIGIN,'inLanguage':['en','ar']},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':L('home',l),'item':ORIGIN+path('home',l)}]+([] if k=='home' else [{'@type':'ListItem','position':2,'name':title,'item':url}])}]
 return tags+'<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('<','\\u003c')+'</script>'
def build(k,l):
 body=''.join(render_section(s,l,i+1,k)+(marquee(l) if k=='home' and s['kind']=='hero' else '') for i,s in enumerate(C['pages'][k])) if k in C['pages'] else (case(k,l) if k in CASES else privacy(l))
 public={'formEndpoint':K['form_endpoint'],'turnstileSiteKey':K.get('turnstile_site_key',''),'policyVersion':'2026-10-19','formCopy':{key:t(v,l) for key,v in C['form'].items()},'close':L('close',l),'menu':L('menu',l)}
 out=f'<!doctype html><html lang="{l}" dir="{"rtl" if l=="ar" else "ltr"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#0B0B0C">'+metadata(k,l,body)+'<link rel="preload" href="/assets/fonts/'+('ORVENArabic-Medium.woff2' if l=='ar' else 'SpaceGrotesk.woff2')+'" as="font" type="font/woff2" crossorigin><link rel="icon" href="/assets/orven-favicon-64.png" type="image/png"><link rel="preload" href="/assets/fonts/'+('ORVENArabic-Regular.woff2' if l=='ar' else 'Inter.woff2')+'" as="font" type="font/woff2" crossorigin><style>'+INLINE_CSS+'</style><script src="/site.js" defer></script></head><body data-page="'+k+'">'+header(k,l)+'<main id="main">'+body+'</main>'+footer(l)+f'<div class="toast" role="status" aria-live="polite" hidden></div><dialog class="lightbox" aria-label="{L("zoom",l)}"><button class="close" type="button" aria-label="{L("close",l)}">×</button><img alt=""><div class="lb-bar"><button class="lb-prev" type="button" aria-label="{L("previous",l)}"><span aria-hidden="true">←</span></button><p></p><span class="lb-count" aria-hidden="true"></span><button class="lb-next" type="button" aria-label="{L("next",l)}"><span aria-hidden="true">→</span></button></div></dialog><script type="application/json" id="site-settings">'+json.dumps(public,ensure_ascii=False).replace('<','\\u003c')+'</script></body></html>'
 folder=D/path(k,l).lstrip('/');folder.mkdir(parents=True,exist_ok=True);(folder/'index.html').write_text(out,encoding='utf-8')
for l in ['en','ar']:
 for k in C['titles']:build(k,l)
(D/'index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="robots" content="noindex"><meta http-equiv="refresh" content="0;url=/en/"><title>ORVEN</title><a href="/en/">English</a> · <a href="/ar/" lang="ar">العربية</a></html>',encoding='utf-8')
(D/'404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Page not found — ORVEN</title><link rel="stylesheet" href="/tokens.css"><main class="wrap section"><p class="eyebrow">404</p><h1>Page not found.</h1><p lang="ar" dir="rtl">الصفحة غير موجودة.</p><a class="btn" href="/en/">Home</a> <a class="btn" href="/ar/" lang="ar">الرئيسية</a></main></html>',encoding='utf-8')
urls=[ORIGIN+path(k,l) for l in ['en','ar'] for k in C['titles']]
sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
for k in C['titles']:
 for l in ['en','ar']:
  sitemap+='<url><loc>'+ORIGIN+path(k,l)+'</loc>'+''.join(f'<xhtml:link rel="alternate" hreflang="{ll}" href="{ORIGIN+path(k,ll)}"/>' for ll in ['en','ar'])+f'<xhtml:link rel="alternate" hreflang="x-default" href="{ORIGIN+path(k,"en")}"/></url>'
(D/'sitemap.xml').write_text(sitemap+'</urlset>',encoding='utf-8')
(D/'robots.txt').write_text('User-agent: *\n'+('Allow: /\nSitemap: '+ORIGIN+'/sitemap.xml\n' if PROD else 'Disallow: /\n'),encoding='utf-8')
(D/'_headers').write_text("/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n  X-Frame-Options: SAMEORIGIN\n  Permissions-Policy: camera=(), microphone=(), geolocation=()\n  Content-Security-Policy: default-src 'self'; script-src 'self' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' https://challenges.cloudflare.com; frame-src https://challenges.cloudflare.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'\n  Strict-Transport-Security: max-age=31536000\n\n/assets/*\n  Cache-Control: public, max-age=86400\n",encoding='utf-8')
(R/'build-info.json').write_text(json.dumps({'mode':'production' if PROD else 'preview','origin':ORIGIN,'pages':16,'core_sections':26,'case_sections':14,'form_active':bool(K['form_endpoint']),'whatsapp_active':bool(K['whatsapp'])},indent=2),encoding='utf-8')
print('Built 16 bilingual pages, 26 core sections and 14 case-study sections. Mode:', 'production' if PROD else 'preview')
