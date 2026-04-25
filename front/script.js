async function startDownload() {
    const url = document.getElementById('urlInput').value;
    const isAudio = document.getElementById('audioOnly').checked;
    const statusDiv = document.getElementById('status');

    if (!url) return alert("Please enter a URL");

    statusDiv.innerText = "Starting download...";

    // 1. Trigger Download
    const response = await fetch('http://127.0.0.1:8000/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url, is_audio: isAudio })
    });

    const data = await response.json();
    const jobId = data.job_id;

    // 2. Poll Status
    const interval = setInterval(async () => {
        const res = await fetch(`http://127.0.0.1:8000/status/${jobId}`);
        const statusData = await res.json();
        
        statusDiv.innerText = `Status: ${statusData.status}`;

        if (statusData.status === 'completed' || statusData.status === 'failed') {
            clearInterval(interval);
        }
    }, 2000); // Check every 2 seconds
}