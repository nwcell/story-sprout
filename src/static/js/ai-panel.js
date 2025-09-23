/**
 * AI Panel Management - Alpine.js Extension
 */

document.addEventListener('alpine:init', () => {
    console.log('AI Panel initialization');

    Alpine.store('aiPanel', {
        // Persisted state - defaults to true if unset
        isOpen: Alpine.$persist(true).as('ai-panel-open'),
        panelHeight: 16, // Will be calculated properly in init

        // Initialize the store
        init() {
            this.setupNavigationListener();
            this.setupResizeObserver();
            // Calculate initial height without changing state
            this.calculateHeight();
        },

        // Business Logic Methods
        toggle() {
            this.isOpen = !this.isOpen;
        },

        open() {
            this.isOpen = true;
        },

        close() {
            this.isOpen = false;
        },


        calculateHeight() {
            // Calculate the panel height for main content margin adjustment
            if (this.isOpen) {
                // Use nextTick to ensure DOM is updated
                Alpine.nextTick(() => {
                    const panel = document.getElementById('ai-panel-main');
                    if (panel) {
                        this.panelHeight = panel.offsetHeight + 24; // Add 1.5rem spacing
                    }
                });
            } else {
                this.panelHeight = 16; // 1rem when closed
            }
        },

        setupNavigationListener() {
            // Recalculate height after HTMX content loads
            document.addEventListener('htmx:afterSettle', () => {
                this.calculateHeight();
            });
        },

        setupResizeObserver() {
            // Watch for panel size changes to update height
            Alpine.nextTick(() => {
                const panel = document.getElementById('ai-panel-main');
                if (panel && window.ResizeObserver) {
                    const resizeObserver = new ResizeObserver(() => {
                        if (this.isOpen) {
                            this.calculateHeight();
                        }
                    });
                    resizeObserver.observe(panel);
                }
            });
        }
    });


    // Initialize the store after registration
    Alpine.store('aiPanel').init();
});

/**
 * Utility functions for external JavaScript access
 *
 * These provide a clean API for other parts of the application
 * to interact with the AI panel
 */
window.AiPanel = {
    get isOpen() {
        return Alpine.store('aiPanel').isOpen;
    },

    toggle() {
        Alpine.store('aiPanel').toggle();
    },

    open() {
        Alpine.store('aiPanel').open();
    },

    close() {
        Alpine.store('aiPanel').close();
    }
};

console.log('AI Panel module loaded');
