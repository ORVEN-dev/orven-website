from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,sys,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parent.parent;D=R/'dist'; errors=[];checks=0
def check(ok,msg):
 global checks
 checks+=1
 if not ok:errors.append(msg)
class Document(HTMLParser):
 def __init__(self,text):super().__init__();self.tags=[];self.feed(text)
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
 def all(self,tag):return [a for t,a in self.tags if t==tag]
files=list(D.glob('en/**/index.html'))+list(D.glob('ar/**/index.html'))
check(len(files)==16,'Expected 16 localized pages')
expect={'home':10,'services':6,'work':3,'about':4,'contact':4,'spiky':7,'future-interiors':7}
for file in files:
 text=file.read_text(encoding='utf-8');doc=Document(text);lang=file.relative_to(D).parts[0]
 check(doc.all('html')[0].get('lang')==lang,f'{file}: lang')
 check(doc.all('html')[0].get('dir')==('rtl' if lang=='ar' else 'ltr'),f'{file}: direction')
 check(len(doc.all('h1'))==1,f'{file}: one h1')
 key=doc.all('body')[0]['data-page'];sections=[a for a in doc.all('section') if a.get('data-section')]
 if key in expect:check(len(sections)==expect[key],f'{file}: approved section count')
 for a in doc.all('a')+doc.all('link')+doc.all('script')+doc.all('img'):
  url=a.get('href',a.get('src',''))
  if not url:continue
  part=urlsplit(url)
  if not part.scheme and not part.netloc:
   local=D/unquote(part.path.lstrip('/')) if part.path.startswith('/') else file.parent/unquote(part.path)
   if not part.path:local=file
   if local.is_dir():local=local/'index.html'
   check(local.exists(),f'{file}: missing {url}')
   if part.fragment and local.suffix=='.html' and local.exists():check(f'id="{part.fragment}"' in local.read_text(encoding='utf-8'),f'{file}: missing anchor {url}')
 for image in doc.all('img'):
  if image.get('src'):check(bool(image.get('alt')),f'{file}: image without alternative text')
 alternates=[a for a in doc.all('link') if a.get('rel')=='alternate']
 check({a.get('hreflang') for a in alternates}=={'en','ar','x-default'},f'{file}: hreflang')
 check(len([a for a in doc.all('link') if a.get('rel')=='canonical'])==1,f'{file}: canonical')
 for script in re.findall(r'<script type="application/ld\+json">(.*?)</script>',text):
  try:json.loads(script)
  except Exception:errors.append(f'{file}: invalid structured data')
 check(not re.search(r'\b(ChatGPT|OpenAI|Puppeteer AI|AI-powered)\b',re.sub('<[^>]+>',' ',text)),f'{file}: public tool claim')
 if key=='contact':
  for field in ['name','contact','details']:check(f'id="{field}"' in text and f'for="{field}"' in text,f'{file}: labelled {field}')
  check('https://wa.me/201156682812' in text,f'{file}: primary WhatsApp')
  check('https://wa.me/201125301065' in text,f'{file}: manual call number')
 if key=='future-interiors':
  check(f'future-public-{lang}-01.jpg' in text,f'{file}: locale matched Future screenshot')
  check(not re.search(r'src="[^"\s]*(?:FI_0[2-6]|expenses|financial)[^"\s]*"',text),f'{file}: no financial image')
 if key=='spiky':check('spiky-public-cover-ar.png' in text and 'spiky-dashboard-redacted-ar.png' in text and 'spiky-client-exercise-ar.png' in text,f'{file}: genuine separate Spiky interfaces')
for path in D.rglob('*'):
 if path.is_file():check(not re.search(r'Dasboard|Complete system|SPK_02|SPK_03|review-source|\.gs$|site-config|\.secret',path.name,re.I),f'Unsafe public artifact {path}')
check(len(ET.parse(D/'sitemap.xml').getroot())==16,'Sitemap has 16 localized URLs')
for l in ['en','ar']:check((D/'assets'/f'og-{l}.jpg').is_file(),f'OG image {l}')
result={'checks':checks,'passed':checks-len(errors),'failed':len(errors),'errors':errors,'scope':'Local generated files; no live-provider claims'}
(R/'test-results').mkdir(exist_ok=True);(R/'test-results/static.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False));sys.exit(bool(errors))
