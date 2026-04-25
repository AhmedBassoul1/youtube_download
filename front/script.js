async function startDownload() {
    // 1. Declare the variables FIRST
    const url = document.getElementById('urlInput').value;
    const isAudio = document.getElementById('audioOnly').checked;
    const quality = document.getElementById('qualitySelect').value;
    const statusDiv = document.getElementById('status'); // THIS LINE IS LIKELY MISSING

    if (!url) {
        alert("Please enter a URL");
        return;
    }

    statusDiv.innerText = "Starting download..."; // Now it knows what statusDiv is

    // 2. Perform the fetch
    const response = await fetch('http://127.0.0.1:8000/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            url: url, 
            is_audio: isAudio,
            quality: quality 
        })
    });

    const data = await response.json();
    const jobId = data.job_id;

    // 3. Poll Status
    const interval = setInterval(async () => {
        const res = await fetch(`http://127.0.0.1:8000/status/${jobId}`);
        const statusData = await res.json();
        
        statusDiv.innerText = `Status: ${statusData.status}`;

        if (statusData.status === 'completed' || statusData.status === 'failed') {
            clearInterval(interval);
        }
    }, 2000); 
}