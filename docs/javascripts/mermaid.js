// Mermaid configuration for Story Sprout documentation
document$.subscribe(function() {
  // Initialize Mermaid when the document loads or changes
  if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
      startOnLoad: false,
      theme: window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'default',
      themeVariables: {
        primaryColor: '#6366f1',
        primaryTextColor: '#1f2937',
        primaryBorderColor: '#4f46e5',
        lineColor: '#6b7280',
        sectionBkgColor: '#f8fafc',
        altSectionBkgColor: '#f1f5f9',
        gridColor: '#e5e7eb',
        secondaryColor: '#e0e7ff',
        tertiaryColor: '#f3f4f6'
      }
    });

    // Re-render mermaid diagrams on page navigation
    mermaid.run({
      querySelector: '.mermaid'
    });
  }
});

// Handle theme switching for mermaid diagrams
if (typeof window !== 'undefined' && window.matchMedia) {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    if (typeof mermaid !== 'undefined') {
      const theme = e.matches ? 'dark' : 'default';
      mermaid.initialize({ 
        startOnLoad: false,
        theme: theme,
        themeVariables: {
          primaryColor: '#6366f1',
          primaryTextColor: e.matches ? '#f9fafb' : '#1f2937',
          primaryBorderColor: '#4f46e5',
          lineColor: '#6b7280',
          sectionBkgColor: e.matches ? '#1f2937' : '#f8fafc',
          altSectionBkgColor: e.matches ? '#374151' : '#f1f5f9',
          gridColor: '#6b7280',
          secondaryColor: e.matches ? '#312e81' : '#e0e7ff',
          tertiaryColor: e.matches ? '#374151' : '#f3f4f6'
        }
      });
      
      // Re-render all mermaid diagrams with new theme
      document.querySelectorAll('.mermaid').forEach(function(element) {
        element.removeAttribute('data-processed');
      });
      mermaid.run({
        querySelector: '.mermaid'
      });
    }
  });
}
