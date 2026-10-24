// Uses a local preview. All inquiry responses and Turnstile are mocked; no inquiry reaches a provider.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const path=require('node:path');
(async()=>{
 const origin=process.env.TEST_ORIGIN||'http://127.0.0.1:8774';
 const out=path.resolve(__dirname,'../test-results/funnel');await fs.mkdir(out,{recursive:true});
 const browser=await chromium.launch({channel:'chrome',headless:true,args:['--no-proxy-server']});
 const results=[],errors=[];
 const offer={en:'Your Website. As Agreed. On Time. Or Your Money Back.',ar:'موقعك. بالمواصفات المتفق عليها. في الموعد. أو تستردّ أموالك.'};
 try{
  for(const width of [320,390,768,908,1024,1440]){
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
   const page=await context.newPage();page.on('pageerror',e=>errors.push(String(e)));
   for(const lang of ['en','ar'])for(const route of ['','services/','contact/']){
    await page.goto(`${origin}/${lang}/${route}`);await page.evaluate(()=>document.fonts.ready);
    const metrics=await page.evaluate(()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
     notes:[...document.querySelectorAll('.delivery-note')].map(n=>({width:n.clientWidth,scrollWidth:n.scrollWidth,actionBefore:!!n.previousElementSibling?.querySelector?.('a,button')||n.previousElementSibling?.matches('a,button')})),
     clipped:[...document.querySelectorAll('.delivery-note p,.delivery-terms p,.hero h1')].filter(n=>n.scrollWidth>n.clientWidth+1).length}));
    assert.ok(metrics.scrollWidth<=width);assert.equal(metrics.clipped,0);
    assert.ok(metrics.notes.length);assert.ok(metrics.notes.every(n=>n.scrollWidth<=n.width&&n.actionBefore));
    for(const note of await page.locator('.delivery-note').all()){
     assert.equal(await note.locator('.delivery-offer').textContent(),offer[lang]);
     assert.equal(await note.locator('.delivery-offer').evaluate(n=>n.previousElementSibling.className),'delivery-name');
     if(lang==='en')assert.equal(await note.locator('.delivery-name').textContent(),'ORVEN 100% Delivery Guarantee');
     assert.ok(await note.evaluate(n=>getComputedStyle(n).position==='static'));
    }
    assert.equal(metrics.notes.length,route===''?3:route==='services/'?4:1);
    if(route==='services/'){
     assert.equal(await page.locator('#delivery-guarantee').evaluate(e=>e.open),false);
     await page.locator('.hero .delivery-note a').click();
     assert.equal(await page.locator('#delivery-guarantee').evaluate(e=>e.open),true);
     assert.ok(await page.locator('#delivery-guarantee').isVisible());
     assert.equal(await page.locator('#delivery-guarantee .delivery-offer').textContent(),offer[lang]);
     await page.locator('#delivery-guarantee summary').focus();await page.keyboard.press('Enter');
     assert.equal(await page.locator('#delivery-guarantee').evaluate(e=>e.open),false);
     // A repeated link to the same fragment must reopen manually collapsed terms.
     await page.locator('.hero .delivery-note a').click();
     assert.equal(await page.locator('#delivery-guarantee').evaluate(e=>e.open),true);
    }
    if([390,1440].includes(width)&&route===''){
     await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:path.join(out,`home-${lang}-${width}.jpg`),type:'jpeg',quality:88,fullPage:false});
    }
    results.push({lang,route,width,...metrics});
   }
   await context.close();
  }
  for(const lang of ['en','ar']){
   const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:900}});
   const page=await context.newPage();await page.goto(`${origin}/${lang}/services/#delivery-guarantee`);
   assert.ok(await page.locator('#delivery-guarantee > div').isVisible());await context.close();
  }
  const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  page.on('pageerror',e=>errors.push(String(e)));
  await page.addInitScript(()=>{window.funnelEvents=[];document.addEventListener('orven:conversion',e=>window.funnelEvents.push(e.detail));});
  await page.route('https://challenges.cloudflare.com/**',r=>r.fulfill({contentType:'application/javascript',body:'window.turnstile={render:(s,o)=>{o.callback("local-test-token");return 1},reset:()=>{}};'}));
  let mode='ok',mockRequests=0;
  await page.route('**/api/inquiry',async r=>{mockRequests++;const data=r.request().postDataJSON();await r.fulfill({json:{received:mode!=='failed',requestId:mode==='mismatch'?'wrong':data.requestId}});});
  for(mode of ['failed','mismatch','ok']){
   await page.goto(`${origin}/en/contact/?utm_campaign=private-test-marker`);
   await page.locator('#name').fill('Local Test Only');await page.locator('#contact').fill('local@example.invalid');await page.locator('#details').fill('A local mocked inquiry only.');
   await page.locator('#inquiry [type=submit]').click();
   await page.waitForFunction(()=>document.querySelector('#form-status').textContent.length>0);
   const events=await page.evaluate(()=>window.funnelEvents);
   assert.equal(events.filter(x=>x.event==='inquiry_success').length,mode==='ok'?1:0);
   for(const event of events){
    assert.deepEqual(Object.keys(event).sort(),['action','event','language','page','section','version']);
    assert.ok(!JSON.stringify(event).includes('private-test-marker'));assert.ok(!JSON.stringify(event).includes('local@example.invalid'));
   }
  }
  await page.goto(`${origin}/ar/`);await page.locator('.hero .delivery-note a').click();
  assert.equal(await page.locator('#delivery-guarantee').evaluate(e=>e.open),true);
  await page.locator('.hero .delivery-note a').click();
  assert.deepEqual(await page.evaluate(()=>window.funnelEvents.at(-1)),{event:'cta_click',action:'guarantee_terms',section:'services-01',page:'services',language:'ar',version:'trust-v1'});
  await page.goto(`${origin}/en/`);await page.locator('.hero [data-conversion="start_project"]').click();
  assert.ok(page.url().endsWith('/en/contact/'));
  assert.deepEqual(errors,[]);assert.equal(mockRequests,3);
  await fs.writeFile(path.join(out,'browser.json'),JSON.stringify({results,errors,mockedInquiryResponses:mockRequests,interactions:'Localized terms links, same-fragment reopening, keyboard disclosure, no-JS terms, localized project CTA, conversion payload privacy and success-only confirmation passed',scope:'Local browser; no production inquiry or third-party analytics'},null,2));
  console.log(JSON.stringify({responsiveViews:results.length,errors,mockedInquiryResponses:mockRequests,interactions:'passed'}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
