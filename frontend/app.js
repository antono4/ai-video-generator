/**
 * AI Video Creator Agent - Frontend Application
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
const state = {
    jobId: null,
    script: null,
    videoUrl: null,
    isProcessing: false,
    pollingInterval: null
};

// DOM Elements
const elements = {
    form: document.getElementById('videoForm'),
    promptInput: document.getElementById('promptInput'),
    duration: document.getElementById('duration'),
    style: document.getElementById('style'),
    submitBtn: document.getElementById('submitBtn'),
    progressSection: document.getElementById('progressSection'),
    scriptSection: document.getElementById('scriptSection'),
    videoSection: document.getElementById('videoSection'),
    progressBar: document.getElementById('progressBar'),
    progressText: document.getElementById('progressText'),
    scriptTitle: document.getElementById('scriptTitle'),
    scenesList: document.getElementById('scenesList'),
    videoPlayer: document.getElementById('videoPlayer'),
    videoOverlay: document.getElementById('videoOverlay'),
    downloadBtn: document.getElementById('downloadBtn'),
    shareBtn: document.getElementById('shareBtn'),
    newVideoBtn: document.getElementById('newVideoBtn'),
    toastContainer: document.getElementById('toastContainer')
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    loadDemoScript();
});

// Event Listeners
function initEventListeners() {
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.videoOverlay.addEventListener('click', toggleVideoPlayback);
    elements.videoPlayer.addEventListener('click', toggleVideoPlayback);
    elements.videoPlayer.addEventListener('play', () => elements.videoOverlay.classList.add('hidden'));
    elements.videoPlayer.addEventListener('pause', () => elements.videoOverlay.classList.remove('hidden'));
    elements.downloadBtn.addEventListener('click', downloadVideo);
    elements.shareBtn.addEventListener('click', shareVideo);
    elements.newVideoBtn.addEventListener('click', resetForm);
}

// Form Handler
async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (state.isProcessing) return;
    
    const prompt = elements.promptInput.value.trim();
    if (!prompt) {
        showToast('Please enter a video topic or prompt', 'error');
        return;
    }
    
    const duration = parseInt(elements.duration.value);
    const style = elements.style.value;
    
    state.isProcessing = true;
    state.script = null;
    state.videoUrl = null;
    
    // Update UI
    elements.submitBtn.classList.add('loading');
    elements.submitBtn.disabled = true;
    
    // Show progress section
    showSection('progress');
    updateProgress('script', 'active', 'Initializing...');
    
    try {
        // Start video creation
        const response = await fetch(`${API_BASE_URL}/api/create-video`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                prompt,
                duration,
                style
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to start video generation');
        }
        
        const data = await response.json();
        state.jobId = data.job_id;
        state.script = data.script;
        
        // Poll for status updates
        startPolling();
        
        // Display script preview
        displayScript(data.script);
        
    } catch (error) {
        console.error('Error:', error);
        showToast(error.message || 'An error occurred. Please try again.', 'error');
        resetForm();
    }
}

// Polling for Status Updates
function startPolling() {
    if (state.pollingInterval) {
        clearInterval(state.pollingInterval);
    }
    
    let pollCount = 0;
    
    state.pollingInterval = setInterval(async () => {
        pollCount++;
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/status/${state.jobId}`);
            
            if (!response.ok) {
                throw new Error('Failed to get status');
            }
            
            const status = await response.json();
            updateUIFromStatus(status);
            
            if (status.status === 'completed') {
                clearInterval(state.pollingInterval);
                state.pollingInterval = null;
                state.isProcessing = false;
                elements.submitBtn.classList.remove('loading');
                elements.submitBtn.disabled = false;
                
                // Show video
                if (status.result && status.result.video_url) {
                    state.videoUrl = `${API_BASE_URL}${status.result.video_url}`;
                    displayVideo(state.videoUrl);
                }
                
                showToast('Video generated successfully!', 'success');
            } else if (status.status === 'error') {
                clearInterval(state.pollingInterval);
                state.pollingInterval = null;
                state.isProcessing = false;
                elements.submitBtn.classList.remove('loading');
                elements.submitBtn.disabled = false;
                showToast(status.message || 'Video generation failed', 'error');
            }
            
            // Timeout after 5 minutes
            if (pollCount > 300) {
                clearInterval(state.pollingInterval);
                state.pollingInterval = null;
                state.isProcessing = false;
                showToast('Video generation timed out', 'error');
            }
            
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 1000);
}

// Update UI from Status
function updateUIFromStatus(status) {
    const progress = status.progress || 0;
    elements.progressBar.style.width = `${progress}%`;
    elements.progressText.textContent = status.message || 'Processing...';
    
    // Update step states
    if (progress < 30) {
        updateProgress('script', 'active', status.message);
    } else if (progress < 60) {
        updateProgress('script', 'completed', 'Script generated');
        updateProgress('images', 'active', status.message);
    } else {
        updateProgress('script', 'completed', 'Script generated');
        updateProgress('images', 'completed', 'Images generated');
        updateProgress('video', 'active', status.message);
    }
}

// Update Progress Step
function updateProgress(step, status, message) {
    const stepEl = document.querySelector(`.progress-step[data-step="${step}"]`);
    if (!stepEl) return;
    
    stepEl.className = `progress-step ${status}`;
    const statusEl = stepEl.querySelector('.step-status');
    if (statusEl) {
        statusEl.textContent = message || '';
    }
    
    // Update connector
    const connector = stepEl.nextElementSibling;
    if (connector && connector.classList.contains('progress-connector')) {
        if (status === 'completed') {
            connector.classList.add('completed');
        }
    }
}

// Display Script
function displayScript(script) {
    elements.scriptTitle.textContent = script.title || 'Generated Script';
    elements.scenesList.innerHTML = '';
    
    script.scenes.forEach(scene => {
        const card = document.createElement('div');
        card.className = 'scene-card';
        card.innerHTML = `
            <div class="scene-header">
                <span class="scene-number">${scene.scene_number}</span>
                <span class="scene-duration">${scene.duration.toFixed(1)}s</span>
            </div>
            <p class="scene-description">${scene.description || ''}</p>
            <p class="scene-narration">${scene.narration || ''}</p>
        `;
        elements.scenesList.appendChild(card);
    });
    
    // Show script section after a short delay
    setTimeout(() => {
        showSection('script');
    }, 500);
}

// Display Video
function displayVideo(url) {
    elements.videoPlayer.src = url;
    elements.videoOverlay.classList.remove('hidden');
    
    setTimeout(() => {
        showSection('video');
    }, 500);
}

// Video Playback
function toggleVideoPlayback() {
    if (elements.videoPlayer.paused) {
        elements.videoPlayer.play();
    } else {
        elements.videoPlayer.pause();
    }
}

// Download Video
function downloadVideo() {
    if (!state.videoUrl) return;
    
    const a = document.createElement('a');
    a.href = state.videoUrl;
    a.download = `ai-video-${state.jobId || 'output'}.mp4`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    showToast('Download started', 'success');
}

// Share Video
function shareVideo() {
    if (!state.videoUrl) return;
    
    if (navigator.share) {
        navigator.share({
            title: 'AI Generated Video',
            text: 'Check out this video I created with AI!',
            url: state.videoUrl
        }).catch(console.error);
    } else {
        // Fallback: copy URL to clipboard
        navigator.clipboard.writeText(state.videoUrl).then(() => {
            showToast('Video URL copied to clipboard', 'success');
        }).catch(() => {
            showToast('Failed to copy URL', 'error');
        });
    }
}

// Reset Form
function resetForm() {
    state.jobId = null;
    state.script = null;
    state.videoUrl = null;
    state.isProcessing = false;
    
    if (state.pollingInterval) {
        clearInterval(state.pollingInterval);
        state.pollingInterval = null;
    }
    
    elements.form.reset();
    elements.submitBtn.classList.remove('loading');
    elements.submitBtn.disabled = false;
    elements.progressBar.style.width = '0%';
    elements.progressText.textContent = 'Initializing...';
    
    // Reset progress steps
    document.querySelectorAll('.progress-step').forEach(step => {
        step.className = 'progress-step waiting';
        const statusEl = step.querySelector('.step-status');
        if (statusEl) statusEl.textContent = 'Waiting...';
    });
    document.querySelectorAll('.progress-connector').forEach(conn => {
        conn.classList.remove('completed');
    });
    
    // Hide all sections except input
    elements.progressSection.style.display = 'none';
    elements.scriptSection.style.display = 'none';
    elements.videoSection.style.display = 'none';
    
    // Reset video
    elements.videoPlayer.pause();
    elements.videoPlayer.src = '';
    elements.videoOverlay.classList.remove('hidden');
}

// Show Section
function showSection(section) {
    elements.progressSection.style.display = section === 'progress' || section === 'script' || section === 'video' ? 'block' : 'none';
    elements.scriptSection.style.display = section === 'script' || section === 'video' ? 'block' : 'none';
    elements.videoSection.style.display = section === 'video' ? 'block' : 'none';
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' 
        ? '<svg viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M15 9L9 15M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';
    
    toast.innerHTML = `
        <span class="toast-icon">${icon}</span>
        <span class="toast-message">${message}</span>
    `;
    
    elements.toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Load Demo Script (for UI demonstration)
function loadDemoScript() {
    // This creates a demo experience when API is not available
    console.log('AI Video Creator initialized');
}

// Utility: Debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
