import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
const code=fs.readFileSync(new URL('../../yousr_saudilization/public/js/yousrerp-brand.js',import.meta.url),'utf8');
test('native checklist branding preserves its counter, Arabic text and child controls',()=>{
 const english={nodeType:3,textContent:'Get to know ERPNext · 0 of 9 steps done'},arabic={nodeType:3,textContent:'تعرف على ERPNext · ٠ من ٩'},control={nodeType:1,textContent:'ERPNext control'},unrelated={nodeType:3,textContent:'ERPNext invoice note'};
 const document={readyState:'complete',body:{},documentElement:{classList:{add(){}}},querySelectorAll(selector){return selector==='.onboarding-widget-box .widget-subtitle'?[{childNodes:[english,control]},{childNodes:[arabic]}]:[]}};
 vm.runInNewContext(code,{document,MutationObserver:class{observe(){}},requestAnimationFrame:fn=>fn()});
 assert.equal(english.textContent,'Get to know YousrERP · 0 of 9 steps done');assert.equal(arabic.textContent,'تعرف على YousrERP · ٠ من ٩');assert.equal(control.textContent,'ERPNext control');assert.equal(unrelated.textContent,'ERPNext invoice note');
});
