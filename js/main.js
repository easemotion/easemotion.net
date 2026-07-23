/* =====================================
   Easemotion — Main JavaScript
   ===================================== */

document.addEventListener('DOMContentLoaded', () => {

  // ---- Mobile nav toggle ----
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
    });
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!toggle.contains(e.target) && !nav.contains(e.target)) {
        nav.classList.remove('open');
      }
    });
  }

  // ---- Lightbox ----
  const lightbox = document.getElementById('lightbox');
  const lbContent = document.getElementById('lb-content');
  const lbClose = document.querySelector('.lightbox-close');
  const lbPrev = document.querySelector('.lightbox-prev');
  const lbNext = document.querySelector('.lightbox-next');
  const lbTitle = document.querySelector('.lightbox-title');
  const lbCounter = document.querySelector('.lightbox-counter');

  let lbItems = [];
  let lbIndex = 0;

  window.openLightbox = function(items, index) {
    lbItems = items;
    lbIndex = index;
    renderLightbox();
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
  };

  function renderLightbox() {
    const item = lbItems[lbIndex];
    lbContent.innerHTML = '';

    if (lbCounter) {
      lbCounter.textContent = `${lbIndex + 1} / ${lbItems.length}`;
    }

    if (item.type === 'vimeo') {
      const iframe = document.createElement('iframe');
      iframe.className = 'lightbox-video';
      iframe.src = `https://player.vimeo.com/video/${item.video}?autoplay=1&dnt=1`;
      iframe.allow = 'autoplay; fullscreen';
      iframe.allowFullscreen = true;
      lbContent.appendChild(iframe);
      lbPrev.style.display = 'none';
      lbNext.style.display = 'none';
    } else if (item.type === 'youtube') {
      const iframe = document.createElement('iframe');
      iframe.className = 'lightbox-video';
      iframe.src = `https://www.youtube.com/embed/${item.video}?autoplay=1`;
      iframe.allow = 'autoplay; fullscreen';
      iframe.allowFullscreen = true;
      lbContent.appendChild(iframe);
      lbPrev.style.display = 'none';
      lbNext.style.display = 'none';
    } else if (item.type === 'image') {
      const img = document.createElement('img');
      img.className = 'lightbox-image';
      img.src = item.src;
      img.alt = item.title || '';
      lbContent.appendChild(img);
      lbPrev.style.display = lbItems.length > 1 ? 'block' : 'none';
      lbNext.style.display = lbItems.length > 1 ? 'block' : 'none';
    }

    if (lbTitle) {
      lbTitle.textContent = item.title || '';
    }
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    lbContent.innerHTML = '';
    document.body.style.overflow = '';
  }

  if (lbClose) lbClose.addEventListener('click', closeLightbox);
  if (lbPrev) lbPrev.addEventListener('click', () => {
    lbIndex = (lbIndex - 1 + lbItems.length) % lbItems.length;
    renderLightbox();
  });
  if (lbNext) lbNext.addEventListener('click', () => {
    lbIndex = (lbIndex + 1) % lbItems.length;
    renderLightbox();
  });

  // Close on backdrop click
  if (lightbox) {
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) closeLightbox();
    });
  }

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && lightbox?.classList.contains('active')) {
      closeLightbox();
    }
    if (e.key === 'ArrowLeft' && lbPrev?.style.display !== 'none') {
      lbPrev.click();
    }
    if (e.key === 'ArrowRight' && lbNext?.style.display !== 'none') {
      lbNext.click();
    }
  });

});
