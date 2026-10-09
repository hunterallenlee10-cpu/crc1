/* Castle Road Construction: site interactions (no dependencies). */
(() => {
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Dynamic years and copyright */
  const now = new Date().getFullYear();
  $$('[data-years]').forEach((el) => { el.textContent = String(now - 1992); });
  $$('[data-year]').forEach((el) => { el.textContent = String(now); });

  /* Header: solid once the page leaves the very top */
  const header = $('[data-header]');
  const sentinel = $('.header-sentinel');
  if (header && sentinel && 'IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => {
      header.classList.toggle('is-scrolled', !entry.isIntersecting);
    }).observe(sentinel);
  }

  /* Mobile menu */
  const toggle = $('[data-menu-toggle]');
  const menu = $('[data-menu]');
  if (toggle && menu) {
    const label = $('.sr-only', toggle);
    const setOpen = (open) => {
      toggle.setAttribute('aria-expanded', String(open));
      label.textContent = open ? 'Close menu' : 'Open menu';
      document.documentElement.classList.toggle('menu-open', open);
      document.body.style.overflow = open ? 'hidden' : '';
      if (open) {
        menu.hidden = false;
        $$('.mobile-links li', menu).forEach((li) => li.animate?.(
          [{ opacity: 0, transform: 'translateY(24px)' }, { opacity: 1, transform: 'none' }],
          { duration: reduceMotion ? 0 : 600, delay: reduceMotion ? 0 : 60 * Number(li.style.getPropertyValue('--i')), easing: 'cubic-bezier(0.16,1,0.3,1)', fill: 'backwards' }
        ));
        $('a', menu)?.focus();
      } else {
        menu.hidden = true;
      }
    };
    toggle.addEventListener('click', () => setOpen(toggle.getAttribute('aria-expanded') !== 'true'));
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { setOpen(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 1024px)').addEventListener('change', (e) => { if (e.matches) setOpen(false); });
  }

  /* Scroll reveal */
  const revealEls = $$('[data-reveal]');
  if (revealEls.length && 'IntersectionObserver' in window && !reduceMotion) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add('is-in'); io.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('is-in'));
  }

  /* Statement: split into words so each can brighten as it scrolls into view */
  $$('[data-statement]').forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.setAttribute('aria-label', el.textContent.trim());
    el.innerHTML = words.map((w) => `<span class="w" aria-hidden="true">${w}</span>`).join(' ');
  });

  /* Home services: hover or focus a row to swap the preview image */
  $$('[data-services]').forEach((section) => {
    const rows = $$('.svc-row', section);
    const imgs = $$('.svc-preview-frame img', section);
    const activate = (i) => {
      rows.forEach((r, n) => r.classList.toggle('is-active', n === i));
      imgs.forEach((img, n) => img.classList.toggle('is-active', n === i));
    };
    rows.forEach((row, i) => {
      row.addEventListener('mouseenter', () => activate(i));
      row.addEventListener('focus', () => activate(i));
    });
    if (window.matchMedia('(min-width: 900px)').matches) activate(0);
  });

  /* Testimonial slider */
  $$('[data-slider]').forEach((root) => {
    const slides = $$('[data-slide]', root);
    if (slides.length < 2) return;
    let index = 0;
    const current = $('[data-current]', root);
    $('[data-total]', root).textContent = String(slides.length);
    const show = (i) => {
      index = (i + slides.length) % slides.length;
      slides.forEach((s, n) => {
        s.classList.toggle('is-active', n === index);
        s.setAttribute('aria-hidden', String(n !== index));
      });
      $$('.quote-media img', root).forEach((img, n) => img.classList.toggle('is-active', n === index));
      current.textContent = String(index + 1);
    };
    $('[data-prev]', root).addEventListener('click', () => show(index - 1));
    $('[data-next]', root).addEventListener('click', () => show(index + 1));
    let startX = null;
    root.addEventListener('pointerdown', (e) => { startX = e.clientX; });
    root.addEventListener('pointerup', (e) => {
      if (startX === null) return;
      const dx = e.clientX - startX;
      if (Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
      startX = null;
    });
    show(0);
  });

  /* Services page: highlight the chip for the section in view */
  const svcNav = $('[data-svc-nav]');
  if (svcNav && 'IntersectionObserver' in window) {
    const links = $$('a', svcNav);
    const map = new Map(links.map((a) => [a.getAttribute('href').slice(1), a]));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        links.forEach((a) => a.classList.remove('is-current'));
        const link = map.get(entry.target.id);
        if (link) {
          link.classList.add('is-current');
          if (svcNav.scrollWidth > svcNav.clientWidth) svcNav.scrollTo({ left: link.offsetLeft - 16, behavior: reduceMotion ? 'auto' : 'smooth' });
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    map.forEach((_, id) => { const t = document.getElementById(id); if (t) io.observe(t); });
  }

  /* Gallery: filters + lightbox */
  const gallery = $('[data-gallery]');
  if (gallery) {
    const tiles = $$('.tile', gallery);
    const filters = $$('[data-filter]');
    filters.forEach((btn) => {
      const cat = btn.dataset.filter;
      const count = cat === 'all' ? tiles.length : tiles.filter((t) => t.dataset.cat.split(' ').includes(cat)).length;
      const sup = $('sup', btn);
      if (sup) sup.textContent = String(count);
      btn.addEventListener('click', () => {
        filters.forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
        tiles.forEach((t) => { t.hidden = !(cat === 'all' || t.dataset.cat.split(' ').includes(cat)); });
      });
    });

    const dialog = $('[data-lightbox]');
    const lbImg = $('img', dialog);
    const lbCap = $('figcaption', dialog);
    const lbCount = $('[data-lb-count]', dialog);
    let list = [];
    let pos = 0;
    const render = () => {
      const tile = list[pos];
      const img = $('img', tile);
      lbImg.src = img.currentSrc || img.src;
      lbImg.srcset = img.srcset;
      lbImg.sizes = '90vw';
      lbImg.alt = img.alt;
      lbCap.textContent = $('.tile-cap span', tile).textContent;
      lbCount.textContent = `${pos + 1} of ${list.length}`;
    };
    const open = (tile) => {
      list = tiles.filter((t) => !t.hidden);
      pos = list.indexOf(tile);
      render();
      dialog.showModal();
      document.body.style.overflow = 'hidden';
    };
    const step = (d) => { pos = (pos + d + list.length) % list.length; render(); };
    tiles.forEach((tile) => $('.tile-btn', tile).addEventListener('click', () => open(tile)));
    $('[data-lb-close]', dialog).addEventListener('click', () => dialog.close());
    $('[data-lb-prev]', dialog).addEventListener('click', () => step(-1));
    $('[data-lb-next]', dialog).addEventListener('click', () => step(1));
    dialog.addEventListener('close', () => { document.body.style.overflow = ''; });
    dialog.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
    });
    dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
    let sx = null;
    dialog.addEventListener('touchstart', (e) => { sx = e.touches[0].clientX; }, { passive: true });
    dialog.addEventListener('touchend', (e) => {
      if (sx === null) return;
      const dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 50) step(dx < 0 ? 1 : -1);
      sx = null;
    });
  }

  /* Forms: inline validation, then submit (Netlify Forms compatible) */
  $$('[data-form]').forEach((form) => {
    const status = $('[data-form-status]', form);
    const button = $('button[type="submit"]', form);
    const fields = $$('input[required], textarea[required]', form);

    const validate = (input) => {
      const field = input.closest('.field');
      let ok = input.value.trim() !== '';
      if (ok && input.type === 'email') ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim());
      if (ok && input.type === 'tel') ok = input.value.replace(/\D/g, '').length >= 10;
      field?.classList.toggle('has-error', !ok);
      input.setAttribute('aria-invalid', String(!ok));
      const err = field && $('.field-error', field);
      if (err) input.setAttribute('aria-describedby', err.id);
      return ok;
    };
    fields.forEach((input) => {
      input.addEventListener('blur', () => { if (input.value) validate(input); });
      input.addEventListener('input', () => { if (input.closest('.field')?.classList.contains('has-error')) validate(input); });
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const results = fields.map(validate);
      if (results.includes(false)) {
        fields[results.indexOf(false)].focus();
        status.textContent = 'Please fix the highlighted fields.';
        status.classList.add('is-error');
        return;
      }
      status.classList.remove('is-error');
      status.textContent = 'Sending...';
      button.setAttribute('aria-busy', 'true');
      try {
        const endpoint = form.dataset.endpoint || '/';
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: form.dataset.endpoint
            ? { Accept: 'application/json' }
            : { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: form.dataset.endpoint ? new FormData(form) : new URLSearchParams(new FormData(form)).toString(),
        });
        if (!res.ok) throw new Error(String(res.status));
        const done = document.createElement('div');
        done.className = 'form-success';
        done.setAttribute('tabindex', '-1');
        done.innerHTML = `<svg class="icon" aria-hidden="true"><use href="#i-check-circle"/></svg>
          <h3>Thanks for submitting!</h3>
          <p>We received your request and will be in touch shortly to schedule your free estimate. Need us sooner? Call <a href="tel:+14108365515"><strong>410-836-5515</strong></a>.</p>`;
        form.replaceChildren(done);
        done.focus();
      } catch (err) {
        button.removeAttribute('aria-busy');
        status.classList.add('is-error');
        status.innerHTML = 'Something went wrong sending your request. Please call us at <a href="tel:+14108365515"><strong>410-836-5515</strong></a>.';
      }
    });
  });
})();
