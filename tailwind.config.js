module.exports = {
    // Directorios que se deben analizar para encontrar las clases de Tailwind
    content: [
        './**/templates/**/*.html',
    ],
    // Lista de clases que se deben incluir en el CSS para evitar que Tailwind las elimine
    // Esto es necesario para que los componentes de terceros como flatpickr funcionen correctamente
    safelist: [
        { pattern: /flatpickr-/ }
    ],
    theme: {
        extend: {},
        },
    plugins: [],
}