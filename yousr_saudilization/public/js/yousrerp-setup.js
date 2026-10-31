/* Supported setup-wizard extension hooks. Native saves, validation and routes remain intact. */
(() => {
  if (!frappe.setup?.on || frappe.setup.__yousr_setup_registered) return;
  frappe.setup.__yousr_setup_registered = true;
  const t = (en, ar) => String(frappe.boot.lang || '').startsWith('ar') ? ar : en;
  const context = frappe.boot.yousr_setup || {};
  const text = (value) => typeof value === 'string' ? value : '';
  const field = (slide, name) => (slide.fields || []).find((item) => item.fieldname === name);
  const defaultValue = (slide, name, value) => {
    const item = field(slide, name);
    if (item && text(value) && !item.default) item.default = value;
  };
  frappe.setup.on('before_load', () => {
    frappe.setup.intro_apps = [{logo:'/assets/yousr_saudilization/images/yousrerp-favicon.svg', setup_wizard_text:t('Your workspace is ready. Let’s make it yours.','مساحة عملك جاهزة. لنجهزها لأعمالك.')}];
    for (const slide of frappe.setup.slides) {
      if (slide.name === 'welcome') {
        slide.title = t('A familiar starting point','بداية تناسب أعمالك');
        slide.help = t('Check your language, country and currency. You can keep the suggested choices.','راجع اللغة والدولة والعملة. يمكنك استخدام الخيارات المقترحة.');
        const telemetry = field(slide, 'enable_telemetry');
        if (telemetry) { telemetry.default = 0; telemetry.hidden = 1; }
      } else if (slide.name === 'user') {
        slide.title = t('Your workspace profile','ملفك داخل مساحة العمل');
        slide.help = t('Your YousrERP account is already created. Choose the contact name and email for this workspace. You can change the suggestions.','حسابك في يسر جاهز. اختر اسم التواصل والبريد لمساحة العمل هذه. يمكنك تعديل الاقتراحات.');
        defaultValue(slide, 'full_name', context.full_name);
        defaultValue(slide, 'email', context.email);
        if (field(slide, 'email')) field(slide, 'email').description = t('You can use a business email different from your portal sign-in. This will not change your portal account.','يمكنك استخدام بريد عمل مختلف عن بريد دخول البوابة. لن يغيّر ذلك حسابك في البوابة.');
      } else if (slide.name === 'persona') {
        slide.title = t('The way you work','طبيعة أعمالك');
        slide.help = t('Choose your activity and the tools you want to start with. This does not change your subscription.','اختر نشاطك والأدوات التي ستبدأ بها. هذا لا يغيّر اشتراكك.');
        defaultValue(slide, 'persona_industry', context.industry);
        for (const name of ['persona_implementing_for','persona_company_size','persona_current_system']) {
          if (field(slide,name)) field(slide,name).hidden = 1;
        }
      } else if (slide.name === 'organization') {
        slide.title = t('Your company, ready to work','جهّز شركتك للعمل');
        slide.help = t('Add your company name and choose when your financial year starts. Our team can help.','أضف اسم شركتك وحدد بداية السنة المالية. فريقنا جاهز للمساعدة.');
        defaultValue(slide, 'company_name', context.company_name);
        if (field(slide,'company_abbr')) field(slide,'company_abbr').label = t('Short company code','رمز الشركة المختصر');
      }
    }
  });
  frappe.setup.on('after_load', () => {
    const intro = document.querySelector('.setup-intro');
    if (intro && !intro.querySelector('.yousr-setup-welcome')) {
      const heading = document.createElement('h1');
      heading.className = 'yousr-setup-welcome';
      heading.textContent = t('Welcome to your YousrERP workspace','مرحباً بك في مساحة عمل يسر');
      intro.querySelector('.setup-intro__hello')?.before(heading);
      const steps = document.createElement('p');
      steps.className = 'yousr-setup-expectation';
      steps.textContent = t('Your preferences → Your profile → Your work → Your company','تفضيلاتك ← ملفك ← نشاطك ← شركتك');
      intro.querySelector('.setup-intro__tagline')?.after(steps);
      const button = intro.querySelector('.setup-intro__start');
      if (button) button.textContent = t('Set up my workspace','إعداد مساحة عملي');
    }
    const container = document.querySelector('.setup-wizard-slide');
    for (const target of [intro, container].filter(Boolean)) {
      if (target.querySelector('.yousr-setup-help')) continue;
      const link = document.createElement('a'); link.className = 'yousr-setup-help';
      const origin = ['https://yousrerp.com','https://stage.yousrerp.com'].includes(context.portal_url) ? context.portal_url : 'https://yousrerp.com';
      link.href = origin + '/help-and-sessions'; link.target = '_blank'; link.rel = 'noopener noreferrer';
      link.textContent = t('Need a hand? Ask the YousrERP team','تحتاج مساعدة؟ تواصل مع فريق يسر'); target.append(link);
    }
  });
})();
