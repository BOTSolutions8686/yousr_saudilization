// Presentation only: retain native routes, roles, permissions and theme choice.
document.documentElement.classList.add("yousr-erp");
(() => {
  // v16 core and optional HR rails use fixed icons rather than Navbar Settings.
  // Replace only these known framework-owned images; preserve tenant icons.
  const brandRail = () => {
    document.querySelectorAll('.dock .header-logo img[src="/assets/erpnext/images/erpnext-logo.svg"], .dock .header-logo img[src="/assets/hrms/images/frappe-hr-logo.svg"]').forEach((image) => {
      image.src = "/assets/yousr_saudilization/images/yousrerp-favicon.svg";
      image.alt = "YousrERP";
    });
  };
  const start = () => {
    brandRail();
    new MutationObserver(brandRail).observe(document.body, {childList: true, subtree: true});
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start, {once: true});
  else start();
})();
