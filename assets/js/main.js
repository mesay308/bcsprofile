(() => {
  const header = document.querySelector('.site-header');
  const burger = document.getElementById('mobile-menu-btn');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const outlineBtn = document.getElementById('outline-menu-btn');
  const outlinePanel = document.getElementById('outline-panel');
  const navLinks = [...document.querySelectorAll('.nav-link')];
  const outlineLinks = [...document.querySelectorAll('.outline-link')];

  const closeOutline = () => {
    if (!outlinePanel || !outlineBtn) return;
    outlinePanel.classList.add('hidden');
    outlineBtn.setAttribute('aria-expanded', 'false');
  };

  const closeMobile = () => {
    if (!mobileDrawer || !burger) return;
    mobileDrawer.classList.add('hidden');
    burger.setAttribute('aria-expanded', 'false');
  };

  if (burger && mobileDrawer) {
    burger.addEventListener('click', () => {
      const isHidden = mobileDrawer.classList.toggle('hidden');
      burger.setAttribute('aria-expanded', String(!isHidden));
      closeOutline();
    });
    mobileDrawer.querySelectorAll('a').forEach((a) => a.addEventListener('click', closeMobile));
  }

  if (outlineBtn && outlinePanel) {
    outlineBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const isHidden = outlinePanel.classList.toggle('hidden');
      outlineBtn.setAttribute('aria-expanded', String(!isHidden));
    });
    outlineLinks.forEach((a) => a.addEventListener('click', closeOutline));
    document.addEventListener('click', (e) => {
      if (!outlinePanel.classList.contains('hidden') && !outlinePanel.contains(e.target) && !outlineBtn.contains(e.target)) {
        closeOutline();
      }
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeOutline();
      closeMobile();
    }
  });

  // Map every section ID to its top-nav group ID so primary nav stays highlighted accurately
  const topMap = {
    s1: 's1', s2: 's1', s3: 's1', s4: 's5',
    s5: 's5', s6: 's6', s7: 's7', s8: 's7',
    s9: 's9', s10: 's11', s11: 's11', contact: 'contact'
  };

  const setActive = (id) => {
    const mapped = topMap[id] || id;
    navLinks.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === '#' + mapped));
    outlineLinks.forEach((a) => a.classList.toggle('is-active', a.getAttribute('href') === '#' + id));
  };

  const sections = [...document.querySelectorAll('section[data-sec]')];
  const io = new IntersectionObserver(
    (entries) => {
      const visible = entries.filter((e) => e.isIntersecting);
      if (visible.length) {
        visible.sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top));
        setActive(visible[0].target.id);
      }
    },
    { rootMargin: '-25% 0px -60% 0px' }
  );
  sections.forEach((s) => io.observe(s));

  // Hide header on scroll down, show on scroll up or near top
  let lastY = window.scrollY;
  window.addEventListener(
    'scroll',
    () => {
      const y = window.scrollY;
      const menuOpen =
        (mobileDrawer && !mobileDrawer.classList.contains('hidden')) ||
        (outlinePanel && !outlinePanel.classList.contains('hidden'));
      if (y > lastY && y > 96 && !menuOpen) {
        header.classList.add('is-hidden');
      } else if (y < lastY || y <= 96) {
        header.classList.remove('is-hidden');
      }
      lastY = y;
    },
    { passive: true }
  );
})();
