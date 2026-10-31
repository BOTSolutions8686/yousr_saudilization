// Presentation only: retain native routes, roles, permissions and theme choice.
document.documentElement.classList.add("yousr-erp");
(() => {
  // v16 core, setup wizard and optional HR rails use fixed icons rather than Navbar Settings.
  // Replace only these known framework-owned images; preserve tenant icons.
  const brandRail = () => {
    document.querySelectorAll('.dock .header-logo img[src="/assets/erpnext/images/erpnext-logo.svg"], .dock .header-logo img[src="/assets/hrms/images/frappe-hr-logo.svg"], .setup-intro__logo[src="/assets/erpnext/images/erpnext-logo.svg"]').forEach((image) => {
      image.src = "/assets/yousr_saudilization/images/yousrerp-favicon.svg";
      image.alt = "YousrERP";
    });
    // Only the native setup checklist subtitle: retain counters, controls and
    // document content, and keep the surrounding English/Arabic translation.
    document.querySelectorAll('.onboarding-widget-box .widget-subtitle').forEach((subtitle) => {
      subtitle.childNodes.forEach((node) => {
        if (node.nodeType === 3 && node.textContent.includes('ERPNext')) {
          node.textContent = node.textContent.replace(/\bERPNext\b/g, 'YousrERP');
        }
      });
    });
  };
  const start = () => {
    brandRail();
    let scheduled = false;
    new MutationObserver(() => {
      if (scheduled) return;
      scheduled = true;
      requestAnimationFrame(() => { scheduled = false; brandRail(); });
    }).observe(document.body, {childList: true, characterData: true, subtree: true});
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once: true});
  else start();
})();
