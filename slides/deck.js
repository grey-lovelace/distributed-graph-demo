// Brand chrome + reveal.js setup. Decks should not need to edit this file.
(function(){
  var sections = Array.prototype.slice.call(document.querySelectorAll('.slides > section'));
  var brand = getComputedStyle(document.documentElement);
  function color(name){ return brand.getPropertyValue('--' + name).trim(); }

  sections.forEach(function(sec, i){
    var isSection = sec.classList.contains('slide-section');
    var isDark = isSection || sec.classList.contains('slide-title') || sec.classList.contains('slide-statement');

    // backgrounds: section dividers are cyan (or green / blue / red), other dark slides are navy
    if(isDark && !sec.hasAttribute('data-background-color')){
      var field = isSection ? (['green','blue','red'].filter(function(c){ return sec.classList.contains(c); })[0] || 'cyan') : 'navy';
      sec.setAttribute('data-background-color', color(field));
    }

    // logo mark top-right on every slide but the title: white on dividers, full color elsewhere
    if(!sec.classList.contains('slide-title')){
      var mark = document.createElement('img');
      mark.className = 'corner-mark'; mark.alt = '';
      mark.src = isSection ? 'assets/mark-white.png' : 'assets/mark.png';
      sec.appendChild(mark);
    }

    // brand footer (dots, rule, slide number) on white slides
    if(!isDark){
      var bar = document.createElement('div');
      bar.className = 'brandbar';
      bar.innerHTML = '<i class="d-red"></i><i class="d-green"></i><i class="d-cyan"></i><i class="d-blue"></i><span class="line"></span><span class="num">' + (i + 1) + '</span>';
      sec.appendChild(bar);
    }
  });

  // QR codes: <div class="qr" data-url="https://..."></div>
  // add class "plain" to leave out the logo in the middle
  // level H survives ~30% damage, which leaves room for the logo
  document.querySelectorAll('.qr[data-url]').forEach(function(el){
    var plain = el.classList.contains('plain');
    var qr = qrcode(0, plain ? 'M' : 'H');
    qr.addData(el.getAttribute('data-url')); qr.make();
    el.innerHTML = qr.createSvgTag({ cellSize: 8, margin: 2, scalable: true, alt: el.getAttribute('data-url') })
      + (plain ? '' : '<img class="qr-logo" src="assets/mark.png" alt="">');
  });

  // .build slides reveal their bullets one click at a time
  document.querySelectorAll('section.build li').forEach(function(li){ li.classList.add('fragment'); });

  // a slide is overflowing when content pokes past its 1280x720 box, or into the brand footer
  function overflows(sec){
    var box = sec.getBoundingClientRect(), scale = box.width / 1280 || 1;
    var bar = sec.querySelector('.brandbar');
    var floor = bar ? bar.getBoundingClientRect().top : box.bottom;
    return Array.prototype.some.call(sec.querySelectorAll('*'), function(el){
      // .body stretches to fill the slide, so measure what is inside it, not the box itself
      if(el.matches('.body') || el.closest('.brandbar')) return false;
      var r = el.getBoundingClientRect();
      if(!r.width && !r.height) return false;
      return (r.bottom - floor) / scale > 2 || (r.right - box.right) / scale > 2;
    });
  }
  function flagOverflow(sec){
    var flag = sec.querySelector('.overflow-flag');
    var bad = overflows(sec);
    if(bad && !flag){
      flag = document.createElement('div');
      flag.className = 'overflow-flag';
      flag.textContent = 'Too much on this slide — trim it or split it in two';
      sec.appendChild(flag);
    } else if(!bad && flag){ flag.remove(); }
    return bad;
  }

  // walk every slide and report overflowing content and missing images; used by the skill to check its work
  window.deckCheck = function(){
    var here = Reveal.getIndices(), bad = [], root = document.querySelector('.reveal');
    root.classList.add('no-anim');
    sections.forEach(function(sec, i){
      Reveal.slide(i, 0, -1);
      var t = sec.querySelector('h1,h2'), title = t ? t.textContent.trim() : '';
      if(flagOverflow(sec)) bad.push({ slide: i + 1, title: title, problem: 'too much content' });
      sec.querySelectorAll('img').forEach(function(img){
        if(img.complete && !img.naturalWidth) bad.push({ slide: i + 1, title: title, problem: 'missing image: ' + img.getAttribute('src') });
      });
    });
    Reveal.slide(here.h, here.v, here.f);
    root.classList.remove('no-anim');
    return bad;
  };

  Reveal.initialize({
    width: 1280, height: 720, margin: 0, center: false, maxScale: 4,
    hash: true, controls: false,
    transition: 'fade', transitionSpeed: 'fast',
    pdfSeparateFragments: false,
    plugins: [ RevealNotes ]
  });

  // click anywhere on a slide to go to the next one. Runs before reveal's own handlers (capture), so a
  // click that picks a slide in the overview is still seen as an overview click and left alone.
  document.querySelector('.reveal').addEventListener('click', function(e){
    if(Reveal.isOverview() || e.target.closest('a') || String(window.getSelection())) return;
    Reveal.next();
  }, true);

  // P: reload in print layout and open the print dialog, for printing or "Save as PDF"
  Reveal.addKeyBinding({ keyCode: 80, key: 'P', description: 'Print or save as PDF' }, function(){
    location.search = '?print-pdf&print';
  });
  var pdfReady = false;
  Reveal.on('pdf-ready', function(){
    pdfReady = true;
    if(/[?&]print(&|$)/.test(location.search)) setTimeout(function(){ window.print(); }, 300);
  });

  // In the print layout (?print-pdf), report what would look wrong in the PDF; used by the skill to check its work.
  // It finds slides that print on more than one page, content that is hidden or caught mid-animation,
  // and a blank page at the end.
  window.pdfCheck = function(){
    if(!/print-pdf/.test(location.search)) return [{ problem: 'open the deck with ?print-pdf in the URL, then run pdfCheck() again' }];
    if(!pdfReady) return [{ problem: 'the print layout is not ready yet; wait a second and run pdfCheck() again' }];
    var bad = [], pages = document.querySelectorAll('.reveal .pdf-page');
    Array.prototype.forEach.call(pages, function(page, i){
      var t = page.querySelector('h1,h2'), title = t ? t.textContent.trim() : '';
      var count = Math.round(page.offsetHeight / 720);
      if(count > 1) bad.push({ slide: i + 1, title: title, problem: 'prints on ' + count + ' pages; trim it until deckCheck() is clean' });
      // Text and pictures should print fully visible. A running animation or a low opacity means
      // the element printed in the middle of its entrance animation.
      Array.prototype.forEach.call(page.querySelectorAll('h1,h2,h3,p,li,img,svg,figure,.card,.panel'), function(el){
        if(!el.getBoundingClientRect().width) return;
        var running = el.getAnimations && el.getAnimations().some(function(a){ return a.playState === 'running'; });
        if(running || parseFloat(getComputedStyle(el).opacity) < 0.99){
          bad.push({ slide: i + 1, title: title, problem: 'prints hidden or mid-animation: ' + el.tagName.toLowerCase() + ' "' + el.textContent.trim().slice(0, 40) + '"' });
        }
      });
    });
    var last = pages[pages.length - 1];
    if(last && /page|always/.test(getComputedStyle(last).breakAfter)) bad.push({ problem: 'the PDF ends with a blank page' });
    return bad;
  };

  // replay the entrance animations each time a slide is shown, then check it once they settle
  function onShow(e){
    var sec = e.currentSlide;
    sec.classList.remove('anim'); void sec.offsetWidth; sec.classList.add('anim');
    setTimeout(function(){ flagOverflow(sec); }, 1400);
  }
  Reveal.on('ready', onShow);
  Reveal.on('slidechanged', onShow);
})();
