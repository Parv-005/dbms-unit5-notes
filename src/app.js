(function () {
  var root = document.documentElement;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  var saved = store('u5-theme');
  if (saved) root.setAttribute('data-theme', saved);
  document.getElementById('themeBtn').addEventListener('click', function () {
    var cur = root.getAttribute('data-theme');
    if (!cur) cur = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    store('u5-theme', next);
  });
  var allOpen = false;
  document.getElementById('expandBtn').addEventListener('click', function () {
    allOpen = !allOpen;
    document.querySelectorAll('.pyq details, .mcq details').forEach(function (d) { d.open = allOpen; });
    this.textContent = allOpen ? '▴ Answers' : '▾ Answers';
  });
  var sb = document.getElementById('sidebar');
  document.getElementById('menuBtn').addEventListener('click', function () { sb.classList.toggle('open'); });
  sb.addEventListener('click', function (e) { if (e.target.tagName === 'A' && window.innerWidth <= 1000) sb.classList.remove('open'); });
  window.addEventListener('beforeprint', function () { document.querySelectorAll('details').forEach(function (d) { d.open = true; }); });
  // active section highlight
  var links = {};
  document.querySelectorAll('.toc a').forEach(function (a) { links[a.getAttribute('href').slice(1)] = a; });
  var heads = Array.prototype.slice.call(document.querySelectorAll('main h2[id], main h3[id]'));
  var current = null;
  function onScroll() {
    var y = window.scrollY + 90, best = null;
    for (var i = 0; i < heads.length; i++) { if (heads[i].offsetTop <= y) best = heads[i]; else break; }
    if (best && best !== current) {
      if (current && links[current.id]) links[current.id].classList.remove('active');
      current = best;
      var a = links[best.id];
      if (a) { a.classList.add('active'); var r = a.getBoundingClientRect(); if (r.top < 90 || r.bottom > window.innerHeight - 20) a.scrollIntoView({ block: 'center' }); }
    }
  }
  var tick = false;
  window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(function () { tick = false; onScroll(); }); } });
  onScroll();
})();
