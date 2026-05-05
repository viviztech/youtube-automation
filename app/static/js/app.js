function showToast(message, success = true) {
    const container = document.getElementById('toast-container');
    if (!container) return;
    const toast = document.createElement('div');
    toast.className = `toast px-4 py-3 rounded-lg text-sm font-medium shadow-lg max-w-xs ${
        success ? 'bg-green-800 border border-green-600 text-green-100' : 'bg-red-800 border border-red-600 text-red-100'
    }`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
}

// Flash messages auto-dismiss
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-flash]').forEach(el => {
        setTimeout(() => el.remove(), 4000);
    });
});
