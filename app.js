const videoForm = document.querySelector('#youtube-search');
const videoInput = document.querySelector('#video-query');
const videoStatus = document.querySelector('#video-status');

videoForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const query = videoInput.value.trim();
  if (!query) {
    videoStatus.textContent = 'Введи, что хочешь найти.';
    videoInput.focus();
    return;
  }
  videoStatus.textContent = `Ищем «${query}» на YouTube…`;
  window.open(`https://www.youtube.com/results?search_query=${encodeURIComponent(query)}`, '_blank', 'noopener,noreferrer');
});

document.querySelectorAll('[data-video]').forEach((button) => {
  button.addEventListener('click', () => {
    videoInput.value = button.dataset.video;
    videoForm.requestSubmit();
  });
});

const spotifyForm = document.querySelector('#spotify-search');
const playlistInput = document.querySelector('#playlist-query');
const spotifyStatus = document.querySelector('#spotify-status');
const playerWrap = document.querySelector('#player-wrap');

spotifyForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const query = playlistInput.value.trim();
  if (!query) {
    spotifyStatus.textContent = 'Введи название плейлиста или настроение.';
    playlistInput.focus();
    return;
  }
  spotifyStatus.textContent = `Ищем «${query}» в Spotify…`;
  window.open(`https://open.spotify.com/search/${encodeURIComponent(query)}/playlists`, '_blank', 'noopener,noreferrer');
});

function spotifyEmbedUrl(raw) {
  try {
    const parsed = new URL(raw);
    if (!['open.spotify.com', 'www.open.spotify.com'].includes(parsed.hostname)) return null;
    const match = parsed.pathname.match(/^\/(playlist|album|track|episode|show)\/([A-Za-z0-9]+)\/?$/);
    if (!match) return null;
    return `https://open.spotify.com/embed/${match[1]}/${match[2]}?utm_source=generator&theme=0`;
  } catch {
    return null;
  }
}

function loadPlaylist() {
  const raw = document.querySelector('#spotify-url').value.trim();
  const embedUrl = spotifyEmbedUrl(raw);
  if (!embedUrl) {
    spotifyStatus.textContent = 'Проверь ссылку Spotify: подойдут ссылки на плейлист, альбом, трек или шоу.';
    return;
  }
  const frame = document.createElement('iframe');
  frame.title = 'Встроенный плеер Spotify';
  frame.src = embedUrl;
  frame.width = '100%';
  frame.height = '352';
  frame.style.border = '0';
  frame.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
  frame.loading = 'lazy';
  frame.setAttribute('allowfullscreen', '');
  playerWrap.replaceChildren(frame);
  spotifyStatus.textContent = 'Плеер загружен. Доступность воспроизведения зависит от Spotify и настроек аккаунта.';
}

document.querySelector('#load-playlist').addEventListener('click', loadPlaylist);
document.querySelector('#spotify-url').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') loadPlaylist();
});
