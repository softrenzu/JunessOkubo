/* Site pageviews and upnow booking-link clicks via Google Analytics 4. */
(function () {
  "use strict";
  var measurementId = String(window.JEUNESSE_GA4_ID || "").trim();
  if (!/^G-[A-Z0-9]{6,15}$/.test(measurementId)) {
    return; // No GA4 property connected yet; never send data to an unknown property.
  }
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", measurementId, { send_page_view: true });
  var script = document.createElement("script");
  script.async = true;
  script.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(measurementId);
  document.head.appendChild(script);

  document.addEventListener("click", function (event) {
    var anchor = event.target && event.target.closest ? event.target.closest("a[href]") : null;
    if (!anchor) return;
    var target;
    try { target = new URL(anchor.href, window.location.href); } catch (err) { return; }
    if (target.hostname !== "upnow.jp" || !target.pathname.startsWith("/goodspace/jeunesse")) return;
    var path = window.location.pathname;
    gtag("event", "upnow_click", {
      link_domain: "upnow.jp",
      link_url: target.href,
      source_page: path,
      source_type: path.startsWith("/blog/") ? "blog" : "site",
      cta_position: (anchor.closest("header") ? "header" :
                     anchor.closest("footer") ? "footer" :
                     anchor.closest(".hero") ? "hero" :
                     anchor.closest(".article") ? "article" : "content"),
      transport_type: "beacon"
    });
  }, true);
})();
