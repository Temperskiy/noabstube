const videoForm = document.querySelector('#youtube-search');
const videoInput = document.querySelector('#video-query');
const videoStatus = document.querySelector('#video-status');
const HISTORY_KEY = 'noabstube-history-v1';
const readHistory = () => {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '{"video":[],"spotify":[]}'); }
  catch { return { video: [], spotify: [] }; }
};
const saveHistory = (kind, item) => {
  const history = readHistory();
  history[kind] = [item, ...history[kind].filter((entry) => entry.value !== item.value)].slice(0, 5);
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  renderHistory();
};
function renderHistory() {
  const history = readHistory();
  [['video', '#video-history'], ['spotify', '#spotify-history']].forEach(([kind, selector]) => {
    const container = document.querySelector(selector);
    container.replaceChildren();
    if (!history[kind].length) {
      const empty = document.createElement('span');
      empty.className = 'empty-history';
      empty.textContent = kind === 'video' ? 'Здесь появятся недавние запросы.' : 'Здесь появятся запросы и плейлисты.';
      container.append(empty);
      return;
    }
    history[kind].forEach((entry) => {
      const button = document.createElement('button');
      button.className = 'history-item';
      button.type = 'button';
      button.textContent = entry.label;
      button.title = `Открыть: ${entry.label}`;
      button.addEventListener('click', () => {
        if (kind === 'video') {
          videoInput.value = entry.value;
          videoForm.requestSubmit();
        } else if (entry.type === 'url') {
          document.querySelector('#spotify-url').value = entry.value;
          loadPlaylist();
        } else {
          playlistInput.value = entry.value;
          spotifyForm.requestSubmit();
        }
      });
      container.append(button);
    });
  });
}

videoForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const query = videoInput.value.trim();
  if (!query) {
    videoStatus.textContent = 'Введи, что хочешь найти.';
    videoInput.focus();
    return;
  }
  videoStatus.textContent = `Ищем «${query}» на YouTube…`;
  saveHistory('video', { label: query, value: query });
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
  saveHistory('spotify', { label: query, value: query, type: 'query' });
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
  saveHistory('spotify', { label: raw.replace(/^https?:\/\//, '').slice(0, 42), value: raw, type: 'url' });
  spotifyStatus.textContent = 'Плеер загружен. Доступность воспроизведения зависит от Spotify и настроек аккаунта.';
}

document.querySelector('#load-playlist').addEventListener('click', loadPlaylist);
document.querySelector('#spotify-url').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') loadPlaylist();
});

document.querySelector('#clear-history').addEventListener('click', () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
  document.querySelector('#clear-history').textContent = 'История очищена';
  window.setTimeout(() => { document.querySelector('#clear-history').textContent = 'Очистить историю'; }, 1800);
});

renderHistory();
