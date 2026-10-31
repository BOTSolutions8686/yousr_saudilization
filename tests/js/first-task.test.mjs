import test from 'node:test';import assert from 'node:assert/strict';import vm from 'node:vm';import fs from 'node:fs';
const code=fs.readFileSync(new URL('../../yousr_saudilization/public/js/yousrerp-first-task.js',import.meta.url),'utf8');
test('guide survives route-container replacement and stays dismissed on the next load',()=>{
 const storage=new Map(),bodyChildren=[],routeChildren=[];
 const make=tag=>({tag,children:[],setAttribute(){},append(...children){this.children.push(...children)},remove(){const i=bodyChildren.indexOf(this);if(i>=0)bodyChildren.splice(i,1)}});
 const document={readyState:'complete',body:{append:node=>bodyChildren.push(node)},querySelector:s=>s==='#body'?{append:node=>routeChildren.push(node)}:null,createElement:make};
 const sandbox={document,localStorage:{getItem:k=>storage.get(k),setItem:(k,v)=>storage.set(k,v)},frappe:{boot:{setup_complete:true,lang:'en',yousr_setup:{show_first_task:true,portal_url:'https://stage.yousrerp.com'}},model:{can_create:()=>true},new_doc(){}}};
 vm.runInNewContext(code,sandbox);assert.equal(bodyChildren.length,1);assert.equal(routeChildren.length,0);
 routeChildren.splice(0);assert.equal(bodyChildren.length,1);
 const dismiss=bodyChildren[0].children.find(n=>n.className==='yousr-first-task-dismiss');dismiss.onclick();assert.equal(bodyChildren.length,0);
 vm.runInNewContext(code,sandbox);assert.equal(bodyChildren.length,0);
});
