document.addEventListener('DOMContentLoaded', () => {
  // ******* INICIALIZACION DE COMPONENTES / LIBRERIAS *******
  flatpickr("#fecha_hora", {
        enableTime: true,
        time_24hr: true,
        dateFormat: "Y-m-d H:i",
        locale: "es",
        disableMobile: true,
        showMonths: 1,
  });
  flatpickr("#fecha", {
        enableTime: false,
        time_24hr: true,
        dateFormat: "Y-m-d",
        locale: "es",
        disableMobile: true,
        showMonths: 1,
  });
  const theme = document.documentElement.getAttribute('data-theme')
  updateThemeIcon(theme)

  // *********** ASIGNACION DE EVENTOS ***********
  // ***** BOTONES *****
  document.querySelectorAll('[data-action="toggleTheme"]').forEach(btn => {btn.addEventListener('click', toggleTheme)})
  document.querySelectorAll('[data-action="togglePassword"]').forEach(btn => {btn.addEventListener('click', (e) => togglePassword(e.currentTarget))})
  document.querySelectorAll('[data-action="collapseSidebar"]').forEach(btn => {btn.addEventListener('click', (e) => collapseSidebar(e.currentTarget))})
  // **** COMBOBOXES ****
  document.querySelectorAll('[data-action="comboboxToggle"]').forEach(trigger => {trigger.addEventListener('click', (e) => comboboxToggle(e.currentTarget))})
  document.querySelectorAll('[data-action="combobox"]').forEach(container => {container.addEventListener('focusout', (e) => close_dropdown(e  ))})
  // ***** RANGES *****
  document.querySelectorAll('[data-action="rangeUpdate"]').forEach(input => {
    const inputId = wrapper.dataset.target
    const fill = document.getElementById(`${inputId}-fill`)
    const thumb = document.getElementById(`${inputId}-thumb`)
    const output = document.getElementById(`${inputId}-value`)
    input.addEventListener('input', (e) => rangeUpdate(e.currentTarget, fill, thumb, output))
  })
  // ***** TOGGLE *****
  document.querySelectorAll('[data-action="toggle"]').forEach(btn => {
    btn.addEventListener('click', (e) => toggleSwitch(e.currentTarget))
  })
  // ***** MODAL *****
  document.querySelectorAll('[data-action="openModal"]').forEach(btn => {
    btn.addEventListener('click', (e) => openModal(e.currentTarget.dataset.target))
  })
  document.querySelectorAll('[data-action="closeModal"]').forEach(btn => {
    btn.addEventListener('click', (e) => closeModal(e.currentTarget.dataset.target))
  })
  document.addEventListener('click', (e) => {
    if (e.target.matches('.modal-overlay')) closeModal(e.target.id)
  })
  // ***** FILE PICKER *****
  document.querySelectorAll('[data-action="filePickerZone"]').forEach(zone => {
    const inputId = zone.dataset.target
    const input = document.getElementById(inputId)
    if (!input) return

    zone.addEventListener('click', () => input.click())
    zone.addEventListener('dragover', (e) => { e.preventDefault(); zone.classList.add('drag-over') })
    zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'))
    zone.addEventListener('drop', (e) => {
      e.preventDefault()
      zone.classList.remove('drag-over')
      renderFileList(inputId, e.dataTransfer.files)
    })
    input.addEventListener('change', () => renderFileList(inputId, input.files))
  })



  // ***************   FUNCIONES   ***************

    // Cambiar tema de color
  function toggleTheme() {
    const html = document.documentElement
    const current = html.getAttribute('data-theme')
    const next = current === 'dark' ? 'light' : 'dark'

    html.setAttribute('data-theme', next)
    localStorage.setItem('theme', next)

    // Actualiza el ícono del botón
    updateThemeIcon(next)
  }
  function updateThemeIcon(theme) {
    const btn = document.querySelector('[data-action="toggleTheme"]')
    if (!btn) return
    const icon = btn.querySelector('use')
    const sprite = btn.dataset.sprite
    icon.setAttribute(
      'href',
      theme === 'dark'
        ? `${sprite}#icon-sun-regular`
        : `${sprite}#icon-moon-regular`
    )
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

  function collapseSidebar(btn){
    const sidebarId = btn.dataset.target;
    const sidebar = document.getElementById(sidebarId);
    const isCollapsed = sidebar.dataset.collapsed === 'true'
    sidebar.dataset.collapsed = isCollapsed ? 'false' : 'true'
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
  // Seleccionar una opción — usa delegación porque las opciones las inyecta HTMX
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

  // Actualizar valor del input-range
  function rangeUpdate(input, fill, thumb, output){
    const min = parseFloat(input.min) || 0
    const max = parseFloat(input.max) || 100
    const val = parseFloat(input.value)
    const pct = ((val - min) / (max - min)) * 100

    fill.style.width = `${pct}%`
    thumb.style.left = `${pct}%`
    if (output) output.value = val
  }

  // Toggle switch
  function toggleSwitch(btn) {
    const isChecked = btn.dataset.checked === 'true'
    btn.dataset.checked = isChecked ? 'false' : 'true'
  }

  // Modal
  function openModal(modalId) {
    const modal = document.getElementById(modalId)
    if (!modal) return
    modal.classList.remove('hidden')
    document.body.style.overflow = 'hidden'
  }
  function closeModal(modalId) {
    const modal = document.getElementById(modalId)
    if (!modal) return
    modal.classList.add('hidden')
    document.body.style.overflow = ''
  }

  // File picker
  function renderFileList(inputId, files) {
    const list = document.getElementById(`${inputId}-files`)
    if (!list) return
    list.innerHTML = ''
    Array.from(files).forEach(file => {
      const size = file.size < 1024 * 1024
        ? `${(file.size / 1024).toFixed(1)} KB`
        : `${(file.size / 1024 / 1024).toFixed(1)} MB`
      const li = document.createElement('li')
      li.className = 'file-item'
      li.innerHTML = `
        <svg class="w-4 h-4 text-fg-muted shrink-0"><use href="/static/sprite.svg#icon-file-regular"/></svg>
        <span class="file-item-name">${file.name}</span>
        <span class="file-item-size">${size}</span>
      `
      list.appendChild(li)
    })
  }
})