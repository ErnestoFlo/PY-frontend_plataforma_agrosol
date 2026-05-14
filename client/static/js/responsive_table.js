(function () {
  // Módulo dueño del "primer render" responsive de la tabla de proveedores.
  // Decide el fragmento HTMX a pedir según viewport y mantiene URL/paginación.
  function initResponsiveTable(containerSelector) {
    const responsiveTableContainer = document.querySelector(containerSelector)
    if (!responsiveTableContainer || typeof htmx === 'undefined') return

    const sourceUrl = responsiveTableContainer.dataset.sourceUrl
    if (!sourceUrl) return

    const mediaQuery = window.matchMedia('(max-width: 767px)')
    let currentFragment = null

    function getPageFromUrl() {
      const params = new URLSearchParams(window.location.search)
      const page = parseInt(params.get('page') || '1', 10)
      return Number.isNaN(page) || page < 1 ? 1 : page
    }

    function resolveFragment() {
      // Desktop usa tabla clásica; mobile usa cards.
      return mediaQuery.matches ? 'table_mobile' : 'table'
    }

    function loadResponsiveTable(forceReload = false) {
      const nextFragment = resolveFragment()
      if (!forceReload && currentFragment === nextFragment) return

      currentFragment = nextFragment
      const page = getPageFromUrl()
      const targetUrl = `${sourceUrl}?page=${page}&fragment=${nextFragment}`
      console.log(targetUrl)

      htmx.ajax('GET', targetUrl, {
        target: responsiveTableContainer,
        swap: 'innerHTML',
        pushURL: true
      })
    }

    loadResponsiveTable(true)
    mediaQuery.addEventListener('change', () => loadResponsiveTable(true))
  }


  window.ResponsiveTable = {
    initResponsiveTable,
  }
})()