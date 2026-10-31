import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const code=fs.readFileSync(new URL('../../yousr_saudilization/public/js/yousrerp-menus.js',import.meta.url),'utf8');
function load({portal='https://stage.yousrerp.com',ar=false}={}) {
 class Dropdown{open(){this.seen=this.options;return 'native-open'}}
 const messages=[],document={readyState:'complete',querySelectorAll:()=>[]};
 const frappe={boot:{lang:ar?'ar':'en',versions:{yousr_saudilization:'0.2.7'},yousr_setup:{portal_url:portal},cloud_settings:{enabled:true}},ui:{Dropdown},msgprint:value=>messages.push(value)};
 const translations={'About':'حول','Frappe Support':'دعم فرابي','Manage Billing':'إدارة الفوترة','Logout':'الخروج'};
 vm.runInNewContext(code,{frappe,document,__:(label)=>ar?(translations[label]||label):label});
 const menu=(options,avatar=true)=>Object.assign(new Dropdown(),{options,trigger_el:{matches:()=>avatar}});
 return{frappe,messages,menu};
}
test('only avatar menu destinations change, preserving native profile/theme/logout callbacks',()=>{
 const {frappe,messages,menu}=load();const profile=()=>{},theme=()=>{},logout=()=>{},provider=()=>{throw Error('provider callback must not run')};
 const items=[{label:'Edit Profile',onclick:profile},{label:'Toggle Theme',onclick:theme},{label:'About',onclick:provider},{label:'Frappe Support',onclick:provider},{label:'Manage Billing',onclick:provider},{label:'Logout',onclick:logout}];
 const avatar=menu(items);assert.equal(avatar.open(),'native-open');assert.equal(avatar.options,items);const rows=avatar.seen;
 assert.equal(rows[0].onclick,profile);assert.equal(rows[1].onclick,theme);assert.equal(rows.at(-1).onclick,logout);
 assert.equal(rows[3].href,'https://stage.yousrerp.com/help-and-sessions');assert.equal(rows[3].onclick,undefined);assert.equal(rows[4].href,'https://stage.yousrerp.com/billings/subscriptions');assert.equal(rows[4].target,'_blank');rows[2].onclick();assert.equal(messages[0].title,'About YousrERP');
 const unrelated=menu(items,false);unrelated.open();assert.equal(unrelated.seen,items);assert.equal(frappe.boot.cloud_settings.enabled,false);
});
test('grouped native Desk menu gains one branded group before logout and remains idempotent',()=>{
 const {menu}=load();const settings=()=>{},logout=()=>{};const items=[{group:'',options:[{name:'settings',label:'Settings',onclick:settings}]},{group:'',options:[{name:'logout',label:'Logout',onclick:logout}]}];
 const avatar=menu(items);avatar.open();assert.equal(avatar.seen.length,3);assert.equal(avatar.seen[0].options[0].onclick,settings);assert.equal(avatar.seen[1].options.length,3);assert.equal(avatar.seen[2].options[0].onclick,logout);
 avatar.options=avatar.seen;avatar.open();assert.equal(avatar.seen.length,3);
});
test('translated menus use Arabic labels and refuse an untrusted portal destination',()=>{
 const {menu}=load({portal:'https://attacker.invalid',ar:true});const avatar=menu([{label:'حول'},{label:'دعم فرابي'},{label:'إدارة الفوترة'},{label:'الخروج'}]);avatar.open();
 assert.equal(avatar.seen[0].label,'عن YousrERP');assert.equal(avatar.seen[1].href,'https://yousrerp.com/help-and-sessions');assert.equal(avatar.seen[2].label,'الاشتراك والفوترة');assert.equal(avatar.seen.at(-1).label,'الخروج');
});
