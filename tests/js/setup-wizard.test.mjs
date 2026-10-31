import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const code=fs.readFileSync(new URL('../../yousr_saudilization/public/js/yousrerp-setup.js',import.meta.url),'utf8');
test('supported setup hook changes presentation while preserving required fields and native handlers',()=>{
 const events={},native=()=>{},save=()=>{},slides=[{name:'welcome',onload:native,fields:[{fieldname:'country',reqd:1},{fieldname:'enable_telemetry',default:1}]},{name:'user',onload:native,fields:[{fieldname:'full_name',reqd:1},{fieldname:'email',reqd:1},{fieldname:'password',reqd:1}]},{name:'persona',onload:native,fields:[{fieldname:'persona_industry',reqd:1},{fieldname:'persona_company_size'}]},{name:'organization',onload:native,fields:[{fieldname:'company_name',reqd:1},{fieldname:'company_abbr',reqd:1},{fieldname:'fy_start_date',reqd:1}]}];
 const frappe={boot:{lang:'en',yousr_setup:{full_name:'QA',email:'',company_name:'Demo'}},setup:{slides,on:(e,fn)=>events[e]=fn},wizard:{save}};
 vm.runInNewContext(code,{frappe,document:{}});events.before_load();assert.equal(slides.length,4);assert.ok(slides.every(s=>s.onload===native));assert.equal(frappe.wizard.save,save);
 assert.ok(slides.flatMap(s=>s.fields).filter(f=>['country','email','password','company_name','company_abbr','fy_start_date'].includes(f.fieldname)).every(f=>f.reqd===1));
 assert.equal(slides[1].fields[0].default,'QA');assert.equal(slides[1].fields[1].default,undefined);assert.equal(slides[0].fields[1].default,0);assert.equal(slides[0].fields[1].hidden,1);assert.equal(slides[2].fields[0].reqd,1);assert.equal(slides[2].fields[1].hidden,1);assert.match(frappe.setup.intro_apps[0].logo,/yousr_saudilization/);
});

test('verified email and each workspace company remain editable suggestions',()=>{
 for (const company of ['Company A','Company B']) {
  const events={},slides=[{name:'user',fields:[{fieldname:'email',reqd:1}]},{name:'organization',fields:[{fieldname:'company_name',reqd:1}]}];
  const frappe={boot:{lang:'en',yousr_setup:{email:'personal@example.invalid',company_name:company}},setup:{slides,on:(e,fn)=>events[e]=fn}};
  vm.runInNewContext(code,{frappe,document:{}});events.before_load();
  assert.equal(slides[0].fields[0].default,'personal@example.invalid');assert.equal(slides[0].fields[0].read_only,undefined);
  assert.equal(slides[1].fields[0].default,company);assert.equal(slides[1].fields[0].read_only,undefined);
 }
});
