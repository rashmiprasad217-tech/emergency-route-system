// Emergency Route System - Main Utility Scripts

document.addEventListener("DOMContentLoaded", function() {
    // Automatically fade out standard Bootstrap flash alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

/**
 * Dynamically displays a Bootstrap alert in the dashboard or active page container
 * @param {string} message - The text body of the alert
 * @param {string} type - Bootstrap context class (success, danger, warning, info)
 */
function showAlert(message, type) {
    var container = document.getElementById('custom-alert-container');
    if (!container) return;

    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show border-0 shadow-sm" role="alert">
            <i class="fa-solid ${type === 'danger' ? 'fa-triangle-exclamation' : (type === 'success' ? 'fa-circle-check' : 'fa-circle-info')} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    container.innerHTML = alertHtml;
    
    // Auto-remove custom alerts after 6 seconds
    setTimeout(function() {
        var alertEl = container.querySelector('.alert');
        if (alertEl) {
            var bsAlert = new bootstrap.Alert(alertEl);
            bsAlert.close();
        }
    }, 6000);
}
