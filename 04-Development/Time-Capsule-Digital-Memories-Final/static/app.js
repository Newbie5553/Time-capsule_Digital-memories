// Show the selected filenames and catch oversized selections before uploading.
// Python performs its own validation, even when JavaScript is disabled.
const uploadInput = document.getElementById('files');
const filenameList = document.getElementById('file-list');

if (uploadInput && filenameList) {
    uploadInput.addEventListener('change', () => {
        const selectedFiles = Array.from(uploadInput.files);
        const existingCount = Number(uploadInput.dataset.existing || 0);
        const totalBytes = selectedFiles.reduce((sum, file) => sum + file.size, 0);
        let error = '';

        if (existingCount + selectedFiles.length > 10) {
            error = 'Each capsule can have up to 10 attachments in total.';
        } else if (totalBytes > 49 * 1024 * 1024) {
            // Leave space for the message and multipart form overhead.
            error = 'Choose files smaller than 49 MB in total for this save.';
        }

        uploadInput.setCustomValidity(error);
        filenameList.textContent = error || (
            selectedFiles.length
                ? selectedFiles.map(file => file.name).join(' · ')
                : 'JPG, PNG, GIF, WebP, MP4, WebM'
        );
    });
}

// Deletion uses a server-rendered confirmation page, so it also works without JS.

// Convert the browser's local date/time to a timezone-explicit UTC value.
const sealForm = document.getElementById('seal-form');
if (sealForm) {
    const input = document.getElementById('opening-time');
    const hidden = document.getElementById('unlock-at');
    const localValue = date => new Date(date.getTime() - date.getTimezoneOffset() * 60000)
        .toISOString().slice(0, 16);
    input.min = localValue(new Date(Date.now() + 60000));
    document.getElementById('timezone-label').textContent =
        `Your timezone: ${Intl.DateTimeFormat().resolvedOptions().timeZone}. The time is saved in UTC.`;
    document.getElementById('seal-submit').disabled = false;
    document.querySelectorAll('[data-minutes]').forEach(button => {
        button.addEventListener('click', () => {
            input.value = localValue(new Date(Date.now() + Number(button.dataset.minutes) * 60000));
        });
    });
    sealForm.addEventListener('submit', event => {
        const selected = new Date(input.value);
        if (!Number.isFinite(selected.getTime())) {
            event.preventDefault();
            input.reportValidity();
            return;
        }
        hidden.value = selected.toISOString();
    });
}

document.querySelectorAll('[data-local-time]').forEach(element => {
    element.textContent = new Date(Number(element.dataset.localTime) * 1000)
        .toLocaleString(undefined, {dateStyle: 'long', timeStyle: 'short'});
});

// Count down using server time and a monotonic browser timer, not the device
// wall clock. Only a successful server status check can trigger opening.
document.querySelectorAll('[data-status-url]').forEach(element => {
    let remainingAtSync = null;
    let syncedAt = 0;
    let finished = false;
    let busy = false;
    const message = element.parentElement.querySelector('[data-countdown-message]');

    async function synchronize() {
        if (busy || finished) return;
        busy = true;
        try {
            const response = await fetch(element.dataset.statusUrl, {cache: 'no-store'});
            if (!response.ok || !response.headers.get('content-type')?.includes('application/json')) {
                throw new Error('Status unavailable');
            }
            const status = await response.json();
            if (status.state === 'ready') {
                finished = true;
                if (element.dataset.reload === 'true') {
                    location.reload();
                } else {
                    element.textContent = 'Ready to open →';
                    const badge = element.closest('.capsule-card')?.querySelector('.badge');
                    if (badge) {
                        badge.textContent = 'Ready to open';
                        badge.className = 'badge ready';
                    }
                }
                return;
            }
            remainingAtSync = Math.max(0, status.unlock_at - status.server_now);
            syncedAt = performance.now();
            if (message) message.textContent = 'Your memories stay sealed until this countdown ends.';
            draw();
        } catch (error) {
            if (message) message.textContent = 'Unable to check the server. Keep the app running; we’ll retry.';
        } finally {
            busy = false;
        }
    }

    function draw() {
        if (finished || remainingAtSync === null) return;
        const remaining = Math.max(0, Math.ceil(remainingAtSync - (performance.now() - syncedAt) / 1000));
        const values = {
            days: Math.floor(remaining / 86400),
            hours: Math.floor(remaining % 86400 / 3600),
            minutes: Math.floor(remaining % 3600 / 60),
            seconds: remaining % 60,
        };
        if (element.classList.contains('countdown-grid')) {
            Object.entries(values).forEach(([unit, value]) => {
                element.querySelector(`[data-unit="${unit}"]`).textContent = String(value).padStart(2, '0');
            });
        } else {
            element.textContent = `${values.days}d ${values.hours}h ${values.minutes}m to go`;
        }
        if (remaining === 0 && message) message.textContent = 'Checking whether your memory is ready…';
    }

    synchronize();
    setInterval(() => {
        draw();
        if (!finished && remainingAtSync !== null && performance.now() - syncedAt >= remainingAtSync * 1000) {
            synchronize();
        }
    }, 1000);
    setInterval(synchronize, 15000);
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) synchronize();
    });
});
