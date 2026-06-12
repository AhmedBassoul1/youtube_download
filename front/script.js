const API = 'http://127.0.0.1:8000';

const audioCheckbox = document.getElementById('audioOnly');
const qualityContainer = document.getElementById('qualityContainer');
const urlInput = document.getElementById('urlInput');
const statusDiv = document.getElementById('status');

let currentInfo = null;       // last /info payload
let lastCheckedUrl = '';
const activeJobs = new Map(); // job_id -> {el, timer}

// ---------- helpers ----------

async function api(path, opts = {}) {
    const res = await fetch(API + path, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

function getQuality() {
    const r = document.querySelector('input[name="quality"]:checked');
    return r ? r.value : '1080p';
}

function setQuality(value) {
    const r = document.querySelector(`input[name="quality"][value="${value}"]`);
    if (r) r.checked = true;
}

audioCheckbox.addEventListener('change', function () {
    qualityContainer.classList.toggle('hidden', this.checked);
    document.getElementById('containerOpt').classList.toggle('hidden', this.checked);
    document.getElementById('audioOpt').classList.toggle('hidden', !this.checked);
});

// ---------- settings bootstrap (remember last folder) ----------

(async function init() {
    try {
        const s = await api('/settings');
        if (s.last_folder) document.getElementById('outputDir').value = s.last_folder;
        if (s.filename_template) document.getElementById('filenameTemplate').placeholder = s.filename_template;
        if (s.duplicate_policy) document.getElementById('duplicatePolicy').value = s.duplicate_policy;
    } catch (_) { /* server not up yet */ }
})();

// ---------- URL info: preview / playlist ----------

urlInput.addEventListener('paste', () => setTimeout(() => maybeCheckUrl(urlInput.value.trim()), 50));
urlInput.addEventListener('blur', () => maybeCheckUrl(urlInput.value.trim()));

function maybeCheckUrl(url) {
    if (!url) { hidePlaylist(); hidePreview(); lastCheckedUrl = ''; return; }
    if (url === lastCheckedUrl) return;
    lastCheckedUrl = url;
    fetchInfo(url);
}

async function fetchInfo(url) {
    hidePreview();
    const container = document.getElementById('playlistContainer');
    container.classList.remove('hidden');
    document.getElementById('playlistTitle').textContent = 'Loading info...';
    document.getElementById('playlistList').innerHTML = '';
    document.getElementById('playlistCount').textContent = '';

    try {
        const data = await api(`/info?url=${encodeURIComponent(url)}`);
        currentInfo = data;
        applyChannelProfile(data.channel_profile);
        if (data.is_playlist && data.videos.length > 0) {
            renderPlaylist(data);
        } else {
            hidePlaylist();
            renderPreview(data);
        }
    } catch (e) {
        showPlaylistError('Could not load info: ' + e.message);
        setTimeout(hidePlaylist, 2500);
    }
}

function applyChannelProfile(profile) {
    const badge = document.getElementById('profileBadge');
    if (!profile) { badge.classList.add('hidden'); return; }
    audioCheckbox.checked = !!profile.is_audio;
    audioCheckbox.dispatchEvent(new Event('change'));
    if (profile.quality) setQuality(profile.quality);
    if (profile.video_container) document.getElementById('videoContainer').value = profile.video_container;
    if (profile.audio_format) document.getElementById('audioFormat').value = profile.audio_format;
    badge.classList.remove('hidden');
}

// ---------- single-video preview ----------

function renderPreview(data) {
    if (!data.title) return;
    document.getElementById('previewThumb').src = data.thumbnail || '';
    document.getElementById('previewTitle').textContent = data.title;
    document.getElementById('previewChannel').textContent = data.channel || 'Unknown channel';
    document.getElementById('previewDuration').textContent = data.duration || '—';
    document.getElementById('previewContainer').classList.remove('hidden');
}

function hidePreview() {
    document.getElementById('previewContainer').classList.add('hidden');
    document.getElementById('profileBadge').classList.add('hidden');
}

// ---------- playlist panel (thumbnails + durations) ----------

function showPlaylistError(msg) {
    document.getElementById('playlistTitle').textContent = msg;
    document.getElementById('playlistList').innerHTML = '';
    document.getElementById('playlistCount').textContent = '';
}

function renderPlaylist(data) {
    document.getElementById('playlistTitle').textContent = data.title || 'Playlist';
    const list = document.getElementById('playlistList');
    list.innerHTML = '';

    data.videos.forEach(video => {
        const item = document.createElement('div');
        item.className = 'playlist-item';
        item.innerHTML = `
            <label class="playlist-label">
                <input type="checkbox" class="playlist-checkbox" checked>
                <span class="playlist-checkmark"></span>
                <img class="playlist-thumb" loading="lazy" alt="">
                <span class="playlist-video-text">
                    <span class="playlist-video-title"></span>
                    <span class="playlist-video-duration"></span>
                </span>
            </label>`;
        item.querySelector('.playlist-checkbox').value = video.index;
        item.querySelector('.playlist-thumb').src = video.thumbnail || '';
        item.querySelector('.playlist-video-title').textContent = video.title;       // textContent => no XSS
        item.querySelector('.playlist-video-duration').textContent = video.duration || '';
        list.appendChild(item);
    });

    list.querySelectorAll('.playlist-checkbox').forEach(cb => cb.addEventListener('change', updatePlaylistCount));
    updatePlaylistCount();
}

function hidePlaylist() {
    document.getElementById('playlistContainer').classList.add('hidden');
    document.getElementById('rangeInput').value = '';
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
    if (!currentInfo || !currentInfo.is_playlist) return null;
    return Array.from(document.querySelectorAll('.playlist-checkbox:checked'))
        .map(cb => parseInt(cb.value, 10));
}

// ---------- folder picker ----------

async function pickFolder() {
    const btn = document.getElementById('browseBtn');
    const input = document.getElementById('outputDir');
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span>Picking…</span>';
    try {
        const data = await api('/pick-folder');
        if (data.path) input.value = data.path;
    } catch (e) {
        alert('Could not open folder picker: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = original;
    }
}

// ---------- download ----------

function buildRequestBody(url) {
    const range = document.getElementById('rangeInput').value.trim();
    const selected = getSelectedIndices();
    const subs = document.getElementById('subtitlesLangs').value.trim();
    return {
        url,
        is_audio: audioCheckbox.checked,
        quality: getQuality(),
        output_dir: document.getElementById('outputDir').value.trim() || null,
        playlist_items: range || null,
        selected_indices: range ? null : selected,
        video_container: document.getElementById('videoContainer').value,
        audio_format: document.getElementById('audioFormat').value,
        subtitles_langs: subs ? subs.split(',').map(s => s.trim()).filter(Boolean) : null,
        filename_template: document.getElementById('filenameTemplate').value.trim() || null,
        duplicate_policy: document.getElementById('duplicatePolicy').value,
        save_channel_profile: document.getElementById('saveProfile').checked,
    };
}

async function startDownload() {
    const url = urlInput.value.trim();
    if (!url) { alert('Please enter a URL'); return; }
    const range = document.getElementById('rangeInput').value.trim();
    const selected = getSelectedIndices();
    if (!range && selected !== null && selected.length === 0) {
        alert('Please select at least one video from the playlist.');
        return;
    }
    statusDiv.innerText = '';
    try {
        const data = await api('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(buildRequestBody(url)),
        });
        trackJob(data.job_id, currentInfo?.title || url);
    } catch (e) {
        statusDiv.innerText = 'Error: ' + e.message;
    }
}

// ---------- batch mode (.txt of URLs) ----------

async function loadBatchFile(input) {
    const file = input.files[0];
    if (!file) return;
    const text = await file.text();
    const urls = text.split(/\r?\n/).map(l => l.trim()).filter(l => l && !l.startsWith('#'));
    input.value = '';
    if (urls.length === 0) { alert('No URLs found in file.'); return; }
    if (!confirm(`Start ${urls.length} downloads with the current settings?`)) return;
    try {
        const body = buildRequestBody('');
        const data = await api('/download-batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                urls,
                is_audio: body.is_audio,
                quality: body.quality,
                output_dir: body.output_dir,
                video_container: body.video_container,
                audio_format: body.audio_format,
                duplicate_policy: body.duplicate_policy,
            }),
        });
        data.jobs.forEach(j => trackJob(j.job_id, j.url));
        if (data.errors.length) {
            statusDiv.innerText = data.errors.map(e => `${e.url}: ${e.error}`).join('\n');
        }
    } catch (e) {
        statusDiv.innerText = 'Batch error: ' + e.message;
    }
}

// ---------- job cards: progress bar + cancel + open folder ----------

function trackJob(jobId, label) {
    const container = document.getElementById('jobsContainer');
    const card = document.createElement('div');
    card.className = 'job-card';
    card.innerHTML = `
        <div class="job-head">
            <span class="job-title"></span>
            <span class="job-state">queued</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:0%"></div></div>
        <div class="job-meta"></div>
        <div class="job-actions">
            <button type="button" class="action-btn job-cancel">Cancel</button>
            <button type="button" class="action-btn job-open hidden">Open folder</button>
        </div>`;
    card.querySelector('.job-title').textContent = label;
    container.prepend(card);

    const cancelBtn = card.querySelector('.job-cancel');
    cancelBtn.onclick = async () => {
        cancelBtn.disabled = true;
        try { await api(`/cancel/${jobId}`, { method: 'POST' }); } catch (_) {}
    };

    const timer = setInterval(() => pollJob(jobId), 1500);
    activeJobs.set(jobId, { el: card, timer });
    pollJob(jobId);
}

async function pollJob(jobId) {
    const job = activeJobs.get(jobId);
    if (!job) return;
    let data;
    try { data = await api(`/status/${jobId}`); }
    catch (_) { return; }

    const { el } = job;
    const p = data.progress || {};
    el.querySelector('.job-state').textContent = data.status;
    el.querySelector('.progress-fill').style.width = `${p.percent || 0}%`;

    const parts = [];
    if (p.total_items > 1) parts.push(`item ${p.item}/${p.total_items}`);
    if (p.percent) parts.push(`${p.percent}%`);
    if (p.speed) parts.push(p.speed);
    if (p.eta) parts.push(`ETA ${p.eta}`);
    if (p.filename) parts.push(p.filename);
    el.querySelector('.job-meta').textContent = parts.join(' · ');

    if (['completed', 'failed', 'cancelled'].includes(data.status)) {
        clearInterval(job.timer);
        activeJobs.delete(jobId);
        el.querySelector('.job-cancel').classList.add('hidden');
        el.classList.add(`job-${data.status}`);
        if (data.status === 'failed' && data.error) {
            el.querySelector('.job-meta').textContent = data.error;
        }
        if (data.status === 'completed' && data.folder) {
            el.querySelector('.progress-fill').style.width = '100%';
            const openBtn = el.querySelector('.job-open');
            openBtn.classList.remove('hidden');
            openBtn.onclick = () => openFolder(data.folder);
        }
        refreshHistory();
    }
}

async function openFolder(path) {
    try {
        await api('/open-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path }),
        });
    } catch (e) { alert('Could not open folder: ' + e.message); }
}

// ---------- history ----------

async function toggleHistory() {
    const panel = document.getElementById('historyContainer');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) refreshHistory();
}

async function refreshHistory() {
    const panel = document.getElementById('historyContainer');
    if (panel.classList.contains('hidden')) return;
    const list = document.getElementById('historyList');
    try {
        const data = await api('/history?limit=50');
        list.innerHTML = '';
        if (data.history.length === 0) {
            list.textContent = 'No downloads yet.';
            return;
        }
        data.history.forEach(h => {
            const row = document.createElement('div');
            row.className = 'history-item';
            row.innerHTML = `
                <span class="history-title"></span>
                <span class="history-status"></span>
                <button type="button" class="action-btn history-open hidden">Open</button>`;
            row.querySelector('.history-title').textContent = h.title || h.url || '';
            row.querySelector('.history-status').textContent = h.status || '';
            if (h.folder) {
                const btn = row.querySelector('.history-open');
                btn.classList.remove('hidden');
                btn.onclick = () => openFolder(h.folder);
            }
            list.appendChild(row);
        });
    } catch (e) {
        list.textContent = 'Could not load history: ' + e.message;
    }
}

async function clearHistory() {
    if (!confirm('Clear the whole download history?')) return;
    try { await api('/history', { method: 'DELETE' }); refreshHistory(); }
    catch (e) { alert(e.message); }
}

// ---------- yt-dlp update ----------

async function updateYtdlp() {
    const btn = document.getElementById('updateBtn');
    btn.disabled = true;
    btn.textContent = 'Updating…';
    try {
        const data = await api('/update-ytdlp', { method: 'POST' });
        btn.textContent = `yt-dlp ${data.version}`;
    } catch (e) {
        btn.textContent = 'Update failed';
        alert('Update failed: ' + e.message);
    } finally {
        setTimeout(() => { btn.disabled = false; btn.textContent = 'Update yt-dlp'; }, 4000);
    }
}
