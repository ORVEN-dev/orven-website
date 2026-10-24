'use strict';
const settings=JSON.parse(document.getElementById('site-settings').textContent);
// Local integration hook only: no analytics provider, network request, storage or visitor data.
function conversion(event,action,section){
 document.dispatchEvent(new CustomEvent('orven:conversion',{detail:{event,action,section,page:document.body.dataset.page,language:document.documentElement.lang,version:settings.conversionVersion}}));
}
document.addEventListener('click',e=>{
 const a=e.target.closest?.('[data-conversion]');if(!a)return;
 conversion('cta_click',a.dataset.conversion,a.closest('[data-section]')?.dataset.section||(a.closest('header')?'header':'footer'));
 if(a.dataset.conversion==='guarantee_terms'&&deliveryTerms)deliveryTerms.open=true;
});
const deliveryTerms=document.getElementById('delivery-guarantee');
if(deliveryTerms){
 const showTerms=()=>{if(location.hash==='#delivery-guarantee'){deliveryTerms.open=true;deliveryTerms.scrollIntoView({block:'start'});}};
 deliveryTerms.open=location.hash==='#delivery-guarantee';
 showTerms();window.addEventListener('hashchange',showTerms);
}
const header=document.querySelector('.site-header');
const menu=document.querySelector('.menu-toggle');
let previousScroll=window.scrollY;
function closeMenu(){header.classList.remove('menu-open');menu.setAttribute('aria-expanded','false');menu.setAttribute('aria-label',settings.menu)}
menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));menu.setAttribute('aria-label',open?settings.close:settings.menu);header.classList.toggle('menu-open',open)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&header.classList.contains('menu-open')){closeMenu();menu.focus()}});
document.querySelectorAll('#primary-nav a').forEach(a=>a.addEventListener('click',closeMenu));
window.addEventListener('resize',()=>{if(window.innerWidth>760)closeMenu()});
window.addEventListener('scroll',()=>{const y=window.scrollY;if(Math.abs(y-previousScroll)>5){header.classList.toggle('is-hidden',y>140&&y>previousScroll&&!header.classList.contains('menu-open'));previousScroll=y}},{passive:true});
const toast=document.querySelector('.toast');let toastTimer;
document.querySelectorAll('[data-unavailable]').forEach(b=>b.addEventListener('click',()=>{toast.textContent=b.dataset.unavailable;toast.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>{toast.hidden=true},8500)}));
const dialog=document.querySelector('.lightbox'),shots=[...document.querySelectorAll('[data-image]')],lbImg=dialog.querySelector('img'),lbCap=dialog.querySelector('p'),lbCount=dialog.querySelector('.lb-count');let lastImageButton,current=0;
function showImage(i){current=(i+shots.length)%shots.length;const b=shots[current];lastImageButton=b;lbImg.src=b.dataset.image;lbImg.alt=b.dataset.caption;lbCap.textContent=b.dataset.caption;if(lbCount)lbCount.textContent=shots.length>1?current+1+' / '+shots.length:'';lbImg.classList.remove('lb-swap');void lbImg.offsetWidth;lbImg.classList.add('lb-swap')}
const step=fwd=>showImage(current+(fwd?1:-1)),rtl=document.documentElement.dir==='rtl';
shots.forEach((b,i)=>b.addEventListener('click',()=>{showImage(i);dialog.classList.toggle('single',shots.length<2);dialog.showModal()}));
dialog.querySelector('.lb-prev')?.addEventListener('click',()=>step(false));dialog.querySelector('.lb-next')?.addEventListener('click',()=>step(true));
dialog.addEventListener('keydown',e=>{if((e.key==='ArrowLeft'||e.key==='ArrowRight')&&shots.length>1){e.preventDefault();step((e.key==='ArrowRight')!==rtl)}});
// Touch: swipe sideways to change image, swipe down (at the top) to close.
let touchX,touchY;dialog.addEventListener('touchstart',e=>{touchX=e.touches[0].clientX;touchY=e.touches[0].clientY},{passive:true});
dialog.addEventListener('touchend',e=>{if(touchX===undefined)return;const t=e.changedTouches[0],dx=t.clientX-touchX,dy=t.clientY-touchY;touchX=undefined;if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.3&&shots.length>1)step((dx<0)!==rtl);else if(dy>90&&dy>Math.abs(dx)*1.3&&dialog.scrollTop<=0)dialog.close()},{passive:true});
dialog.querySelector('.close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close()});
dialog.addEventListener('close',()=>lastImageButton?.focus());
const form=document.getElementById('inquiry');
if(form){
 const copy=settings.formCopy,status=document.getElementById('form-status'),submit=form.querySelector('[type=submit]');
 let requestId=crypto.randomUUID(),startedAt=Date.now(),turnstileToken='',widgetId,loadingVerification;
 function loadVerification(){
  if(loadingVerification||!settings.turnstileSiteKey)return;
  loadingVerification=true;
  const script=document.createElement('script');script.src='https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';script.async=true;
  script.onload=()=>{widgetId=window.turnstile.render('#turnstile',{sitekey:settings.turnstileSiteKey,action:'inquiry',language:document.documentElement.lang,theme:'light',appearance:'interaction-only',callback:token=>{turnstileToken=token;},'expired-callback':()=>{turnstileToken='';},'error-callback':()=>{turnstileToken='';status.textContent=copy.verification;}})};
  script.onerror=()=>{status.textContent=copy.verification;loadingVerification=false;};document.head.append(script);
 }
 if(settings.formEndpoint)form.addEventListener('focusin',loadVerification,{once:true});
 const ids=['name','contact','details'];
 function error(id,msg){const input=document.getElementById(id);input.setAttribute('aria-invalid',String(Boolean(msg)));document.getElementById(id+'-error').textContent=msg}
 function normalizeDigits(s){return s.replace(/[٠-٩]/g,d=>String(d.charCodeAt(0)-1632)).replace(/[۰-۹]/g,d=>String(d.charCodeAt(0)-1776))}
 function validContact(s){s=normalizeDigits(s.trim());if(/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s))return true;return /^[+\d\s()-]+$/.test(s)&&/^\+?\d{8,15}$/.test(s.replace(/[\s()-]/g,''))}
 ids.forEach(id=>document.getElementById(id).addEventListener('input',()=>error(id,'')));
 form.addEventListener('submit',async e=>{
  e.preventDefault();status.textContent='';status.classList.remove('ok');let firstInvalid;
  ids.forEach(id=>{const v=document.getElementById(id).value.trim();const msg=!v?copy.required:id==='contact'&&!validContact(v)?copy.invalid:'';error(id,msg);if(msg&&!firstInvalid)firstInvalid=id});
  if(firstInvalid){document.getElementById(firstInvalid).focus();return}
  if(!settings.formEndpoint){status.textContent=copy.unconfigured;status.focus();return}
  if(!turnstileToken){loadVerification();status.textContent=copy.verification;status.focus();return}
  submit.disabled=true;submit.textContent=copy.sending;
  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),30000);
  try{
   const values=Object.fromEntries(new FormData(form));const data={name:values.name,contact:normalizeDigits(values.contact),details:values.details,service:values.service,company_url:values.company_url,locale:document.documentElement.lang,requestId,startedAt,turnstileToken,policyVersion:settings.policyVersion};
   const response=await fetch(settings.formEndpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data),signal:controller.signal,credentials:'omit',referrerPolicy:'no-referrer'});
   const result=await response.json();
   if(!response.ok||result.received!==true||result.requestId!==requestId)throw new Error('Unconfirmed delivery');
   conversion('inquiry_success','inquiry_form',form.closest('[data-section]').dataset.section);
   status.textContent=copy.success;status.classList.add('ok');form.reset();requestId=crypto.randomUUID();startedAt=Date.now();
  }catch{status.textContent=copy.error}
  finally{clearTimeout(timeout);submit.disabled=false;submit.textContent=copy.submit;turnstileToken='';if(widgetId!==undefined)window.turnstile.reset(widgetId);status.focus()}
 });
}
/* Motion — progressive enhancement. Nothing is hidden unless this runs; only content below the
   fold is hidden; everything is skipped under prefers-reduced-motion. The hero is pure CSS. */
(()=>{
 const root=document.documentElement,fine=matchMedia('(hover:hover) and (pointer:fine)').matches;
 if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;
 const $$=s=>[...document.querySelectorAll(s)];let lenis;
 // Smooth scrolling: self-hosted Lenis, desktop/fine pointers only. Lenis honours html scroll-padding-top (the fixed header height), so anchors land below the header.
 if(fine){const s=document.createElement('script');s.src='/assets/vendor/lenis.min.js';s.onload=()=>{try{lenis=new window.Lenis({autoRaf:true,lerp:.1,prevent:n=>!!n.closest?.('dialog,textarea,select,[data-lenis-prevent]')})}catch{}};document.head.append(s)}
 document.addEventListener('click',e=>{
  const a=e.target.closest?.('a[href*="#"]');if(!lenis||!a||a.classList.contains('skip'))return;
  const u=new URL(a.href,location.href),t=u.hash&&document.getElementById(decodeURIComponent(u.hash.slice(1)));
  if(!t||u.pathname!==location.pathname)return;
  e.preventDefault();lenis.scrollTo(t);history.pushState(null,'',u.hash);
 });
 $$('[data-image]').forEach(b=>b.addEventListener('click',()=>lenis?.stop()));dialog.addEventListener('close',()=>lenis?.start());
 // Project images: subtle parallax inside the frame.
 const seen=new Set(),pio=new IntersectionObserver(es=>es.forEach(x=>x.isIntersecting?seen.add(x.target):seen.delete(x.target)));
 $$('.project-image').forEach(a=>{a.classList.add('px');pio.observe(a)});let tick=0;
 const para=()=>{tick=0;seen.forEach(a=>{const r=a.getBoundingClientRect(),h=innerHeight,p=Math.max(-1,Math.min(1,(r.top+r.height/2-h/2)/(h/2+r.height/2)));a.firstElementChild.style.translate='0 '+(p*r.height*-.035).toFixed(1)+'px'})};
 // Process steps: a bronze line follows scroll progress. Case studies: reading progress bar.
 const steps=$$('.process-grid');let bar;
 if(document.querySelector('.case-hero')){bar=document.createElement('div');bar.className='read-progress';bar.setAttribute('aria-hidden','true');document.body.append(bar)}
 const frame=()=>{para();const h=innerHeight;
  steps.forEach(g=>{const r=g.getBoundingClientRect();g.style.setProperty('--p',Math.max(0,Math.min(1,(h*.85-r.top)/Math.max(r.height,h*.45))).toFixed(3))});
  if(bar)bar.style.transform=`scaleX(${Math.min(1,scrollY/Math.max(1,document.documentElement.scrollHeight-h)).toFixed(4)})`};
 addEventListener('scroll',()=>{if(!tick)tick=requestAnimationFrame(frame)},{passive:true});
 // Hero: soft bronze light follows the pointer (fine pointers only; CSS eases the movement).
 const hero=document.querySelector('.hero');
 if(fine&&hero)hero.addEventListener('pointermove',e=>{const r=hero.getBoundingClientRect();hero.style.setProperty('--gx',((e.clientX-r.left)/r.width*100).toFixed(1)+'%');hero.style.setProperty('--gy',((e.clientY-r.top)/r.height*100).toFixed(1)+'%')},{passive:true});
 // Cursor label over project images and floating thumbnail on the related-project link.
 if(fine){
  const make=(c,h)=>{const d=document.createElement('div');d.className='follower '+c;d.setAttribute('aria-hidden','true');d.innerHTML=h;document.body.append(d);return d};
  const label=make('cursor-label',''),thumb=make('float-thumb','<img alt="">');let cur,x=0,y=0,tx=0,ty=0,raf=0;
  const place=()=>{const w=cur.offsetWidth,h=cur.offsetHeight,px=tx+w+20>innerWidth?tx-w-16:tx+16,py=ty+h+20>innerHeight?ty-h-16:ty+16;return[px,py]};
  const loop=()=>{const[px,py]=place();x+=(px-x)*.22;y+=(py-y)*.22;cur.style.transform=`translate(${x}px,${y}px)`;raf=Math.abs(px-x)+Math.abs(py-y)>.4?requestAnimationFrame(loop):0};
  addEventListener('pointermove',e=>{tx=e.clientX;ty=e.clientY;if(cur&&!raf)raf=requestAnimationFrame(loop)},{passive:true});
  const bind=(sel,el,set)=>$$(sel).forEach(a=>{a.addEventListener('pointerenter',e=>{set(a);cur=el;tx=e.clientX;ty=e.clientY;[x,y]=place();el.style.transform=`translate(${x}px,${y}px)`;el.classList.add('on')});a.addEventListener('pointerleave',()=>el.classList.remove('on'))});
  bind('[data-cursor]',label,a=>{label.textContent=a.dataset.cursor});
  bind('[data-thumb]',thumb,a=>{const i=thumb.firstChild;if(i.getAttribute('src')!==a.dataset.thumb)i.src=a.dataset.thumb});
 }
 // Lazy images that are still loading fade in instead of popping.
 $$('img[loading=lazy]').forEach(i=>{if(i.complete)return;i.classList.add('img-fade');const on=()=>i.classList.add('loaded');i.addEventListener('load',on,{once:true});i.addEventListener('error',on,{once:true})});
 // Founder cards: a soft light follows the pointer inside the card.
 if(fine)$$('.member').forEach(c=>c.addEventListener('pointermove',e=>{const r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left).toFixed(0)+'px');c.style.setProperty('--my',(e.clientY-r.top).toFixed(0)+'px')},{passive:true}));
 // Scroll reveals. Line-split headings are restored to their original markup once revealed.
 const original=new Map();
 const split=h=>{
  if([...h.children].some(c=>c.tagName!=='BR'))return false;
  const html=original.get(h)||h.innerHTML;original.set(h,html);
  h.innerHTML=html.split(/<br\s*\/?>/i).map(p=>p.trim().split(/\s+/).map(w=>'<span>'+w+'</span>').join(' ')).join('<br>');
  const lines=[];let top;
  for(const w of h.querySelectorAll('span')){if(top===undefined||Math.abs(w.offsetTop-top)>4){lines.push([]);top=w.offsetTop}lines.at(-1).push(w.innerHTML)}
  h.innerHTML=lines.map((l,i)=>`<span class="ln"><span style="--i:${i}">${l.join(' ')}</span></span>`).join(' ');return true;
 };
 const done=el=>{el.classList.remove('rv','rv-line','rv-split','in');el.style.removeProperty('--d');if(original.has(el)){el.innerHTML=original.get(el);original.delete(el)}};
 const io=new IntersectionObserver(es=>{let n=0;for(const x of es){if(!x.isIntersecting)continue;const el=x.target,d=Math.min(n++,6)*80;io.unobserve(el);if(el.classList.contains('rv-split')&&!split(el))el.classList.remove('rv-split');el.style.setProperty('--d',d+'ms');el.classList.add('in');setTimeout(()=>done(el),d+1700)}},{rootMargin:'0px 0px -8% 0px'});
 const init=()=>{try{
  root.classList.add('js-motion');
  // Read positions before writing classes. Split only a heading entering the viewport,
  // not every offscreen heading during initial load (which forced repeated page layouts).
  const pending=[],below=el=>el.getBoundingClientRect().top>innerHeight*.92,mark=(sel,...cls)=>$$(sel).forEach(el=>{if(below(el))pending.push([el,cls])});
  mark('.section-head h2,.case-prose>h2,.case-gallery h2','rv-split');
  mark('.cards-grid article,.process-grid article,.team-grid article,.capabilities li,.faq details,.reviews-grid article','rv-line');
  mark('.project-image');
  mark('.section:not(.hero) .section-head .eyebrow,.section:not(.hero) .section-head .intro,.grid article,.project>:not(.project-image),.work-bottom,.review-note,.section-link,.detail>.wrap>.text-link,.cta .actions,.case-prose>:not(h2),.case-text>.wrap>.eyebrow,.case-features>.wrap>.eyebrow,.case-gallery>.wrap>.eyebrow,.gallery-group>h3,.gallery-group>p,.gallery-figure,.case-gallery>.wrap>p');
  pending.forEach(([el,cls])=>{el.classList.add('rv',...cls);io.observe(el)});
  let rt;addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(()=>original.forEach((_,h)=>{if(!h.classList.contains('in'))split(h)}),200)});
  addEventListener('beforeprint',()=>$$('.rv').forEach(done));frame();
 }catch{root.classList.remove('js-motion')}};
 Promise.race([document.fonts?.ready,new Promise(r=>setTimeout(r,1200))]).then(init,init);
})();
