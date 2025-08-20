// Alpine.js image upload component
function imageUpload(hasImage = false) {
    return {
        fileName: '',
        isDragging: false,
        isHovering: false,
        hasImage: hasImage,
        isUploading: false,

        showOverlay() {
            this.$refs.container.classList.add('bg-black', 'bg-opacity-20');
        },

        hideOverlay() {
            this.$refs.container.classList.remove('bg-black', 'bg-opacity-20');
        },

        handleMouseEnter() {
            if (!this.isDragging && !this.isUploading) {
                this.showOverlay();
                this.isHovering = true;
            }
        },

        handleMouseLeave() {
            if (!this.isDragging && !this.isUploading) {
                this.hideOverlay();
                this.isHovering = false;
            }
        },

        handleDragOver() {
            if (this.isUploading) return;
            
            if (this.isHovering) {
                this.isHovering = false;
            } else {
                this.showOverlay();
            }
            this.isDragging = true;
        },

        handleDragEnd() {
            if (this.isUploading) return;
            
            this.hideOverlay();
            this.isDragging = false;
        },

        handleFileSelected() {
            if (this.$refs.fileInput.files.length > 0) {
                this.fileName = this.$refs.fileInput.files[0].name;
                this.isUploading = true;
                this.hideOverlay();
            }
        },

        // HTMX event handlers
        init() {
            // Listen for HTMX events
            this.$el.addEventListener('htmx:beforeRequest', () => {
                this.isUploading = true;
            });
            
            this.$el.addEventListener('htmx:afterRequest', () => {
                this.isUploading = false;
                this.fileName = '';
            });
        }
    }
}
