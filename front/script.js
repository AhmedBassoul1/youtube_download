const audioCheckbox = document.getElementById('audioOnly');
const qualityContainer = document.getElementById('qualityContainer');
const urlInput = document.getElementById('urlInput');
let currentPlaylist = null;
let lastCheckedUrl = '';

audioCheckbox.addEventListener('change', function() {
    if (this.checked) {
        qualityContainer.classList.add('hidden');
    } else {
        qualityContainer.classList.remove('hidden');
    }
});

// Sync radio buttons -> hidden select
const qualityRadios = document.querySelectorAll('input[name="quality"]');
const qualitySelect = document.getElementById('qualitySelect');
qualityRadios.forEach(radio => {
    radio.addEventListener('change', function() {
        if (this.checked) qualitySelect.value = this.value;
    });
});

// --- Playlist detection ---
// We trigger only on paste and blur (not on every keystroke), so the panel
// doesn't flicker while the user is still typing.
urlInput.addEventListener('paste', () => {
    // After paste, the value is updated on next tick.
    setTimeout(() => maybeCheckPlaylist(urlInput.value.trim()), 50);
});
urlInput.addEventListener('blur', () => {
    maybeCheckPlaylist(urlInput.value.trim());
});

function urlHasPlaylistParam(url) {
    return /[?&]list=/.test(url);
}

function maybeCheckPlaylist(url) {
    if (!url) {
        hidePlaylist();
        lastCheckedUrl = '';
        return;
    }
    if (url === lastCheckedUrl) return;   // already checked this exact URL
    lastCheckedUrl = url;

    if (!urlHasPlaylistParam(url)) {
        // Single video — no panel needed
        hidePlaylist();
        return;
    }
    checkPlaylist(url);
}

async function checkPlaylist(url) {
    const container = document.getElementById('playlistContainer');
    container.classList.remove('hidden');
    document.getElementById('playlistTitle').textContent = 'Loading playlist...';
    document.getElementById('playlistList').innerHTML = '';
    document.getElementById('playlistCount').textContent = '';

    try {
        const res = await fetch(`http://127.0.0.1:8000/playlist-info?url=${encodeURIComponent(url)}`);
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            showPlaylistError('Could not load playlist: ' + (err.detail || res.status));
            return;
        }
        const data = await res.json();
        if (data.is_playlist && data.videos && data.videos.length > 0) {
            renderPlaylist(data);
        } else {
            // Backend says it's not a playlist (or empty). Hide and tell the user once.
            showPlaylistError('No playlist videos found at this URL.');
            setTimeout(hidePlaylist, 2000);
        }
    } catch (e) {
        showPlaylistError('Network error: ' + e.message);
    }
}

function showPlaylistError(msg) {
    document.getElementById('playlistTitle').textContent = msg;
    document.getElementById('playlistList').innerHTML = '';
    document.getElementById('playlistCount').textContent = '';
}

function renderPlaylist(data) {
    currentPlaylist = data;
    const title = document.getElementById('playlistTitle');
    const list = document.getElementById('playlistList');

    title.textContent = data.playlist_title || 'Playlist';
    list.innerHTML = '';

    data.videos.forEach(video => {
        const item = document.createElement('div');
        item.className = 'playlist-item';
        item.innerHTML = `
            <label class="playlist-label">
                <input type="checkbox" class="playlist-checkbox" value="${video.index}" checked>
                <span class="playlist-checkmark"></span>
                <span class="playlist-video-title"></span>
            </label>
        `;
        // Use textContent (not innerHTML) for video titles to avoid XSS
        item.querySelector('.playlist-video-title').textContent = video.title;
        list.appendChild(item);
    });

    list.querySelectorAll('.playlist-checkbox').forEach(cb => {
        cb.addEventListener('change', updatePlaylistCount);
    });
    updatePlaylistCount();
}

function hidePlaylist() {
    document.getElementById('playlistContainer').classList.add('hidden');
    currentPlaylist = null;
}

function selectAllVideos(checked) {
    document.querySelectorAll('.playlist-checkbox').forEach(cb => cb.checked = checked);
    updatePlaylistCount();
}

function updatePlaylistCount() {
    const checked = document.querySelectorAll('.playlist-checkbox:checked').length;
    const total = document.querySelectorAll('.playlist-checkbox').length;
    document.getElementById('playlistCount').textContent = `${checked} of ${total} videos selected`;
}

function getSelectedIndices() {
    if (!currentPlaylist) return null;
    const checked = document.querySelectorAll('.playlist-checkbox:checked');
    if (checked.length === 0) return [];
    return Array.from(checked).map(cb => parseInt(cb.value, 10));
}

// --- Folder picker ---
async function pickFolder() {
    const btn = document.getElementById('browseBtn');
    const input = document.getElementById('outputDir');
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span>Picking…</span>';
    try {
        const res = await fetch('http://127.0.0.1:8000/pick-folder');
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || 'Failed to open folder picker');
        }
        const data = await res.json();
        if (data.path) {
            input.value = data.path;
        }
    } catch (e) {
        alert('Could not open folder picker: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = original;
    }
}

// --- Download ---
async function startDownload() {
    const url = document.getElementById('urlInput').value;
    const isAudio = audioCheckbox.checked;
    const quality = document.getElementById('qualitySelect').value;
    const outputDir = document.getElementById('outputDir').value.trim();
    const statusDiv = document.getElementById('status');
    const selectedIndices = getSelectedIndices();

    if (!url) { alert("Please enter a URL"); return; }
    if (selectedIndices !== null && selectedIndices.length === 0) {
        alert("Please select at least one video from the playlist.");
        return;
    }
    statusDiv.innerText = "Starting download...";

    try {
        const response = await fetch('http://127.0.0.1:8000/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                url: url,
                is_audio: isAudio,
                quality: quality,
                output_dir: outputDir || null,
                selected_indices: selectedIndices
            })
        });
        const data = await response.json();
        const jobId = data.job_id;

        const interval = setInterval(async () => {
            const res = await fetch(`http://127.0.0.1:8000/status/${jobId}`);
            const statusData = await res.json();
            let msg = `Status: ${statusData.status}`;
            if (statusData.status === 'failed' && statusData.error) {
                msg += ` — ${statusData.error}`;
            } else if (statusData.status === 'completed' && statusData.folder) {
                msg += ` — saved to ${statusData.folder}`;
            }
            statusDiv.innerText = msg;
            if (statusData.status === 'completed' || statusData.status === 'failed') {
                clearInterval(interval);
            }
        }, 2000);
    } catch (e) { statusDiv.innerText = "Error: Could not connect to server."; }
}