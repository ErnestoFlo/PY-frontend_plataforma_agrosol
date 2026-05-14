document.addEventListener('DOMContentLoaded', () => {
  // *********************************************************
  // ******* INICIALIZACION DE COMPONENTES / LIBRERIAS *******
  // *********************************************************

  // Inicialización de módulos que lo requieran
  // Inicializa tablas responsivas de todo el proyecto
  if (window.ResponsiveTable) {window.ResponsiveTable.initResponsiveTable('[data-responsive-table="proveedores"]')}  // Tabla de proveedores
  if (window.ResponsiveTable) {window.ResponsiveTable.initResponsiveTable('[data-responsive-table="usuarios"]')}  // Tabla de usuarios
  if (window.Login) {window.Login.init()} // Inicializa el módulo de login (inactividad)
  flatpickr("#c-date-hourpicker", {
        enableTime: true,
        time_24hr: true,
        dateFormat: "Y-m-d H:i",
        locale: "es",
        disableMobile: true,
        showMonths: 1,
  });
  flatpickr("#c-datepicker", {
        enableTime: false,
        time_24hr: true,
        dateFormat: "Y-m-d",
        locale: "es",
        disableMobile: true,
        showMonths: 1,
  });
  // Estado del sidebar
  const SIDEBAR_STATE_KEY = 'sidebarCollapsed'
  const sidebar = document.getElementById('sidebar')

  if (sidebar) {
    const saved = localStorage.getItem(SIDEBAR_STATE_KEY)
    if (saved === 'true' || saved === 'false') {
      sidebar.dataset.collapsed = saved
    } else {
      // valor por defecto (abierta)
      sidebar.dataset.collapsed = 'false'
    }
  }
  const theme = document.documentElement.getAttribute('data-theme')
  updateThemeAssets(theme)
  const skeleton = document.querySelector('#skeleton-template')
  const aside = document.querySelector('#sidebar');
  const accordions = document.querySelectorAll('.sidebar-accordion');

  // *********************************************
  // *********** ASIGNACION DE EVENTOS ***********
  // *********************************************
  // ***** BOTONES *****
  document.querySelectorAll('[data-action="toggleTheme"]').forEach(btn => {btn.addEventListener('click', toggleTheme)})
  document.querySelectorAll('[data-action="togglePassword"]').forEach(btn => {btn.addEventListener('click', (e) => togglePassword(e.currentTarget))})
  document.querySelectorAll('[data-action="collapseSidebar"]').forEach(btn => {btn.addEventListener('click', (e) => collapseSidebar(e.currentTarget))})
  document.querySelectorAll('[data-action="handleBack"]').forEach(btn => {btn.addEventListener('click', (e) => handleBack())})
  document.querySelectorAll('[data-action="cerrarSesionAhora"]').forEach(btn => {btn.addEventListener('click', (e) => window.Login.cerrarSesionAhora())})
  document.querySelectorAll('[data-action="continuarSesion"]').forEach(btn => {btn.addEventListener('click', (e) => window.Login.continuarSesion())})
  // **** INPUTS ****
  document.querySelectorAll('[data-action="filtrarSugerencias"]').forEach(searcher => {searcher.addEventListener('input', (e) => filtrarSugerencias(e.currentTarget.value))})
  document.querySelectorAll('[data-action="actualizarIniciales"]').forEach(input => {input.addEventListener('input', (e) => actualizarIniciales())})
  // **** COMBOBOXES ****
  document.querySelectorAll('[data-action="comboboxToggle"]').forEach(trigger => {trigger.addEventListener('click', (e) => comboboxToggle(e.currentTarget))})
  document.querySelectorAll('[data-action="combobox"]').forEach(container => {container.addEventListener('focusout', (e) => close_dropdown(e  ))})
  // ***** TOGGLE *****
  document.querySelectorAll('[data-action="toggle"]').forEach(btn => {
    btn.addEventListener('click', (e) => toggleSwitch(e.currentTarget))
  })
  // ***** FILE PICKER *****
  document.addEventListener('click', (e) => {
    const zone = e.target.closest('[data-action="filePickerZone"]')
    if (!zone) return
    const picker = zone.closest('.file-picker')
    const input = picker.querySelector('.file-input')
    input.click()
  })
  document.addEventListener('dragover', (e) => {
    const zone = e.target.closest('[data-action="filePickerZone"]')
    if (!zone) return
    e.preventDefault()
    zone.classList.add('drag-over')
  })
  document.addEventListener('dragleave', (e) => {
    const zone = e.target.closest('[data-action="filePickerZone"]')
    if (!zone) return
    zone.classList.remove('drag-over')
  })
  document.addEventListener('drop', (e) => {
    const zone = e.target.closest('[data-action="filePickerZone"]')
    if (!zone) return
    e.preventDefault()
    zone.classList.remove('drag-over')
    const picker = zone.closest('.file-picker')
    const input = picker.querySelector('.file-input')
    handleFiles(picker, input, e.dataTransfer.files)
  })
  document.addEventListener('change', (e) => {
    if (!e.target.classList.contains('file-input')) return

    const picker = e.target.closest('.file-picker')
    const isAvatarInput = picker?.dataset.name === 'c-file-foto'

    if (isAvatarInput) {
      previewAvatar(e.target)
      return
    }

    handleFiles(picker, e.target, e.target.files)
  })

  // ***** BOTTOM BAR *****
  document.querySelectorAll('[data-action="bottombarItem"]').forEach(item => {
    item.addEventListener('click', (e) => {
      const bar = e.currentTarget.closest('.bottombar')
      if (!bar) return
      bar.querySelectorAll('.bottombar-item').forEach(i => i.classList.remove('active'))
      e.currentTarget.classList.add('active')
    })
  })
  // ***** DELEGATED CLICK LISTENER *****
  // Un único listener para acciones globales.
  // Clave para HTMX: también cubre nodos inyectados después del load inicial.
  document.addEventListener('click', (e) => {
    // Detectar acción desde data-action
    const actionBtn = e.target.closest('[data-action="openModal"], [data-action="closeModal"], [data-action="togglePopover"], [data-action="closePopover"]')
    
    if (actionBtn) {
      // Evita que HTMX procese también el click en el mismo botón.
      e.preventDefault()
      const action = actionBtn.dataset.action
      const target = actionBtn.dataset.target
      const get_url = actionBtn.getAttribute('hx-get')
      
      if (action === 'openModal') {
        openModal(target, get_url)
      } else if (action === 'closeModal') {
        closeModal(target)
      } else if (action === 'togglePopover') {
        e.stopPropagation()
        togglePopover(target)
      } else if (action === 'closePopover') {
        closePopover(target)
      } 
      return // Prevenir propagación innecesaria
    }
    
    // Cerrar popovers al hacer clic fuera
    if (!e.target.closest('[data-action="popoverContainer"]')) {
      document.querySelectorAll('.popover').forEach(p => p.setAttribute('data-open', 'false'))
      document.querySelectorAll('.bottombar-more-popover').forEach(p => p.setAttribute('data-open', 'false'))
    }
  })
  // ***** HTMX EVENT LISTENERS *****
  // Deshabilitar botón submit SOLO cuando HTMX comienza una petición validada
  document.addEventListener('htmx:beforeRequest', (e) => {
    const form = e.target.closest('form')
    if (form && e.detail.xhr.upload) {
      const submitBtn = form.querySelector('[type="submit"]')
      if (submitBtn) {
        submitBtn.disabled = true
        submitBtn.style.opacity = '0.6'
        submitBtn.style.cursor = 'not-allowed'
      }
    }
  })
  // Re-habilitar botón si hay error HTTP
  document.addEventListener('htmx:responseError', (e) => {
    const form = e.target.closest('form')
    if (form) {
      const submitBtn = form.querySelector('[type="submit"]')
      if (submitBtn) {
        submitBtn.disabled = false
        submitBtn.style.opacity = '1'
        submitBtn.style.cursor = 'pointer'
      }
    }
  })


  // *********************************************
  // ***************   FUNCIONES   ***************
  // *********************************************

  // Regresar a la página anterior
  function handleBack() {
    try {
      if (window.history.length > 1) {
        history.back();
      } else {
        window.location.href = "/dashboard/";
      }
    } catch (e) {
      window.location.href = "/dashboard/";
    }
  }
  // Cambiar tema de color
  function toggleTheme() {
    const html = document.documentElement
    const current = html.getAttribute('data-theme')
    const next = current === 'dark' ? 'light' : 'dark'

    html.setAttribute('data-theme', next)
    localStorage.setItem('theme', next)

    // Actualiza el ícono del botón
    updateThemeAssets(next)
  }
  function updateThemeAssets(theme) {
    const btn = document.querySelector('[data-action="toggleTheme"]')
    const main_logo = document.querySelector('#main-logo')
    if (btn) {
      const icon = btn.querySelector('use')
      const sprite = btn.dataset.sprite;
      icon.setAttribute(
        'href',
        theme === 'dark'
          ? `${sprite}#icon-sun-regular`
          : `${sprite}#icon-moon-regular`
      )
    }
    if(main_logo){
      main_logo.setAttribute(
        'src',
        theme === 'dark'
          ? '/static/images/logo letras blancas icono color@4x-8.png'
          : '/static/images/Logo princiapal@4x-8.png'
      )
    }
  }

  // OBSERVAR CAMBIOS EN ATRIBUTOS DE CUALQUIER ELEMENTO
  function watchAttribute(element, attr, callback) {
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (mutation.attributeName === attr) {
          callback(element.getAttribute(attr));
        }
      }
    });

    observer.observe(element, {
      attributes: true,
      attributeFilter: [attr],
    });

    return observer;
  }

  // CAMBIOS POR ATRIBUTOS
  // Sidebar cierra = acordeon cierra
  function closeAccordionsInside(container) {
    const details = container.querySelectorAll('details');

    details.forEach((item) => {
      item.removeAttribute('open');
    });
  }
  if (aside) {
    watchAttribute(aside, 'data-collapsed', (value) => {
      if (value === 'true') {
        closeAccordionsInside(aside);
      }
    });
  }

  // Acordeon abre = sidebar abre
  function expandSidebar() {
    if (aside) {
      aside.setAttribute('data-collapsed', 'false');
    }
  }
  accordions.forEach((accordion) => {
    accordion.addEventListener('toggle', () => {
      if (accordion.open) expandSidebar();
    });
  });

  // Recuperar eventos de elementos recuperados por HTMX (ej. modales y formularios)
  document.body.addEventListener("htmx:historyRestore", function (evt) {
    const modal = evt.target.querySelector('.modal')
    if (modal) {
      const form = modal.querySelector('form')
      if (form) {
        form.addEventListener('submit', () => {
          const submitBtn = form.querySelector('[type="submit"]')
          if (submitBtn) {
            submitBtn.disabled = true
            submitBtn.style.opacity = '0.6'
            submitBtn.style.cursor = 'not-allowed'
          }
        })
      }
    }
  });


  const SUGERENCIAS = ['Proyecto Alpha','Stock Herramientas','Lote Alimentos Q1','Colección Ropa Verano','Dispositivos Electrónicos','Fertilizante NPK','Semillas Maíz','Abono Orgánico','Fungicida Mancozeb'];
    // Sugerencias dinamicas para un buscador
    const results = document.getElementById('search-results');
    results.addEventListener('click', (e) => {
      const item = e.target.closest('.suggestion');
      if (!item) return;
      seleccionarSugerencia(item.dataset.suggestion);
    });


    function seleccionarSugerencia(val) {
      document.getElementById('c-searcher').value = val;
      document.getElementById('search-results').classList.add('hidden');
      AlertManager.info(`Seleccionado: ${val}`);
    }

    function filtrarSugerencias(q) {
      if (!q.trim()) { results.classList.add('hidden'); return; }
      const matches = SUGERENCIAS.filter(s => s.toLowerCase().includes(q.toLowerCase()));
      if (!matches.length) { results.classList.add('hidden'); return; }
      results.innerHTML = matches.map(m =>
        `<div class="suggestion px-3 py-4 body cursor-pointer flex items-center gap-3" data-suggestion="${m}">
          <svg class="w-5 h-5 p-0 input-button btn-icon-ghost-neutral">
            <use href="/static/sprite.svg#icon-magnifyng-glass-fill" />
          </svg>
          ${m}
        </div>`
      ).join('');
      results.classList.remove('hidden');
    }

    document.addEventListener('click', e => {
      if (!e.target.closest('.search-wrapper')) {
        document.getElementById('search-results').classList.remove('show');
      }
    });


  // Color pickers sync
  document.querySelector('#c-color')?.addEventListener('input', (e) => {
    actualizarColor(e.target.value)
  })
  document.querySelector('#color-hex-val')?.addEventListener('input', (e) => {
    sincronizarColor(e.target.value)
  })
  function actualizarColor(val) {
    document.getElementById('color-hex-val').value = val;
  }
  function sincronizarColor(val) {
    if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
      document.getElementById('c-color').value = val;
    }
  }


  // File Upload Preview
function handleFiles(picker, input, files) {
  const list = picker.querySelector('.file-list')
  const preview = picker.querySelector('.upload-preview')
  const img = picker.querySelector('.preview-img')

  if (!list) return
  list.innerHTML = ''
  Array.from(files).forEach(file => {
    const size = file.size < 1024 * 1024
      ? `${(file.size / 1024).toFixed(1)} KB`
      : `${(file.size / 1024 / 1024).toFixed(1)} MB`
    const li = document.createElement('li')
    li.className = 'file-item flex gap-2 items-center'
    li.innerHTML = `
      <svg class="w-4 h-4 text-fg-muted">
        <use href="/static/sprite.svg#icon-file-regular"/>
      </svg>
      <span>${file.name}</span>
      <span class="text-xs text-fg-muted">${size}</span>
    `
    list.appendChild(li)
  })
  // preview SOLO si es imagen
  const first = files[0]
  if (first && first.type.startsWith('image/')) {

    const reader = new FileReader()

    reader.onload = (ev) => {
      img.src = ev.target.result
      preview.classList.remove('hidden')
    }

    reader.readAsDataURL(first)
  }
  // Actualiza el input file para que el formulario lo envíe
  input.files = files
}

// Avatar Upload Preview
  function previewAvatar(input) {
    if (!input.files || !input.files[0]) return
    const reader = new FileReader()
    reader.onload = e => {
      const img = document.getElementById('avatar-img-preview')
      img.src = e.target.result
      img.style.display = 'block'
      const initials = document.getElementById('avatar-initials')
      if (initials) {
        initials.style.display = 'none'
      }
    }
    reader.readAsDataURL(input.files[0])
  }
  function actualizarIniciales() {
    console.log('ejecutando')
    const fn = document.getElementById('f-first_name').value.trim();
    const ln = document.getElementById('f-last_name').value.trim();
    document.getElementById('avatar-initials').textContent =
      ((fn[0] || '') + (ln[0] || '')).toUpperCase() || '?';
  }

  // Mostrar - Ocultar Contraseña
  function togglePassword(btn){
    const inputId = btn.dataset.target
    const input = document.getElementById(inputId)
    const sprite = btn.dataset.sprite
    const isPassword = input.type === 'password'

    input.type = isPassword ? 'text' : 'password'

    const icon = btn.querySelector('use')
    icon.setAttribute(
      'href',
      isPassword
        ? `${sprite}#icon-close-eye-regular`
        : `${sprite}#icon-open-eye-regular`
    )
  }

  // Cerrar el sidebar cuando hay un clic en el botón cerrar
  function collapseSidebar(btn){
    const sidebarId = btn.dataset.target;
    const sidebar = document.getElementById(sidebarId);
    if (!sidebar) return;

    const isCollapsed = sidebar.dataset.collapsed === 'true'
    const next = isCollapsed ? 'false' : 'true'
    sidebar.dataset.collapsed = next
    localStorage.setItem('sidebarCollapsed', next)
  }

  // Abrir y cerrar el dropdown de un combobox
  function comboboxToggle(trigger){
    const targetId = trigger.dataset.target + '-options'
    const dropdown = document.getElementById(targetId)
    if (!dropdown) return  // ← si aún no existe, no hace nada
    dropdown.classList.contains('hidden') ? dropdown.classList.remove('hidden') : dropdown.classList.add('hidden')
  }
  document.addEventListener('htmx:afterSwap', (e) => {
    const dropdown = e.target.classList.contains('combobox-dropdown')
      ? e.target
      : e.target.closest('.combobox-dropdown')
    
    if (!dropdown) return
    dropdown.classList.remove('hidden')
  })

  // Seleccionar una opción de un combobox — usa delegación porque las opciones las inyecta HTMX
  document.addEventListener('click', (e) => {
    const option = e.target.closest('[data-action="combobox-select"]')
    if (!option) return

    const dropdown = option.closest('ul')
    const inputId = dropdown.dataset.input
    const input = document.getElementById(inputId)

    input.value = option.dataset.value
    dropdown.classList.add('hidden')
  })
  // Cerrar al hacer clic fuera
  function close_dropdown(e){
    // relatedTarget es el elemento que recibe el foco a continuación
    const container = e.currentTarget
    if (!container.contains(e.relatedTarget)) {
      const dropdown = container.querySelector('.combobox-dropdown')
      if (!dropdown) return
      dropdown.classList.add('hidden')
    }
  }

  // Toggle switch
  function toggleSwitch(btn) {
    const isChecked = btn.dataset.checked === 'true'
    btn.dataset.checked = isChecked ? 'false' : 'true'
  }

  // Modal
  function openModal(modalId, get_url) {
    const modal = document.getElementById(modalId)
    if (!modal) return

    // Fix temporal de jerarquía: cerrar cualquier modal abierta antes de abrir otra.
    document.querySelectorAll('.modal-overlay').forEach((overlay) => {
      if (overlay.id !== modalId) {
        const content = overlay.querySelector('[id$="-content"]')
        if (content) content.innerHTML = ''
        overlay.classList.add('hidden')
      }
    })

    const form_container = document.querySelector(`#${modalId}-content`)
    form_container.innerHTML = skeleton.innerHTML
    modal.classList.remove('hidden')
    if (form_container && get_url) {
      // Normaliza query params para que backend retorne el fragmento correcto
      // según contexto (viewport/página y modal de formulario).
      let requestUrl = get_url
      const url = new URL(get_url, window.location.origin)
      const isFormModal = modalId === 'modal-create' || modalId === 'modal-edit'
      const isMobileViewport = window.matchMedia('(max-width: 767px)').matches
      if (!url.searchParams.has('viewport')) {
        url.searchParams.set('viewport', isMobileViewport ? 'mobile' : 'desktop')
      }
      if (!url.searchParams.has('page')) {
        const currentPage = new URLSearchParams(window.location.search).get('page') || '1'
        url.searchParams.set('page', currentPage)
      }
      if (isFormModal && !url.searchParams.has('fragment')) {
        url.searchParams.set('fragment', 'form')
      }
      if (isFormModal && !url.searchParams.has('edit_form')) {
        url.searchParams.set('edit_form', true)
      }
      console.log("URL antes de normalizar:", get_url)
      requestUrl = `${url.pathname}${url.search}`

      htmx.ajax('GET', requestUrl, {
        target: form_container,
        swap: 'innerHTML'
      })
      console.log("URL:", requestUrl)
    }

    document.body.style.overflow = 'hidden'
  }

  // ============================================================================
  // ALERT MANAGER - Gestor centralizado de alertas
  // ============================================================================
  class AlertManager {
    constructor() {
      this.container = this.initContainer()
      this.alerts = new Map()
      this.config = {
        duration: 3000,
        position: 'bottom-right',
        maxStack: 5
      }
      this.iconMap = {
        success: 'icon-check-circle-fill',
        danger: 'icon-xmark-circle-fill',
        warning: 'icon-exclamation-circle-fill',
        info: 'icon-info-circle-fill'
      }
    }
    static instance = null
    static getInstance() {
      if (!this.instance) {
        this.instance = new AlertManager()
      }
      return this.instance
    }
    initContainer() {
      let container = document.getElementById('alerts-container')
      if (!container) {
        container = document.createElement('div')
        container.id = 'alerts-container'
        container.className = 'fixed top-4 right-4 z-[500] flex flex-col gap-2 max-w-md'
        document.body.appendChild(container)
      }
      return container
    }
    /**
     * Alerta simple: solo mensaje, desaparece automáticamente
     * @param {string} message - Mensaje a mostrar
     * @param {string} variant - success, error, warning, info
     * @param {number} duration - Tiempo en ms antes de desaparecer (default: 3000)
     */
    simple(message, variant = 'success', duration) {
      const alertId = `alert-${Date.now()}`
      const durationMs = duration || this.config.duration
      const icon = this.iconMap[variant] || this.iconMap.info

      const alertDiv = document.createElement('div')
      alertDiv.id = alertId
      alertDiv.className = `alert-simple alert-${variant} mb-2 alert-enter`
      alertDiv.setAttribute('role', 'alert')
      alertDiv.innerHTML = `
        <svg class="w-5 h-5 shrink-0">
          <use href="/static/sprite.svg#${icon}"/>
        </svg>
        <span class="text-sm font-semibold">${message}</span>
      `
      this.container.appendChild(alertDiv)
      this.alerts.set(alertId, { element: alertDiv, timeout: null })
      // Auto-dismiss
      const timeoutId = setTimeout(() => {
        this.dismiss(alertId)
      }, durationMs)
      this.alerts.get(alertId).timeout = timeoutId
      return alertId
    }
    /**
     * Alerta detallada: con título y descripción, requiere cierre manual
     * @param {string} title - Título de la alerta
     * @param {string} body - Descripción detallada
     * @param {string} variant - success, error, warning, info
     */
    detailed(title, body, variant = 'info') {
      const alertId = `alert-${Date.now()}`
      const icon = this.iconMap[variant] || this.iconMap.info

      const alertDiv = document.createElement('div')
      alertDiv.id = alertId
      alertDiv.className = `alert-detailed alert-${variant} alert-enter`
      alertDiv.setAttribute('role', 'alert')
      alertDiv.innerHTML = `
        <div class="flex items-center justify-between w-full">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 shrink-0">
              <use href="/static/sprite.svg#${icon}"/>
            </svg>
            <span class="font-display font-semibold text-sm">${title}</span>
          </div>
          <button type="button" class="shrink-0 text-fg-muted hover:text-fg transition-colors" data-alert-dismiss="${alertId}">
            <svg class="w-4 h-4">
              <use href="/static/sprite.svg#icon-xmark-fill"/>
            </svg>
          </button>
        </div>
        <p class="text-sm text-fg-body mt-2 ml-7">${body}</p>
      `
      const closeBtn = alertDiv.querySelector('[data-alert-dismiss]')
      closeBtn.addEventListener('click', () => this.dismiss(alertId))
      this.container.appendChild(alertDiv)
      this.alerts.set(alertId, { element: alertDiv, timeout: null })
      return alertId
    }
    dismiss(alertId) {
      const alert = this.alerts.get(alertId)
      if (!alert) return
      // Cancelar timeout si existe
      if (alert.timeout) clearTimeout(alert.timeout)
      // Animar salida
      alert.element.classList.remove('alert-enter')
      alert.element.classList.add('alert-exit')
      // Remover después de animación
      setTimeout(() => {
        alert.element.remove()
        this.alerts.delete(alertId)
      }, 300)
    }
    dismissAll() {
      this.alerts.forEach((_, alertId) => {
        this.dismiss(alertId)
      })
    }
    // ========== ATAJOS ESTÁTICOS (fácil acceso) ==========
    static success(message, duration) {
      return this.getInstance().simple(message, 'success', duration)
    }
    static danger(message, duration) {
      return this.getInstance().simple(message, 'danger', duration)
    }
    static warning(message, duration) {
      return this.getInstance().simple(message, 'warning', duration)
    }
    static info(message, duration) {
      return this.getInstance().simple(message, 'info', duration)
    }
    static detailedSuccess(title, body) {
      return this.getInstance().detailed(title, body, 'success')
    }
    static detailedDanger(title, body) {
      return this.getInstance().detailed(title, body, 'danger')
    }
    static detailedWarning(title, body) {
      return this.getInstance().detailed(title, body, 'warning')
    }
    static detailedInfo(title, body) {
      return this.getInstance().detailed(title, body, 'info')
    }
  }
  window.AlertManager = AlertManager

  // Mostrar - Cerrar Popovers
  function togglePopover(popoverId) {
    const popover = document.getElementById(popoverId)
    if (!popover) return
    const isOpen = popover.dataset.open === 'true'
    // Cierra todos los demás primero
    document.querySelectorAll('.popover').forEach(p => p.setAttribute('data-open', 'false'))
    popover.setAttribute('data-open', isOpen ? 'false' : 'true')
  }

  function closePopover(popoverId) {
    const popover = document.getElementById(popoverId)
    if (!popover) return
    popover.setAttribute('data-open', 'false')
  }
  window.closePopover = closePopover

  // ==================================
  // LOGS
  // ==================================

  // ── Filtros ──
    function filtrarLogs(tipo) {
      document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('filtro-activo'));
      document.getElementById('f-' + tipo)?.classList.add('filtro-activo');
      document.querySelectorAll('.log-row').forEach(row => {
        row.classList.toggle('hidden', tipo !== 'todos' && row.dataset.tipo !== tipo);
      });
    }

  // Mostrar mensaje de éxito almacenado en sessionStorage (desde HTMX o redirecciones) 
  // cuando la pagina recarga en su totalidad y se necesita dar feedback de una accion previa
  const message = sessionStorage.getItem('success_message');

  if (message) {
    AlertManager.success(message);
    sessionStorage.removeItem('success_message');
  }

})

  // Cerrar el modal cuando hay un clic en el botón cerrar
  function closeModal(modalId) {
    const modal = document.getElementById(modalId)
    if (!modal) return
    const form_container = modal.querySelector(`#${modalId}-content`)
    if (form_container) form_container.innerHTML = ''
    modal.classList.add('hidden')
    document.body.style.overflow = ''

    // Si por cualquier flujo se cambió la URL a rutas de acción, vuelve a listado.
    const currentPath = window.location.pathname
    const isProveedorActionPath = /^\/agrosol\/proveedores\/(crear|editar\/[^/]+|confirmar\/[^/]+|eliminar\/[^/]+)\/?$/.test(currentPath)
    if (isProveedorActionPath) {
      window.history.replaceState(null, '', '/agrosol/proveedores/')
    }
  }
  window.closeModal = closeModal