/* The optional practice area never replaces the native setup or real-company defaults. */
frappe.after_ajax(() => {
  if (!frappe.boot?.yousr_practice) return;
  const ar=String(frappe.boot.lang||'').startsWith('ar');
  const link=document.createElement('a');
  link.href='/app/yousr-practice';
  link.className='btn btn-default btn-sm';
  link.textContent=ar?'البيانات التدريبية · DEMO':'Practice data · DEMO';
  link.setAttribute('aria-label',link.textContent);
  const item=document.createElement('li');item.className='nav-item';item.append(link);
  document.querySelector('.navbar .navbar-nav')?.prepend(item);
});
