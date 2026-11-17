frappe.pages['yousr-practice'].on_page_load = function(wrapper) {
  const ar=String(frappe.boot.lang||'').startsWith('ar'),t=(en,arabic)=>ar?arabic:en;
  const page=frappe.ui.make_app_page({parent:wrapper,title:t('Practice area · DEMO','مساحة التدريب · DEMO'),single_column:true});
  const root=document.createElement('section');root.className='yousr-practice';page.main.append(root);
  const el=(tag,text,cls,parent=root)=>{const e=document.createElement(tag);if(text)e.textContent=text;if(cls)e.className=cls;parent.append(e);return e;};
  const banner=el('div',null,'practice-notice');banner.setAttribute('role','note');
  el('h2',t('Fictional data. Your real company stays separate.','بيانات وهمية. شركتك الحقيقية تبقى مستقلة.'),null,banner);
  el('p',t('These sample customers, items and drafts belong to Yousr Practice - DEMO. Your real company remains the default. Practice documents cannot be submitted, paid or sent to ZATCA.','العملاء والأصناف والمسودات هنا تابعة لشركة التدريب. تبقى شركتك الحقيقية افتراضية. لا يمكن اعتماد المستندات التدريبية أو دفعها أو إرسالها إلى هيئة الزكاة.'),null,banner);
  const status=el('p',t('Checking practice data…','جارٍ التحقق من البيانات التدريبية…'));status.setAttribute('role','status');
  const records=el('div',null,'practice-records');
  const refresh=()=>frappe.call({method:'yousr_saudilization.demo_setup.status',callback:({message:s})=>{
    records.replaceChildren();status.textContent=({Ready:t('Ready to explore. Open a DEMO record below.','جاهزة للاستكشاف. افتح أحد المستندات التدريبية أدناه.'),Queued:t('Your real workspace is ready. Optional practice data is queued. You can continue working.','مساحة عملك جاهزة. البيانات التدريبية قيد الانتظار ويمكنك متابعة العمل.'),Building:t('Preparing optional practice data…','جارٍ إعداد البيانات التدريبية الاختيارية…'),Failed:t('Your real workspace is ready. Practice data could not be prepared; your business data was not changed.','مساحة عملك جاهزة. تعذر إعداد البيانات التدريبية دون تغيير بيانات أعمالك.')}[s.status]||t('Practice data was not requested.','لم تُطلب بيانات تدريبية.'));
    for(const r of s.records||[]){const b=el('button',r.doctype+' · '+r.name,'btn btn-default',records);b.type='button';b.addEventListener('click',()=>frappe.set_route('Form',r.doctype,r.name));}
    if(s.status==='Failed'){const b=el('button',t('Retry practice setup','إعادة محاولة إعداد التدريب'),'btn btn-primary',records);b.addEventListener('click',()=>{b.disabled=true;frappe.call({method:'yousr_saudilization.demo_setup.retry',callback:refresh,always:()=>{b.disabled=false}});});}
  }});
  page.set_secondary_action(t('Refresh status','تحديث الحالة'),refresh);refresh();
  el('h2',t('ZATCA response examples','أمثلة استجابات هيئة الزكاة'));
  el('p',t('SIMULATED EXAMPLES — not actual ZATCA approvals, submissions or legal tax invoices. No tax credentials are connected to this practice company. Actual sandbox testing requires a separately configured test environment.','أمثلة محاكاة — ليست موافقات أو إرسالات فعلية للهيئة أو فواتير ضريبية قانونية. شركة التدريب غير مرتبطة بمفاتيح ضريبية. الاختبار الفعلي يتطلب بيئة اختبار مستقلة.'));
  const cases=[
    [t('Standard invoice · example acceptance','فاتورة قياسية · مثال قبول'),t('Illustrative clearance response','استجابة تخليص توضيحية'),t('Complete buyer information and matching invoice totals.','معلومات المشتري مكتملة وإجماليات الفاتورة متطابقة.'),'success'],
    [t('Simplified invoice · example acceptance','فاتورة مبسطة · مثال قبول'),t('Illustrative reporting response','استجابة إبلاغ توضيحية'),t('Example of a consumer invoice reporting outcome.','مثال توضيحي لنتيجة إبلاغ فاتورة مستهلك.'),'success'],
    [t('Standard invoice · example rejection','فاتورة قياسية · مثال رفض'),t('Example: buyer details missing','مثال: نقص بيانات المشتري'),t('Review required buyer VAT and address information, correct it and validate before resubmission.','راجع بيانات الضريبة والعنوان المطلوبة للمشتري وصححها وتحقق منها قبل إعادة الإرسال.'),'danger'],
    [t('Invoice totals · example rejection','إجماليات الفاتورة · مثال رفض'),t('Example: totals do not match','مثال: الإجماليات غير متطابقة'),t('The example shows VAT15 on a100 line: the total must be115, not110.','يعرض المثال ضريبة15 على بند100: الإجمالي115 وليس110.'),'danger']
  ];
  const grid=el('div',null,'practice-examples');
  for(const [title,outcome,explanation,kind]of cases){const card=el('article',null,'practice-example',grid);el('span',t('DEMO · SIMULATED','تدريب · محاكاة'),'practice-label',card);el('h3',title,null,card);el('p',outcome,'text-'+kind,card);el('p',explanation,null,card);el('p',t('Sample line SAR100 · VAT15 · total115','بند تجريبي100 ر.س · ضريبة15 · إجمالي115'),null,card);}
};
