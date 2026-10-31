/* Scoped presentation adapter. Native menu navigation, focus and permissions remain native. */
(() => {
  const context = frappe.boot.yousr_setup || {};
  const portal = ['https://yousrerp.com', 'https://stage.yousrerp.com'].includes(context.portal_url) ? context.portal_url : 'https://yousrerp.com';
  const ar = String(frappe.boot.lang || '').startsWith('ar');
  const t = (en, arabic) => ar ? arabic : en;
  const nativeLabel = (value, label) => value === label || (typeof __ === 'function' && value === __(label));
  const about = () => {
    const version = String(frappe.boot.versions?.yousr_saudilization || '').replace(/[^a-zA-Z0-9._+-]/g, '');
    frappe.msgprint({title:t('About YousrERP','عن YousrERP'),message:`<img class="yousr-about-logo" src="/assets/yousr_saudilization/images/yousrerp-compact-light.svg" alt="YousrERP"><p>${t('Your business, connected.','أعمالك، مترابطة.')}</p><p>${t('A product of BOT Solutions.','أحد منتجات BOT Solutions.')}</p><small>${t('Workspace experience','تجربة مساحة العمل')} ${version}</small>`});
  };
  const ownRows = () => [
    {name:'yousr-about',label:t('About YousrERP','عن YousrERP'),icon:'info',onclick:about},
    {name:'yousr-support',label:t('YousrERP support','دعم YousrERP'),icon:'life-buoy',href:portal+'/help-and-sessions',target:'_blank'},
    {name:'yousr-billing',label:t('Subscription & billing','الاشتراك والفوترة'),icon:'credit-card',href:portal+'/billings/subscriptions',target:'_blank'},
  ];
  const transform = (items) => {
    if (!Array.isArray(items)) return items;
    const found = new Set();
    const visit = (rows) => rows.map(item => {
      if (!item || typeof item !== 'object') return item;
      if (Array.isArray(item.options)) return {...item,options:visit(item.options)};
      let index = nativeLabel(item.label,'About') ? 0 : nativeLabel(item.label,'Frappe Support') ? 1 : nativeLabel(item.label,'Manage Billing') ? 2 : -1;
      if (index < 0) index = ownRows().findIndex(row=>row.name===item.name);
      if (index < 0) return item;
      const row=ownRows()[index];found.add(row.name);
      return {...item,onclick:undefined,onClick:undefined,href:undefined,url:undefined,target:undefined,...row};
    });
    const result=visit(items),missing=ownRows().filter(row=>!found.has(row.name));
    const hasLogout = item => nativeLabel(item?.label,'Logout') || (Array.isArray(item?.options) && item.options.some(hasLogout));
    let index=result.findIndex(hasLogout);if(index<0)index=result.length;
    if(missing.length) result.splice(index,0,...(result.some(item=>Array.isArray(item?.options))?[{group:'YousrERP',options:missing}]:missing));
    return result;
  };
  const install = () => {
    const prototype=frappe.ui?.Dropdown?.prototype;
    if(!prototype?.open || prototype.__yousrManagedMenu) return;
    const open=prototype.open;
    prototype.open=function(...args) {
      if(!this.trigger_el?.matches?.('.desktop-avatar, .dock-user, .dropdown-navbar-user')) return open.apply(this,args);
      const original=this.options;
      this.options=typeof original==='function'?function(...values){const result=original.apply(this,values);return result?.then?result.then(transform):transform(result)}:transform(original);
      try{return open.apply(this,args)}finally{this.options=original}
    };
    prototype.__yousrManagedMenu=true;
  };
  // Infrastructure settings are operated by the YousrERP team. Do not change
  // is_fc_site, native roles, site limits or the operator's Cloud credentials.
  if(frappe.boot.cloud_settings) frappe.boot.cloud_settings={...frappe.boot.cloud_settings,enabled:false};
  install();
  if(!frappe.ui?.Dropdown?.prototype?.__yousrManagedMenu && frappe.after_ajax) frappe.after_ajax(install);
  const retireGuide=()=>document.querySelectorAll('.yousr-first-task').forEach(card=>card.remove());
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',retireGuide,{once:true});else retireGuide();
})();
