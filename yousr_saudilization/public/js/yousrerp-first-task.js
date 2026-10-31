(() => {
  const setup = frappe.boot.yousr_setup || {};
  if (!frappe.boot.setup_complete || !setup.show_first_task) return;
  const key = 'yousr-first-task-v1';
  try { if (localStorage.getItem(key) === 'done') return; } catch (_) { return; }
  const t = (en, ar) => String(frappe.boot.lang || '').startsWith('ar') ? ar : en;
  const mount = () => {
    if (document.querySelector('.yousr-first-task')) return;
    const card = document.createElement('section');card.className='yousr-first-task';card.setAttribute('aria-label',t('Your first useful step','خطوتك الأولى'));
    const heading=document.createElement('h2');heading.textContent=t('Start with one useful task.','ابدأ بخطوة مفيدة.');card.append(heading);
    const copy=document.createElement('p');copy.textContent=t('No need to set up everything today. Choose a first step, or ask us for help.','لا تحتاج إلى إعداد كل شيء اليوم. اختر خطوتك الأولى أو اطلب المساعدة.');card.append(copy);
    const actions=document.createElement('div');actions.className='yousr-first-task-actions';
    const choices = {purchasing:[['Supplier','Add a supplier','إضافة مورد'],['Item','Add an item','إضافة صنف']],stock:[['Item','Add an item','إضافة صنف'],['Supplier','Add a supplier','إضافة مورد']],projects:[['Project','Start a project','بدء مشروع'],['Customer','Add a customer','إضافة عميل']],manufacturing:[['Item','Add an item','إضافة صنف'],['BOM','Start a bill of materials','بدء قائمة مواد']],hr:[['Employee','Add an employee','إضافة موظف'],['Department','Add a department','إضافة قسم']]};
    for(const [doctype,en,ar] of (choices[setup.first_task] || [['Customer','Add a customer','إضافة عميل'],['Item','Add an item','إضافة صنف']])) {
      if(frappe.model?.can_create && !frappe.model.can_create(doctype)) continue;
      const button=document.createElement('button');button.type='button';button.textContent=t(en,ar);button.onclick=()=>frappe.new_doc(doctype);actions.append(button);
    }
    const help=document.createElement('a');help.href=(['https://yousrerp.com','https://stage.yousrerp.com'].includes(setup.portal_url)?setup.portal_url:'https://yousrerp.com')+'/help-and-sessions';help.target='_blank';help.rel='noopener noreferrer';help.textContent=t('Ask for setup help','اطلب مساعدة في الإعداد');actions.append(help);card.append(actions);
    const close=document.createElement('button');close.type='button';close.className='yousr-first-task-dismiss';close.textContent=t('I’m ready to explore','سأستكشف مساحة العمل');close.onclick=()=>{try{localStorage.setItem(key,'done')}catch(_){}card.remove()};card.append(close);
    // Desk replaces its route container after navigation. Keep this dismissible
    // account guide outside that container so rendering cannot silently remove it.
    document.body.append(card);
  };
  if(document.readyState === "loading") document.addEventListener("DOMContentLoaded",mount,{once:true}); else mount();
})();
