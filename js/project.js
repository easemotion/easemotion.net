/* =====================================
   Easemotion — Project Detail Page
   ===================================== */

document.addEventListener('DOMContentLoaded', () => {

  // Mobile nav toggle (reuse from main.js pattern)
  const toggle = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.nav-links');
  if (toggle && nav) {
    toggle.addEventListener('click', () => nav.classList.toggle('open'));
    document.addEventListener('click', (e) => {
      if (!toggle.contains(e.target) && !nav.contains(e.target)) nav.classList.remove('open');
    });
  }

  // Lightbox
  const lightbox = document.getElementById('lightbox');
  const lbContent = document.getElementById('lb-content');
  const lbClose = document.querySelector('.lightbox-close');
  const lbTitle = document.querySelector('.lightbox-title');
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
    if (item.type === 'vimeo') {
      const iframe = document.createElement('iframe');
      iframe.className = 'lightbox-video';
      iframe.src = `https://player.vimeo.com/video/${item.video}?autoplay=1&dnt=1`;
      iframe.allow = 'autoplay; fullscreen';
      iframe.allowFullscreen = true;
      lbContent.appendChild(iframe);
    } else if (item.type === 'youtube') {
      const iframe = document.createElement('iframe');
      iframe.className = 'lightbox-video';
      iframe.src = `https://www.youtube.com/embed/${item.video}?autoplay=1`;
      iframe.allow = 'autoplay; fullscreen';
      iframe.allowFullscreen = true;
      lbContent.appendChild(iframe);
    } else if (item.type === 'image') {
      const img = document.createElement('img');
      img.className = 'lightbox-image';
      img.src = item.src;
      img.alt = item.title || '';
      lbContent.appendChild(img);
    }
    if (lbTitle) lbTitle.textContent = item.title || '';
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    lbContent.innerHTML = '';
    document.body.style.overflow = '';
  }

  if (lbClose) lbClose.addEventListener('click', closeLightbox);
  if (lightbox) lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && lightbox?.classList.contains('active')) closeLightbox(); });

  // ---- Load project data ----
  const params = new URLSearchParams(window.location.search);
  const projectId = params.get('id');

  if (!projectId) {
    document.getElementById('project-root').innerHTML = `
      <div class="container" style="padding:120px 24px;text-align:center;">
        <h1>Project not found</h1>
        <p style="color:var(--text-dim);margin-top:12px;"><a href="index.html">← Back to home</a></p>
      </div>`;
    return;
  }

  // Fetch and render
  fetch('data/projects.json')
    .then(r => r.json())
    .then(data => {
      const allProjects = [...data.motion, ...data.illustration];
      const project = allProjects.find(p => p.id === projectId);

      if (!project) {
        document.getElementById('project-root').innerHTML = `
          <div class="container" style="padding:120px 24px;text-align:center;">
            <h1>Project not found</h1>
            <p style="color:var(--text-dim);margin-top:12px;"><a href="index.html">← Back to home</a></p>
          </div>`;
        return;
      }

      // Determine category for back link
      const isMotion = data.motion.find(p => p.id === projectId);
      const backLink = isMotion ? 'motion.html' : 'illustration.html';
      const categoryName = isMotion ? 'Motion' : 'Illustration';

      // Build media section
      let mediaHtml = '';
      if (project.type === 'vimeo') {
        mediaHtml = `
          <div class="project-video-wrap">
            <iframe src="https://player.vimeo.com/video/${project.video}?autoplay=0&dnt=1" allow="fullscreen" allowfullscreen></iframe>
          </div>`;
      } else if (project.type === 'youtube') {
        mediaHtml = `
          <div class="project-video-wrap">
            <iframe src="https://www.youtube.com/embed/${project.video}" allow="fullscreen" allowfullscreen></iframe>
          </div>`;
      } else if (project.type === 'image') {
        // Single image or gallery
        if (project.images && project.images.length > 1) {
          let imgs = project.images.map((img, i) =>
            `<img src="${escapeHtml(img)}" alt="${escapeHtml(project.title)}" loading="lazy"
                  onclick="openLightbox([${project.images.map((im,idx) =>
                `{type:'image',src:'${escapeHtml(im)}',title:'${escapeHtml(project.title)}'}`
              ).join(',')}], ${i})" />`
          ).join('');
          mediaHtml = `<div class="project-gallery">${imgs}</div>`;
        } else {
          const imgSrc = project.thumb || project.images?.[0];
          mediaHtml = `
            <div class="project-video-wrap">
              <img src="${escapeHtml(imgSrc)}" alt="${escapeHtml(project.title)}" style="cursor:pointer;"
                   onclick="openLightbox([{type:'image',src:'${escapeHtml(imgSrc)}',title:'${escapeHtml(project.title)}'}],0)" />
            </div>`;
        }
      }

      // Build meta
      const metaItems = [];
      if (project.client) metaItems.push({ label: 'Client', value: project.client });
      if (project.year) metaItems.push({ label: 'Year', value: project.year });
      if (project.cat) metaItems.push({ label: 'Category', value: project.cat });
      const metaHtml = metaItems.map(m =>
        `<div class="meta-item"><span class="label">${m.label}</span><span class="value">${escapeHtml(m.value)}</span></div>`
      ).join('');

      // Update title
      document.title = `${escapeHtml(project.title)} — Easemotion`;

      // Related works (same category, exclude current)
      const categoryProjects = isMotion ? data.motion : data.illustration;
      const related = categoryProjects
        .filter(p => p.id !== projectId)
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);

      let relatedHtml = '';
      if (related.length > 0) {
        relatedHtml = `
          <section class="related-section container">
            <div class="section-header">
              <h2>Related ${categoryName} Works</h2>
            </div>
            <div class="related-grid">
              ${related.map(p => {
                const label = p.type === 'image' ? 'Still' : 'Video';
                return `
                <a href="project.html?id=${p.id}" class="related-card">
                  <div class="thumb-wrap">
                    <img src="${escapeHtml(p.thumb)}" alt="${escapeHtml(p.title)}" loading="lazy" />
                  </div>
                  <div class="overlay">
                    <h3>${escapeHtml(p.title)}</h3>
                    <span class="label">${label}</span>
                  </div>
                </a>`;
              }).join('')}
            </div>
          </section>`;
      }

      // Render
      document.getElementById('project-root').innerHTML = `
        <section class="project-hero container">
          <a href="${backLink}" class="project-back">← Back to ${categoryName}</a>
          ${mediaHtml}

          <div class="project-info">
            <h1>${escapeHtml(project.title)}</h1>
            <div class="project-meta">${metaHtml}</div>
            <div class="project-description">
              <p>${escapeHtml(project.desc || '')}</p>
            </div>
          </div>
        </section>
        ${relatedHtml}
      `;
    })
    .catch(err => {
      document.getElementById('project-root').innerHTML = `
        <div class="container" style="padding:120px 24px;text-align:center;">
          <h1>Error loading project</h1>
          <p style="color:var(--text-dim);margin-top:8px;">${err.message}</p>
          <p style="margin-top:16px;"><a href="index.html">← Back to home</a></p>
        </div>`;
    });

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
});
