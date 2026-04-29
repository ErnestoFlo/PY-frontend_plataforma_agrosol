// login.js
(function () {
  console.log('Inicializando módulo de login (inactividad)');

  // Variables privadas del módulo
  const MINUTOS_INACTIVIDAD = 30;
  const SEGUNDOS_AVISO = 60;

  let timerInactividad;
  let timerCuentaRegresiva;
  let segundosRestantes = SEGUNDOS_AVISO;

  let modal, contador, barra;

  // Funciones privadas
  function reiniciarTimer() {
    clearTimeout(timerInactividad);

    if (!modal || modal.classList.contains('hidden')) {
      timerInactividad = setTimeout(() => {
        mostrarModal();
      }, MINUTOS_INACTIVIDAD * 60 * 1000);
    }
  }

  function mostrarModal() {
    if (!modal) return;

    document.querySelectorAll('.modal-overlay').forEach((overlay) => {
      if (overlay.id !== 'modal-inactivity' && !overlay.classList.contains('hidden')) {
        const content = overlay.querySelector('[id$="-content"]');
        if (content) content.innerHTML = '';
        overlay.classList.add('hidden');
      }
    });

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';

    segundosRestantes = SEGUNDOS_AVISO;

    if (contador) contador.textContent = segundosRestantes;
    if (barra) barra.style.width = '100%';

    timerCuentaRegresiva = setInterval(() => {
      segundosRestantes--;

      if (contador) contador.textContent = segundosRestantes;
      if (barra) barra.style.width = (segundosRestantes / SEGUNDOS_AVISO * 100) + '%';

      if (segundosRestantes <= 0) {
        clearInterval(timerCuentaRegresiva);
        cerrarSesionAhora();
      }
    }, 1000);
  }

  // Métodos públicos
  function continuarSesion() {
    clearInterval(timerCuentaRegresiva);
    modal?.classList.add('hidden');
    document.body.style.overflow = '';
    reiniciarTimer();
  }

  function cerrarSesionAhora() {
    clearInterval(timerCuentaRegresiva);
    clearTimeout(timerInactividad);
    document.getElementById('form-logout')?.submit();
  }

  function init() {
    modal    = document.getElementById('modal-inactivity');
    contador = document.getElementById('contador');
    barra    = document.getElementById('barra-progreso');

    ['mousemove','mousedown','keydown','touchstart','scroll','click']
      .forEach(e => document.addEventListener(e, reiniciarTimer, { passive: true }));

    reiniciarTimer();
  }

  // 🌍 API pública del módulo
  window.Login = {
    init,
    continuarSesion,
    cerrarSesionAhora
  };

})();