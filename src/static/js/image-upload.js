// Stateless image upload utility functions
function showOverlay(el) {
    // If el is the file input, find the container by going up
    const container = el.closest('[x-data]').querySelector('[x-ref="container"]');
    if (container) {
        container.classList.add('bg-black', 'bg-opacity-20');
    }
}

function showRedOverlay(el) {
    // If el is the file input, find the container by going up
    const container = el.closest('[x-data]').querySelector('[x-ref="container"]');
    if (container) {
        container.classList.add('bg-red-500', 'bg-opacity-30');
        
        // Show invalid file indicator
        const indicator = container.querySelector('.invalid-file-indicator');
        if (indicator) {
            indicator.classList.remove('hidden');
        }
    }
}

function hideOverlay(el) {
    // If el is the file input, find the container by going up
    const container = el.closest('[x-data]').querySelector('[x-ref="container"]');
    if (container) {
        container.classList.remove('bg-black', 'bg-opacity-20', 'bg-red-500', 'bg-opacity-30');
        
        // Hide invalid file indicator
        const indicator = container.querySelector('.invalid-file-indicator');
        if (indicator) {
            indicator.classList.add('hidden');
        }
    }
}

function isFileTypeAllowed(file, fileInput) {
    const accept = fileInput.getAttribute('accept');
    if (!accept) return true;
    
    const allowedTypes = accept.split(',').map(type => type.trim());
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    const fileMimeType = file.type;
    
    return allowedTypes.some(allowedType => {
        if (allowedType.startsWith('.')) {
            return allowedType === fileExtension;
        } else {
            return fileMimeType === allowedType || fileMimeType.startsWith(allowedType.replace('*', ''));
        }
    });
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
        // Check if any dragged items are invalid files
        const fileInput = el.closest('[x-data]').querySelector('[x-ref="fileInput"]');
        const items = event.dataTransfer.items;
        let hasInvalidFile = false;
        
        if (items && items.length > 0 && fileInput) {
            const accept = fileInput.getAttribute('accept');
            if (accept) {
                // Map extensions to MIME types for better validation
                const extensionToMime = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg', 
                    '.png': 'image/png',
                    '.webp': 'image/webp',
                    '.gif': 'image/gif',
                    '.bmp': 'image/bmp',
                    '.svg': 'image/svg+xml'
                };
                
                const allowedTypes = accept.split(',').map(type => type.trim());
                const allowedMimeTypes = new Set();
                
                // Convert extensions to MIME types
                allowedTypes.forEach(type => {
                    if (type.startsWith('.')) {
                        const mimeType = extensionToMime[type.toLowerCase()];
                        if (mimeType) {
                            allowedMimeTypes.add(mimeType);
                        }
                    } else {
                        allowedMimeTypes.add(type);
                    }
                });
                
                for (let i = 0; i < items.length; i++) {
                    const item = items[i];
                    if (item.kind === 'file') {
                        const fileType = item.type;
                        if (!allowedMimeTypes.has(fileType)) {
                            hasInvalidFile = true;
                            break;
                        }
                    }
                }
            }
        }
        
        if (hasInvalidFile) {
            showRedOverlay(el);
        } else {
            showOverlay(el);
        }
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
            // Validate files before upload
            const validFiles = [];
            for (let i = 0; i < files.length; i++) {
                if (isFileTypeAllowed(files[i], fileInput)) {
                    validFiles.push(files[i]);
                }
            }
            
            if (validFiles.length > 0) {
                // Create a new FileList with only valid files
                const dt = new DataTransfer();
                validFiles.forEach(file => dt.items.add(file));
                
                // Set the valid files on the input and trigger change event
                fileInput.files = dt.files;
                data.fileName = validFiles[0].name;
                
                // Trigger the change event to activate HTMX
                fileInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
            // If no valid files, do nothing (don't trigger upload)
        }
    }

    hideOverlay(el);
    data.isDragging = false;
}

/**
 * Downloads an image from the given URL with the specified filename
 * @param {string} imageUrl - The URL of the image to download
 * @param {string} fileName - The desired filename for the downloaded image
 */
function downloadImage(imageUrl, fileName) {
    // Create a temporary anchor element
    const link = document.createElement('a');
    link.href = imageUrl;
    
    // Extract file extension from URL if not in filename
    if (!fileName.includes('.')) {
        const urlParts = imageUrl.split('.');
        const extension = urlParts[urlParts.length - 1].split('?')[0]; // Remove query params if any
        fileName = `${fileName}.${extension}`;
    }
    
    link.download = fileName;
    link.style.display = 'none';
    
    // Append to body, click, and remove
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Copies an image to the clipboard so it can be pasted into other applications
 * @param {string} imageUrl - The URL of the image to copy
 */
async function copyImageToClipboard(imageUrl) {
    try {
        // Check if we're in a secure context (HTTPS or localhost)
        if (!window.isSecureContext) {
            const protocol = window.location.protocol;
            const hostname = window.location.hostname;
            
            if (protocol === 'http:' && hostname !== 'localhost' && hostname !== '127.0.0.1') {
                showCopyFeedback('Clipboard requires HTTPS or localhost. Try using localhost instead of your current URL.', 'error');
            } else {
                showCopyFeedback('Clipboard requires secure context (HTTPS)', 'error');
            }
            return;
        }

        // Check if the Clipboard API is available
        if (!navigator.clipboard || !navigator.clipboard.write) {
            showCopyFeedback('Clipboard API not supported in this browser', 'error');
            return;
        }

        // Show loading feedback
        showCopyFeedback('Copying image...', 'loading');

        // Fetch the image
        const response = await fetch(imageUrl);
        if (!response.ok) {
            throw new Error(`Failed to fetch image: ${response.status}`);
        }

        const blob = await response.blob();
        
        // Create clipboard item with the image blob
        const clipboardItem = new ClipboardItem({
            [blob.type]: blob
        });

        // Write to clipboard
        await navigator.clipboard.write([clipboardItem]);
        showCopyFeedback('Image copied to clipboard!', 'success');

    } catch (error) {
        console.error('Failed to copy image:', error);
        showCopyFeedback('Failed to copy image', 'error');
    }
}

/**
 * Shows temporary feedback for copy operations
 * @param {string} message - The message to show
 * @param {string} type - The type of feedback ('success', 'error', 'loading')
 */
function showCopyFeedback(message, type = 'success') {
    // Remove any existing feedback
    const existingFeedback = document.querySelector('.copy-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }

    // Create feedback element
    const feedback = document.createElement('div');
    feedback.className = 'copy-feedback fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 text-white text-sm font-medium transition-all duration-300';
    
    // Set style based on type
    switch (type) {
        case 'success':
            feedback.classList.add('bg-green-600');
            break;
        case 'error':
            feedback.classList.add('bg-red-600');
            break;
        case 'loading':
            feedback.classList.add('bg-blue-600');
            break;
        default:
            feedback.classList.add('bg-gray-600');
    }

    feedback.textContent = message;
    document.body.appendChild(feedback);

    // Auto-remove after 3 seconds (except for loading messages)
    if (type !== 'loading') {
        setTimeout(() => {
            if (feedback && feedback.parentNode) {
                feedback.style.opacity = '0';
                setTimeout(() => {
                    if (feedback && feedback.parentNode) {
                        feedback.remove();
                    }
                }, 300);
            }
        }, 3000);
    }
}
