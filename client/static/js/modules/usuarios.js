(function() {
  document.addEventListener('DOMContentLoaded', () => {
    const CSRF = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

    // ── BÚSQUEDA DE USUARIOS ──
    document.querySelector('[data-action="buscarUsuarios"]').addEventListener('input', function() {
      const q    = this.value.toLowerCase();
      const fila = document.querySelectorAll('.fila');
      let n = 0;
      fila.forEach(f => {
        const ok = f.textContent.toLowerCase().includes(q);
        f.style.display = ok ? '' : 'none';
        if (ok) n++;
      });
      const total = fila.length;
      document.getElementById('info-resultado').textContent = q
        ? `${n} resultado${n !== 1 ? 's' : ''} para "${this.value}"`
        : `${total} usuario${total !== 1 ? 's' : ''} en total`;
    });
  })


  // ── CREAR USUARIO ──
  async function crearUsuario() {
    ocultarError();
    const username  = document.getElementById('f-username').value.trim();
    const password1 = document.getElementById('f-password1').value;
    const password2 = document.getElementById('f-password2').value;

    if (!username)          { window.AlertManager.detailedWarning("Campo 'Nombre de Usuario'", 'El username es obligatorio.');          return; }
    if (!password1)         { window.AlertManager.detailedWarning("Campo 'Contraseña'", 'La contraseña es obligatoria.');        return; }
    if (password1.length < 8){ window.AlertManager.detailedWarning("Campo 'Contraseña'", 'La contraseña debe tener mínimo 8 caracteres.'); return; }
    if (password1 !== password2){ window.AlertManager.detailedWarning("Campo 'Contraseña'", 'Las contraseñas no coinciden.');    return; }

    const btn = document.getElementById('btn-guardar-usuario');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Creando...';

    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', CSRF);
    fd.append('username',     username);
    fd.append('first_name',   document.getElementById('f-first_name').value.trim());
    fd.append('last_name',    document.getElementById('f-last_name').value.trim());
    fd.append('email',        document.getElementById('f-email').value.trim());
    fd.append('password1',    password1);
    fd.append('password2',    password2);
    fd.append('cargo',        document.getElementById('f-cargo').value.trim());
    fd.append('area',         document.getElementById('f-area').value.trim());
    fd.append('telefono',     document.getElementById('f-telefono').value.trim());
    fd.append('is_staff',     document.getElementById('f-is_staff').checked     ? '1' : '0');
    fd.append('is_superuser', document.getElementById('f-is_superuser').checked ? '1' : '0');
    fd.append('grupo',        document.getElementById('f-grupo').value);
    const avatarFile = document.getElementById('f-avatar').files[0];
    if (avatarFile) fd.append('avatar', avatarFile);

    try {
      const res  = await fetch("agrosol/usuarios/crear", { method: 'POST', body: fd });
      const json = await res.json();

      if (!json.success) {
        mostrarError(json.error || 'Error al crear el usuario.');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Crear Usuario';
        return;
      }

      // Cerrar modal y agregar fila
      bootstrap.Modal.getInstance(document.getElementById('modal-crear-usuario')).hide();
      agregarFilaTabla(json.usuario);

      // Actualizar stat
      const s = document.getElementById('stat-total');
      if (s) s.textContent = parseInt(s.textContent) + 1;

    } catch(e) {
      mostrarError('Error de conexión. Intenta de nuevo.');
      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Crear Usuario';
    }
  }

})();