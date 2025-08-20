// Stateless image upload utility functions
function showOverlay(el) {
    // If el is the file input, find the container by going up
    const container = el.closest('[x-data]').querySelector('[x-ref="container"]');
    if (container) {
        container.classList.add('bg-black', 'bg-opacity-20');
    }
}

function hideOverlay(el) {
    // If el is the file input, find the container by going up
    const container = el.closest('[x-data]').querySelector('[x-ref="container"]');
    if (container) {
        container.classList.remove('bg-black', 'bg-opacity-20');
    }
}

function handleMouseEnter(el, data) {
    if (!data.isDragging && !data.isUploading) {
        showOverlay(el);
        data.isHovering = true;
    }
}

function handleMouseLeave(el, data) {
    if (!data.isDragging && !data.isUploading) {
        hideOverlay(el);
        data.isHovering = false;
    }
}

function handleDragOver(el, data, event) {
    event.preventDefault();
    if (data.isUploading) return;

    if (data.isHovering) {
        data.isHovering = false;
    } else {
        showOverlay(el);
    }
    data.isDragging = true;
}

function handleDragEnd(el, data, event) {
    event.preventDefault();
    if (data.isUploading) return;

    hideOverlay(el);
    data.isDragging = false;
}

function handleFileSelected(el, data) {
    const fileInput = el.closest('[x-data]').querySelector('[x-ref="fileInput"]');
    if (fileInput && fileInput.files.length > 0) {
        data.fileName = fileInput.files[0].name;
    }
}

function handleFileDrop(el, data, event) {
    event.preventDefault();
    if (data.isUploading) return;

    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const fileInput = el.closest('[x-data]').querySelector('[x-ref="fileInput"]');
        if (fileInput) {
            // Set the files on the input and trigger change event
            fileInput.files = files;
            data.fileName = files[0].name;
            
            // Trigger the change event to activate HTMX
            fileInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    hideOverlay(el);
    data.isDragging = false;
}
