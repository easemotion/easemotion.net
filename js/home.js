/* =====================================
   Easemotion — Home Page Randomizer
   ===================================== */

document.addEventListener('DOMContentLoaded', () => {
  const grid = document.getElementById('home-grid');
  if (!grid) return;

  // Fetch projects data
  fetch('data/projects.json')
    .then(r => r.json())
    .then(data => {
      const all = [...data.motion, ...data.illustration];

      // Shuffle (Fisher-Yates)
      for (let i = all.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [all[i], all[j]] = [all[j], all[i]];
      }

      // Pick 12 random projects
      const selected = all.slice(0, 12);

      // Render cards
      grid.innerHTML = selected.map((p, idx) => {
        const sizeClasses = ['', ' tall', '', ' short', '', ' xl', ''];
        const sizeClass = sizeClasses[idx % 7] || '';
        const isVideo = p.type === 'vimeo' || p.type === 'youtube';
        const playBtn = isVideo ? '<div class="play-indicator"></div>' : '';
        const label = isVideo ? 'Video' : 'Still';
        const title = escapeHtml(p.title);
        const thumb = escapeHtml(p.thumb);

        return `
          <a href="project.html?id=${escapeHtml(p.id)}" class="project-card${sizeClass}">
            <div class="thumb-wrap">
              <img src="${thumb}" alt="${title}" loading="lazy" />
              ${playBtn}
            </div>
            <div class="overlay">
              <h3>${title}</h3>
              <span class="label">${label}</span>
            </div>
          </a>`;
      }).join('');
    })
    .catch(() => {
      grid.innerHTML = '<p style="grid-column:1/-1;text-align:center;color:var(--text-dim);padding:60px 0;">Unable to load projects.</p>';
    });

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
});
