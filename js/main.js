/* ============================================
   YAHWAYLOVE — Main JS
   ============================================ */

// --- Dark Mode Toggle ---
(function () {
  const html = document.documentElement;
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  let theme = mq.matches ? 'dark' : 'light';
  html.setAttribute('data-theme', theme);

  document.addEventListener('DOMContentLoaded', () => {
    const toggles = document.querySelectorAll('[data-theme-toggle]');
    toggles.forEach(t => {
      updateIcon(t, theme);
      t.addEventListener('click', () => {
        theme = theme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', theme);
        toggles.forEach(btn => updateIcon(btn, theme));
      });
    });
  });

  function updateIcon(btn, t) {
    if (!btn) return;
    btn.setAttribute('aria-label', `Switch to ${t === 'dark' ? 'light' : 'dark'} mode`);
    btn.innerHTML = t === 'dark'
      ? `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
           <circle cx="12" cy="12" r="5"/>
           <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
         </svg>`
      : `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
           <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
         </svg>`;
  }
})();

// --- Mobile Nav ---
document.addEventListener('DOMContentLoaded', () => {
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const isOpen = navLinks.classList.contains('open');
      hamburger.setAttribute('aria-expanded', isOpen);
    });

    // Close on link click
    navLinks.querySelectorAll('a').forEach(a => {
      a.addEventListener('click', () => navLinks.classList.remove('open'));
    });
  }

  // --- Scroll Animations ---
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));

  // --- Active nav link ---
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.style.color = 'var(--brand-gold)';
    }
  });

  // --- Smooth counter animation ---
  document.querySelectorAll('[data-count]').forEach(el => {
    const target = parseInt(el.dataset.count);
    const duration = 2000;
    const step = target / (duration / 16);
    let current = 0;
    const obs = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        obs.disconnect();
        const timer = setInterval(() => {
          current += step;
          if (current >= target) {
            current = target;
            clearInterval(timer);
          }
          el.textContent = Math.floor(current).toLocaleString() + (el.dataset.suffix || '');
        }, 16);
      }
    }, { threshold: 0.5 });
    obs.observe(el);
  });
});

// --- Form submission via Formspree / email routing ---
document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('[data-form]');
  forms.forEach(form => {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = form.querySelector('[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = 'Sending…';
      btn.disabled = true;

      const data = Object.fromEntries(new FormData(form));
      data._subject = `YAHWAYLOVE Inquiry — ${data.service || 'General'}`;

      try {
        const res = await fetch('https://formspree.io/f/xwpbbzvy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
          body: JSON.stringify(data)
        });

        if (res.ok) {
          form.innerHTML = `
            <div style="text-align:center;padding:var(--space-12) 0;">
              <div style="font-size:3rem;margin-bottom:var(--space-4);">✝</div>
              <h3 style="font-family:var(--font-display);font-size:var(--text-xl);margin-bottom:var(--space-3);color:var(--color-text)">Message Received</h3>
              <p style="color:var(--color-text-muted);max-width:40ch;margin:0 auto;">We'll respond within 24 hours. In the meantime, God is already at work.</p>
            </div>`;
        } else {
          throw new Error();
        }
      } catch {
        btn.textContent = 'Error — Try Again';
        btn.disabled = false;
        setTimeout(() => { btn.textContent = originalText; btn.disabled = false; }, 3000);
      }
    });
  });
});
