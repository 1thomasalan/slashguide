/* Slash Guide: copy buttons, search + filter, the / key, Short facade. No tracking. */
(function () {
  "use strict";

  // ---- copy
  function copyText(t) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(t);
    return new Promise(function (ok, fail) {
      var ta = document.createElement("textarea");
      ta.value = t; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy") ? ok() : fail(); } catch (e) { fail(e); }
      document.body.removeChild(ta);
    });
  }
  var live = document.createElement("p");
  live.className = "vh"; live.setAttribute("aria-live", "polite");
  document.body.appendChild(live);

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-copy]");
    if (!b) return;
    ev.preventDefault();
    var t = b.getAttribute("data-copy"), l = b.querySelector(".copy-l"), old = l ? l.textContent : "";
    copyText(t).then(function () {
      b.classList.add("done"); if (l) l.textContent = "Copied";
      live.textContent = "Copied " + t;
      clearTimeout(b._t);
      b._t = setTimeout(function () { b.classList.remove("done"); if (l) l.textContent = old; }, 1600);
    }, function () {
      if (l) l.textContent = "Press Ctrl+C";
      live.textContent = "Copy didn't work here. Select the text and press Ctrl+C.";
    });
  });

  // ---- Short facade: load YouTube only when asked
  document.addEventListener("click", function (ev) {
    var p = ev.target.closest(".vid-play");
    if (!p) return;
    var box = p.closest("[data-yt]"), id = box.getAttribute("data-yt");
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) + "?autoplay=1&rel=0";
    f.title = "YouTube Short"; f.allow = "autoplay; encrypted-media; picture-in-picture"; f.allowFullscreen = true;
    box.innerHTML = ""; box.appendChild(f);
  });

  // ---- home: search + filter
  var q = document.getElementById("q");
  var rows = Array.prototype.slice.call(document.querySelectorAll(".row"));

  // "/" focuses search (home) or goes to it (other pages)
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "/" || ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var t = ev.target, tag = t && t.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || (t && t.isContentEditable)) return;
    ev.preventDefault();
    if (q) { q.focus(); q.select(); }
    else { var home = document.querySelector(".logo"); if (home) location.href = home.getAttribute("href") + "#search"; }
  });

  if (!q || !rows.length) return;
  var pills = Array.prototype.slice.call(document.querySelectorAll(".pill[data-sec]"));
  var secs = Array.prototype.slice.call(document.querySelectorAll(".sec"));
  var count = document.getElementById("count"), empty = document.getElementById("empty");
  var libH = document.getElementById("lib-h"), lib = document.getElementById("shortcuts");
  var calm = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var current = "all";
  rows.forEach(function (r) { r._q = r.getAttribute("data-q"); r._s = r.getAttribute("data-s"); });

  function apply() {
    var terms = q.value.toLowerCase().replace(/^\//, "").trim().split(/\s+/).filter(Boolean);
    var seen = {}, n = 0;
    rows.forEach(function (r) {
      var ok = (current === "all" || r._s === current) && terms.every(function (t) { return r._q.indexOf(t) > -1; });
      r.hidden = !ok;
      if (ok) { var k = r.querySelector(".row-a").getAttribute("href"); if (!seen[k]) { seen[k] = 1; n++; } }
    });
    document.querySelectorAll(".grp").forEach(function (g) { g.hidden = !g.querySelector(".row:not([hidden])"); });
    secs.forEach(function (s) { s.hidden = !s.querySelector(".row:not([hidden])"); });
    count.textContent = n + (n === 1 ? " shortcut" : " shortcuts");
    empty.hidden = n > 0;
  }
  function setSec(id) {
    current = id;
    pills.forEach(function (p) {
      var on = p.getAttribute("data-sec") === id;
      p.setAttribute("aria-pressed", String(on));
      if (on && libH) libH.textContent = p.getAttribute("data-title");
    });
    apply();
  }
  var timer;
  q.addEventListener("input", function () { clearTimeout(timer); timer = setTimeout(apply, 60); });
  q.addEventListener("keydown", function (ev) {
    if (ev.key === "Enter") { ev.preventDefault(); document.getElementById("shortcuts").scrollIntoView({ behavior: "smooth" }); }
    if (ev.key === "Escape") { q.value = ""; apply(); }
  });
  pills.forEach(function (p) {
    p.addEventListener("click", function () {
      setSec(p.getAttribute("data-sec"));
      lib.scrollIntoView({ behavior: calm ? "auto" : "smooth", block: "start" });
    });
  });
  document.querySelectorAll("[data-jump]").forEach(function (a) {
    a.addEventListener("click", function () { q.value = ""; setSec(a.getAttribute("data-jump")); });
  });
  document.querySelectorAll("[data-try]").forEach(function (b) {
    b.addEventListener("click", function () { q.value = b.getAttribute("data-try"); setSec("all"); q.focus(); });
  });

  var params = new URLSearchParams(location.search);
  if (params.get("q")) q.value = params.get("q");
  var s = params.get("s");
  if (s && pills.some(function (p) { return p.getAttribute("data-sec") === s; })) setSec(s); else apply();
  if (location.hash === "#search") q.focus();
})();

/* light / dark toggle: follows the system until the visitor picks; choice kept in localStorage only */
(function(){
  var btn=document.querySelector(".theme"); if(!btn) return;
  var root=document.documentElement, mq=window.matchMedia("(prefers-color-scheme: dark)");
  function cur(){return root.dataset.theme||(mq.matches?"dark":"light")}
  function sync(){var c=cur();btn.setAttribute("aria-label",c==="dark"?"Switch to light mode":"Switch to dark mode");
    document.querySelectorAll('meta[name="theme-color"]').forEach(function(m){m.content=c==="dark"?"#111112":"#ffffff";m.removeAttribute("media")})}
  btn.addEventListener("click",function(){var n=cur()==="dark"?"light":"dark";root.dataset.theme=n;try{localStorage.setItem("sg-theme",n)}catch(e){}sync()});
  if(mq.addEventListener) mq.addEventListener("change",sync);
  sync();
})();
