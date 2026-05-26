// ==========================================
// CONFIGURATION — UPDATE THIS WITH YOUR API URL
// ==========================================
const API_URL = 'YOUR_API_GATEWAY_URL'; // e.g., https://abc123.execute-api.us-east-1.amazonaws.com/prod

// ==========================================
// SHORTEN URL
// ==========================================
document.getElementById('shorten-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const urlInput = document.getElementById('url-input');
    const customCode = document.getElementById('custom-code').value.trim();
    const expireDays = document.getElementById('expire-days').value;
    const btn = document.getElementById('shorten-btn');
    const resultDiv = document.getElementById('result');
    const errorDiv = document.getElementById('error');

    // Reset UI
    resultDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');
    btn.textContent = 'Shortening...';
    btn.disabled = true;

    try {
        const payload = {
            url: urlInput.value.trim(),
            expire_days: parseInt(expireDays)
        };
        if (customCode) {
            payload.custom_code = customCode;
        }

        const response = await fetch(`${API_URL}/shorten`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to shorten URL');
        }

        // Show result
        document.getElementById('result-url').value = data.short_url;
        document.getElementById('result-original-url').textContent = data.original_url;
        document.getElementById('result-original-url').href = data.original_url;
        resultDiv.classList.remove('hidden');

        // Clear inputs
        urlInput.value = '';
        document.getElementById('custom-code').value = '';

    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('hidden');
    } finally {
        btn.textContent = 'Shorten';
        btn.disabled = false;
    }
});

// ==========================================
// COPY URL
// ==========================================
function copyUrl() {
    const urlInput = document.getElementById('result-url');
    const copyBtn = document.getElementById('copy-btn');

    navigator.clipboard.writeText(urlInput.value).then(() => {
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
    }).catch(() => {
        // Fallback for older browsers
        urlInput.select();
        document.execCommand('copy');
        copyBtn.textContent = 'Copied!';
        setTimeout(() => { copyBtn.textContent = 'Copy'; }, 2000);
    });
}

// ==========================================
// LOOK UP STATS
// ==========================================
document.getElementById('stats-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const code = document.getElementById('stats-code').value.trim();
    const statsResult = document.getElementById('stats-result');
    const statsError = document.getElementById('stats-error');

    statsResult.classList.add('hidden');
    statsError.classList.add('hidden');

    try {
        const response = await fetch(`${API_URL}/stats/${code}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Short URL not found');
        }

        document.getElementById('stat-clicks').textContent = data.click_count;
        document.getElementById('stat-created').textContent = formatDate(data.created_at);
        document.getElementById('stat-last-click').textContent = data.last_clicked === 'never' ? 'Never' : formatDate(data.last_clicked);
        document.getElementById('stat-original-url').textContent = truncateUrl(data.original_url);
        document.getElementById('stat-original-url').href = data.original_url;

        statsResult.classList.remove('hidden');

    } catch (err) {
        statsError.textContent = err.message;
        statsError.classList.remove('hidden');
    }
});

// ==========================================
// HELPERS
// ==========================================
function formatDate(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
        return isoString;
    }
}

function truncateUrl(url, maxLength = 50) {
    return url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
}
