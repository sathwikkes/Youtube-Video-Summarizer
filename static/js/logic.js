function summarizeVideo() {
    const videoUrl = document.getElementById('videoUrl').value;

    // Send the videoUrl to the server for processing
    fetch('/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ videoUrl }),
    })
    .then(response => response.json())
    .then(data => {
        const summaryResult = document.getElementById('summaryResult');
        summaryResult.innerHTML = data.summary;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
