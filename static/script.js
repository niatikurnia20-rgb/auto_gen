async function startGeneration() {
    const topicInput = document.getElementById('topic');
    const topic = topicInput.value;
    const btn = document.getElementById('generate-btn');

    if (!topic) {
        topicInput.style.borderColor = '#ef4444';
        setTimeout(() => topicInput.style.borderColor = 'rgba(255,255,255,0.1)', 2000);
        return;
    }

    // UI State: Processing
    btn.disabled = true;
    btn.innerHTML = `<span>Processing...</span> <div class="loader-ring" style="width:15px;height:15px;"></div>`;
    
    document.getElementById('status-box').classList.remove('hidden');
    document.getElementById('result-box').classList.add('hidden');
    document.getElementById('logs').innerHTML = "";
    
    // Smooth scroll to status
    document.getElementById('status-box').scrollIntoView({ behavior: 'smooth' });

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ topic: topic })
        });
        
        if (!response.ok) throw new Error("API Error");
        
        const data = await response.json();
        checkStatus(data.task_id);

    } catch (e) {
        alert("Failed to start generation.");
        resetUI();
    }
}

async function checkStatus(taskId) {
    const interval = setInterval(async () => {
        try {
            const res = await fetch(`/status/${taskId}`);
            const data = await res.json();

            document.getElementById('status-text').innerText = data.status;
            
            // Smart Log Update
            const logsDiv = document.getElementById('logs');
            // Check if we have new logs to append/animate
            const currentLogCount = logsDiv.children.length;
            if (data.logs.length > currentLogCount) {
                const newLogs = data.logs.slice(currentLogCount);
                newLogs.forEach(log => {
                    const p = document.createElement('p');
                    p.innerText = `> ${log}`;
                    logsDiv.appendChild(p);
                });
                logsDiv.scrollTop = logsDiv.scrollHeight; // Auto-scroll to bottom
            }

            if (data.status === 'Completed') {
                clearInterval(interval);
                showResult(data.video_url);
            } else if (data.status === 'Failed') {
                clearInterval(interval);
                alert("Generation Failed!");
                resetUI();
            }
        } catch (e) {
            clearInterval(interval);
            console.error("Polling error", e);
        }
    }, 2000);
}

function showResult(url) {
    resetUI();
    document.getElementById('status-box').classList.add('hidden');
    const resultBox = document.getElementById('result-box');
    resultBox.classList.remove('hidden');
    
    const video = document.getElementById('video-player');
    video.src = url;
    
    const link = document.getElementById('download-link');
    link.href = url;
    
    // Smooth scroll to result
    resultBox.scrollIntoView({ behavior: 'smooth' });
}

function resetUI() {
    const btn = document.getElementById('generate-btn');
    btn.disabled = false;
    btn.innerHTML = `<span>Generate Video</span> <i class="fa-solid fa-bolt"></i>`;
}
