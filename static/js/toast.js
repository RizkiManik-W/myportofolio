let toastTimer;
let toastCloseTimer;

function showToast(title, message, type = "normal", duration = 3000) {
    const toast = document.getElementById("toast-component");
    if (!toast) return;

    document.getElementById("toast-title").textContent = String(title ?? "");
    document.getElementById("toast-message").textContent = String(message ?? "");

    toast.classList.remove("toast-normal", "toast-success", "toast-error");
    toast.classList.add(
        type === "success" || type === "error" ? `toast-${type}` : "toast-normal"
    );

    clearTimeout(toastTimer);
    clearTimeout(toastCloseTimer);

    if (!toast.matches(":popover-open")) {
        toast.showPopover();
        void toast.offsetHeight;
    }
    toast.classList.add("toast-show");

    toastTimer = setTimeout(() => {
        toast.classList.remove("toast-show");
        toastCloseTimer = setTimeout(() => {
            if (toast.matches(":popover-open")) toast.hidePopover();
        }, 250);
    }, duration);
}
