// Presentation only: retain native routes, roles, permissions and theme choice.
document.documentElement.classList.add("yousr-erp");
(() => {
  // v16's app rail uses ERPNext's fixed icon rather than Navbar Settings.
  // Replace that one framework-owned image; leave tenant/app icons alone.
  const brandRail = () => {
    document.querySelectorAll('.dock .header-logo img[src="/assets/erpnext/images/erpnext-logo.svg"]').forEach((image) => {
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
