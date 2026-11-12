/* Hållfjället – bildspel, meny, ljus/mörk logga, till toppen och LÄS MER. */
(function () {
  var rot = document.documentElement;
  var smal = window.matchMedia('(max-width: 800px)');
  var lugn = window.matchMedia('(prefers-reduced-motion: reduce)');
  var sprak = /^en/i.test(rot.lang) ? 'en' : 'sv';

  /* ---------- Bildspelet ---------- */
  var bilder = [].slice.call(document.querySelectorAll('.bildspel img'));
  var nu = 0;
  var FORSTA = 2000;   // första bytet kommer tidigt, så att man ser att det är ett bildspel
  var TEMPO = 3500;    // därefter 3,5 sekunder per bild (övertoningen är 1,6 s, se hf.css)

  function ladda(img) {
    if (img && img.dataset.srcset) {
      img.srcset = img.dataset.srcset;
      img.src = img.dataset.src;
      img.removeAttribute('data-srcset');
    }
  }
  function bildAr(img, nyckel) { return img && img.getAttribute('data-ljus-' + nyckel) === '1'; }
  function aktuellLjus() { return bildAr(bilder[nu], smal.matches ? 'm' : 'd'); }

  function visa(i) {
    var forra = bilder[nu];
    nu = i;
    bilder.forEach(function (b) { if (b !== forra) b.className = ''; });
    forra.className = 'under';
    bilder[nu].className = 'synlig';
    ladda(bilder[(nu + 1) % bilder.length]);
    farg();
  }
  function nasta() {
    var i = (nu + 1) % bilder.length, img = bilder[i];
    ladda(img);
    if (document.hidden) return setTimeout(nasta, TEMPO);
    if (img.complete && img.naturalWidth) { visa(i); return setTimeout(nasta, TEMPO); }
    img.addEventListener('load', function () { visa(i); setTimeout(nasta, TEMPO); }, { once: true });
  }
  if (bilder.length > 1) {
    ladda(bilder[1]);
    if (!lugn.matches) setTimeout(nasta, FORSTA);
  }

  /* ---------- Logga och meny: ljusa på mörka bilder ---------- */
  var huvud = document.querySelector('.huvud');
  var ytor = [].slice.call(document.querySelectorAll('.hero, .bild'));
  function farg() {
    if (!huvud) return;
    var y = huvud.getBoundingClientRect().top + 10, ljus = false;
    ytor.forEach(function (s) {
      var r = s.getBoundingClientRect();
      if (r.top <= y && r.bottom >= y) {
        ljus = s.classList.contains('hero') ? aktuellLjus() : s.getAttribute('data-ljus-' + (smal.matches ? 'm' : 'd')) === '1';
      }
    });
    rot.classList.toggle('ljus-huvud', ljus);
    rot.classList.toggle('ljus-logga', aktuellLjus()); // loggan följer bildspelet, i samma färg som menyn
    if (toppen) toppen.classList.toggle('synlig', window.scrollY > window.innerHeight);
  }
  var vantar = false;
  function vidScroll() {
    if (vantar) return;
    vantar = true;
    window.requestAnimationFrame(function () { vantar = false; farg(); });
  }

  /* ---------- Till toppen ---------- */
  var toppen = document.querySelector('.till-toppen');
  if (toppen) toppen.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: lugn.matches ? 'auto' : 'smooth' });
  });

  window.addEventListener('scroll', vidScroll, { passive: true });
  window.addEventListener('resize', vidScroll);
  farg();

  /* ---------- Menyn ---------- */
  var meny = document.getElementById('meny');
  var oppna = document.querySelector('.menyknapp');
  var stang = meny && meny.querySelector('.stang');
  function sattMeny(oppen) {
    if (!meny) return;
    if (oppen && meny.dataset.bild) {
      var bredd = window.innerWidth * (window.devicePixelRatio || 1);
      var storlek = bredd > 1280 ? 1920 : bredd > 640 ? 1280 : 640;
      meny.style.backgroundImage = 'url(' + meny.dataset.bild.replace('{w}', storlek) + ')';
      meny.removeAttribute('data-bild');
    }
    meny.classList.toggle('oppen', oppen);
    meny.setAttribute('aria-hidden', String(!oppen));
    meny.inert = !oppen;
    oppna.setAttribute('aria-expanded', String(oppen));
    document.body.classList.toggle('meny-oppen', oppen);
    if (oppen) { var forsta = meny.querySelector('a'); if (forsta) forsta.focus({ preventScroll: true }); }
    else oppna.focus({ preventScroll: true });
  }
  if (meny && oppna) {
    meny.inert = true;
    oppna.addEventListener('click', function () { sattMeny(true); });
    stang.addEventListener('click', function () { sattMeny(false); });
    meny.addEventListener('click', function (e) { if (e.target.closest('a')) sattMeny(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && meny.classList.contains('oppen')) sattMeny(false); });
  }

  /* ---------- LÄS MER / VISA MINDRE ---------- */
  var TEXT = { sv: ['Läs mer', 'Visa mindre'], en: ['Read more', 'Show less'] };
  var nr = 0;
  function ord(p) { return (p.textContent.match(/\S+/g) || []).length; }
  function aktiv(box) { return !box.classList.contains('bara-mobil') || smal.matches; }

  function bygg(box) {
    var stycken = [].filter.call(box.children, function (c) { return c.tagName === 'P' && c.textContent.trim(); });
    if (stycken.length < 3) return;
    // Bryt vid det styckeskifte som ligger närmast halva texten
    var efter = parseInt(box.getAttribute('data-las-mer-efter'), 10);
    if (!efter) {
      var total = 0, summa = 0, bast = Infinity;
      stycken.forEach(function (p) { total += ord(p); });
      for (var i = 0; i < stycken.length - 1; i++) {
        summa += ord(stycken[i]);
        var skillnad = Math.abs(summa - total / 2);
        if (skillnad < bast) { bast = skillnad; efter = i + 1; }
      }
    }
    var sista = stycken[efter - 1];
    var more = document.createElement('div'), inner = document.createElement('div');
    more.className = 'lm-more'; inner.className = 'lm-inner'; more.id = 'las-mer-' + (++nr);
    while (sista.nextSibling) inner.appendChild(sista.nextSibling); // texten flyttas, ingenting ändras
    more.appendChild(inner);
    var rad = document.createElement('p');
    rad.className = 'lm-knapp-rad';
    rad.innerHTML = '<button type="button" class="lm-knapp" aria-expanded="false"><span class="lm-etikett"></span></button>';
    var knapp = rad.firstChild;
    knapp.setAttribute('aria-controls', more.id);
    knapp.firstChild.textContent = TEXT[sprak][0];
    box.appendChild(more); box.appendChild(rad);
    knapp.addEventListener('click', function () { vaxla(box, !box.classList.contains('lm-open')); });
    more.addEventListener('transitionend', function (e) {
      if (e.target !== more || e.propertyName !== 'height') return;
      if (box.classList.contains('lm-open')) more.style.height = 'auto';
      else more.inert = aktiv(box);
    });
    synka(box);
  }
  function vaxla(box, oppen) {
    var more = box.querySelector('.lm-more'), knapp = box.querySelector('.lm-knapp');
    knapp.classList.add('lm-byter');
    setTimeout(function () { knapp.firstChild.textContent = TEXT[sprak][oppen ? 1 : 0]; knapp.classList.remove('lm-byter'); }, 200);
    knapp.setAttribute('aria-expanded', String(oppen));
    var fran = more.getBoundingClientRect().height, till = oppen ? more.scrollHeight : 0;
    more.inert = false;
    if (!oppen) {
      // Har man läst långt ner glider sidan mjukt tillbaka, så att man inte tappar bort sig
      var topp = more.getBoundingClientRect().top;
      if (topp < window.innerHeight * 0.25) window.scrollBy({ top: topp - window.innerHeight * 0.55, behavior: lugn.matches ? 'auto' : 'smooth' });
    }
    more.style.height = fran + 'px';
    more.offsetHeight;
    box.classList.toggle('lm-open', oppen);
    more.style.height = till + 'px';
    if (lugn.matches) { more.style.height = oppen ? 'auto' : '0px'; if (!oppen) more.inert = true; }
  }
  function synka(box) {
    var more = box.querySelector('.lm-more');
    if (more) more.inert = aktiv(box) && !box.classList.contains('lm-open');
  }
  var lasMer = [].slice.call(document.querySelectorAll('.las-mer'));
  lasMer.forEach(bygg);
  smal.addEventListener('change', function () { lasMer.forEach(synka); farg(); });
})();
