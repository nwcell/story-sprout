/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'gray': '#6B7280',
        'light-gray': '#E5E7EB',
        'dark-gray': '#4B5563',
        'black': '#1F2937',
        'white': '#FFFFFF',
      },
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '2rem',
      },
      fontSize: {
        'xxs': '0.625rem',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in',
        'slide-down': 'slideDown 0.3s ease-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      boxShadow: {
        'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
        'medium': '0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
      },
    },
  },
  variants: {
    extend: {
      opacity: ['group-hover', 'focus-within', 'disabled'],
      cursor: ['hover', 'focus', 'disabled'],
      backgroundColor: ['disabled'],
      textColor: ['disabled'],
      borderColor: ['focus-within'],
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    function ({ addComponents }) {
      addComponents({
        '.editable-field-container': {
          position: 'relative',
          borderWidth: '1px',
          borderColor: 'transparent',
          borderRadius: '0.375rem', // rounded-md
          padding: '0.5rem',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: '#E5E7EB', // light-gray
          },
          '&:focus-within': {
            borderColor: '#6B7280', // gray
            boxShadow: '0 0 0 3px rgba(156, 163, 175, 0.1)',
          }
        },
      })
    }
  ],
}
