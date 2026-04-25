const audioCheckbox = document.getElementById('audioOnly');
const qualityContainer = document.getElementById('qualityContainer');

audioCheckbox.addEventListener('change', function() {
    if (this.checked) {
        qualityContainer.classList.add('hidden');
    } else {
        qualityContainer.classList.remove('hidden');
    }
});

// Sync radio buttons -> hidden select (so original logic stays unchanged)
const qualityRadios = document.querySelectorAll('input[name="quality"]');
const qualitySelect = document.getElementById('qualitySelect');
qualityRadios.forEach(radio => {
    radio.addEventListener('change', function() {
        if (this.checked) qualitySelect.value = this.value;
    });
});

async function startDownload() {
    const url = document.getElementById('urlInput').value;
    const isAudio = audioCheckbox.checked;
    const quality = document.getElementById('qualitySelect').value;
    const statusDiv = document.getElementById('status');

    if (!url) { alert("Please enter a URL"); return; }
    statusDiv.innerText = "Starting download...";

    try {
        const response = await fetch('http://127.0.0.1:8000/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, is_audio: isAudio, quality: quality })
        });
        const data = await response.json();
        const jobId = data.job_id;

        const interval = setInterval(async () => {
            const res = await fetch(`http://127.0.0.1:8000/status/${jobId}`);
            const statusData = await res.json();
            statusDiv.innerText = `Status: ${statusData.status}`;
            if (statusData.status === 'completed' || statusData.status === 'failed') {
                clearInterval(interval);
            }
        }, 2000);
    } catch (e) { statusDiv.innerText = "Error: Could not connect to server."; }
}
