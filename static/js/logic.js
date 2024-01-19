function summarizeVideo() {
    const videoUrl = document.getElementById('videoUrl').value;

    fetch('/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_url: videoUrl }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('videoTitle').innerHTML = data.title;
        document.getElementById('summaryResult').innerText = data.summary;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('summaryResult').innerText = 'An error occurred.';
    });
}
