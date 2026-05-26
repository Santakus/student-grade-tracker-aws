// ==========================================
// CONFIGURATION — UPDATE WITH YOUR API URL
// ==========================================
const API_URL = 'YOUR_API_GATEWAY_URL'; // e.g., https://abc123.execute-api.us-east-1.amazonaws.com/prod

// ==========================================
// FORM SUBMISSION
// ==========================================
document.getElementById('contact-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const btn = document.getElementById('submit-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    const successMsg = document.getElementById('success-msg');
    const errorMsg = document.getElementById('error-msg');

    // Reset feedback
    successMsg.classList.add('hidden');
    errorMsg.classList.add('hidden');

    // Show loading state
    btnText.classList.add('hidden');
    btnLoader.classList.remove('hidden');
    btn.disabled = true;

    const payload = {
        name: form.name.value.trim(),
        email: form.email.value.trim(),
        subject: form.subject.value.trim(),
        message: form.message.value.trim()
    };

    try {
        const response = await fetch(`${API_URL}/contact`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.details ? data.details.join(', ') : data.error || 'Submission failed');
        }

        // Show success
        form.classList.add('hidden');
        successMsg.classList.remove('hidden');

        // Reset form for potential resubmission
        setTimeout(() => {
            form.reset();
            form.classList.remove('hidden');
            successMsg.classList.add('hidden');
        }, 5000);

    } catch (err) {
        document.getElementById('error-detail').textContent = err.message;
        errorMsg.classList.remove('hidden');
    } finally {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
        btn.disabled = false;
    }
});
