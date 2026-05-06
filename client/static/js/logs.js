// logs.js
(function () {
  console.log('Inicializando modulo de logs (filtros y otras utilidades)');

  document.querySelectorAll('[data-action="filtrarLogs"]').forEach(btn => {btn.addEventListener('click', (e) => window.Logs.filtrarLogs(btn.dataset.type))})
  document.querySelectorAll('[data-action="buscarLogs"]').forEach(input => {
    input.addEventListener('input', (e) => window.Logs.buscarLogs(e.currentTarget.value))
  })

  // Variables privadas
  let filtroActual = 'todos';

  // Métodos Privados
  function aplicarFiltros(q = '') {
    if (q === undefined) {
      const input = document.querySelector('input[data-action="buscarLogs"]');
      q = input?.value.toLowerCase() || '';
    }

    let visibles = 0;

    document.querySelectorAll('.log-row').forEach(row => {
      const tipoOk = filtroActual === 'todos' || row.dataset.tipo === filtroActual;

      const texto = row.dataset.texto.toLowerCase();
      const textoOk = !q || texto.includes(q);

      if (tipoOk && textoOk) {
        row.classList.remove('hidden');
        visibles++;
      } else {
        row.classList.add('hidden');
      }
    });
    const info = document.getElementById('logs-info');
    if (info) {
      const total = document.querySelectorAll('.log-row').length;
      info.textContent = visibles === total
        ? `${total} registro${total !== 1 ? 's' : ''}`
        : `${visibles} de ${total} registros`;
    }
  }

  // Metodos Públicos
  function filtrarLogs(tipo) {
    filtroActual = tipo;
    document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('filtro-activo'));
    document.getElementById('f-' + tipo)?.classList.add('filtro-activo');
    aplicarFiltros();
  }

  function buscarLogs(q) {
    aplicarFiltros(q.toLowerCase());
  }

  window.Logs = {
    filtrarLogs,
    buscarLogs
  };

})();