(function() {
    const CSRF = window.APP.csrf;
    const url = window.APP.urls;

    let gId = null, gNombre = '';

    // DATOS DESDE DJANGO
    const USUARIOS = JSON.parse(document.getElementById('todos-usuarios-data').textContent)
    const MODULOS = JSON.parse(document.getElementById('modulos-data').textContent)

    // ── TABS ──
    function switchTab(t){
      document.querySelectorAll('.tab-pane').forEach(p=>p.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
      document.getElementById(`tab-${t}`).classList.add('active');
      document.getElementById(`tab-btn-${t}`).classList.add('active');
    }

    // ════════════ GRUPOS ════════════
    async function crearGrupo(){
      const input=document.getElementById('nuevo-grupo-nombre');
      const nombre=input.value.trim();
      if(!nombre){window.AlertManager.danger('Escribe un nombre.');return;}
      const btn=document.getElementById('btn-crear-grupo');
      btn.disabled=true; btn.innerHTML='<span class="spinner-border spinner-border-sm me-1"></span>Creando...';
      const fd=new FormData(); fd.append('nombre',nombre); fd.append('csrfmiddlewaretoken',CSRF);
      const res=await fetch(url.grupoCrear,{method:'POST',body:fd});
      const json=await res.json();
      btn.disabled=false; btn.innerHTML='<i class="bi bi-plus-lg"></i>Crear Grupo';
      if(!json.success){window.AlertManager.danger(json.error||'Error.');return;}
      input.value='';
      document.getElementById('empty-grupos')?.remove();
      insertarTarjetaGrupo(json.grupo);
      const s=document.getElementById('stat-grupos'); if(s) s.textContent=parseInt(s.textContent)+1;
      window.AlertManager.success(`Grupo "${json.grupo.name}" creado.`);
    }

    function insertarTarjetaGrupo(g){
      const d=document.createElement('div');
      d.className='grupo-card item-new'; d.id=`grupo-card-${g.id}`;
      d.innerHTML=`
        <div class="grupo-header">
          <div>
            <p style="font-weight:800;font-size:.98rem;margin:0;"><i class="bi bi-people me-1" style="color:var(--verde);"></i>${g.name}</p>
            <p style="font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);margin:.2rem 0 0;" id="grupo-meta-${g.id}">0 usuarios · 0 módulos</p>
          </div>
          <div style="display:flex;gap:.5rem;flex-shrink:0;flex-wrap:wrap;">
            <button class="btn-outline naranja" onclick="abrirModalModulos(${g.id},'${g.name}')"><i class="bi bi-collection"></i>Módulos</button>
            <button class="btn-outline" onclick="abrirModalUsuarios(${g.id},'${g.name}')"><i class="bi bi-person-plus"></i>Usuarios</button>
            <button class="btn-icon-sm rem" onclick="eliminarGrupo(${g.id},'${g.name}')"><i class="bi bi-trash3"></i></button>
          </div>
        </div>
        <div class="grupo-body">
          <p class="subsection"><i class="bi bi-collection"></i>Módulos con acceso</p>
          <div id="modulos-grupo-${g.id}" style="margin-bottom:.85rem;">
            <p style="font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);" id="empty-modulos-${g.id}">Sin módulos asignados</p>
          </div>
          <p class="subsection"><i class="bi bi-people"></i>Usuarios</p>
          <div id="usuarios-grupo-${g.id}">
            <p style="font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);" id="empty-usuarios-${g.id}">Sin usuarios asignados</p>
          </div>
        </div>`;
      document.getElementById('lista-grupos').prepend(d);
    }

    async function eliminarGrupo(id,nombre){
      if(!confirm(`¿Eliminar el grupo "${nombre}"?`)) return;
      const fd=new FormData(); fd.append('csrfmiddlewaretoken',CSRF);
      const url=url.grupoEliminar.replace('/0/',`/${id}/`);
      const res=await fetch(url,{method:'POST',body:fd}); const json=await res.json();
      if(!json.success){window.AlertManager.danger('Error.');return;}
      document.getElementById(`grupo-card-${id}`)?.remove();
      const s=document.getElementById('stat-grupos'); if(s) s.textContent=Math.max(0,parseInt(s.textContent)-1);
      window.AlertManager.danger(`Grupo "${nombre}" eliminado.`);
    }

    // ── MODAL USUARIOS ──
    function abrirModalUsuarios(id,nombre){
      gId=id; gNombre=nombre;
      document.getElementById('modal-u-nombre').textContent=nombre;
      document.getElementById('search-u').value='';
      renderUsuarios('');
      new bootstrap.Modal(document.getElementById('modal-usuarios')).show();
    }

    function renderUsuarios(q){
      const cont=document.getElementById('lista-u-modal');
      const lista=USUARIOS.filter(u=>!u.grupos.includes(gId)&&(u.nombre.toLowerCase().includes(q.toLowerCase())||u.username.toLowerCase().includes(q.toLowerCase())||u.cargo.toLowerCase().includes(q.toLowerCase())));
      if(!lista.length){cont.innerHTML=`<p style="font-family:'DM Mono',monospace;font-size:.75rem;color:var(--muted);text-align:center;padding:1.5rem 0;">${q?'Sin resultados':'Todos ya están en este grupo'}</p>`;return;}
      cont.innerHTML=lista.map(u=>`
        <div class="item-row" id="modal-u-${u.id}">
          <div class="d-flex align-items-center gap-2">
            <div class="u-avatar">${u.avatar?`<img src="${u.avatar}" alt="">`:(u.nombre[0]||'?').toUpperCase()}</div>
            <div>
              <p style="font-weight:700;font-size:.88rem;margin:0;">${u.nombre}</p>
              <p style="font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);margin:0;">
                @${u.username}${u.cargo?' · '+u.cargo:''}
                ${u.grupo_actual?`<span style="color:var(--amarillo);margin-left:.35rem;"><i class="bi bi-people-fill"></i> ${u.grupo_actual}</span>`:''}
              </p>
            </div>
          </div>
          <button class="btn-add ${u.grupo_actual?'':''}${u.grupo_actual?'':'naranja'}" style="${u.grupo_actual?'background:rgba(251,191,36,.1);color:var(--amarillo);border-color:rgba(251,191,36,.25);':''}" onclick="asignarU(${u.id},'${u.nombre}')">
            ${u.grupo_actual?'<i class="bi bi-arrow-left-right me-1"></i>Mover':'<i class="bi bi-plus me-1"></i>Agregar'}
          </button>
        </div>`).join('');
    }

    async function asignarU(uid,unombre){
      const fd=new FormData(); fd.append('user_id',uid); fd.append('accion','agregar'); fd.append('csrfmiddlewaretoken',CSRF);
      const url=url.grupoAsignarUsuario.replace('/0/',`/${gId}/`);
      const res=await fetch(url,{method:'POST',body:fd}); const json=await res.json();
      if(!json.success){window.AlertManager.danger('Error.');return;}
      const u=USUARIOS.find(u=>u.id===uid); if(u) u.grupos.push(gId);
      document.getElementById(`modal-u-${uid}`)?.remove();
      addChipU(gId,json.usuario);
      metaGrupo(gId); stats();
      renderUsuarios(document.getElementById('search-u').value);
      const grupoAnt = json.grupo_anterior;
      window.AlertManager.danger(grupoAnt ? `${unombre} movido de "${grupoAnt}" a "${gNombre}".` : `${unombre} agregado a ${gNombre}.`);
    }

    function addChipU(gid,u){
      const cont=document.getElementById(`usuarios-grupo-${gid}`);
      document.getElementById(`empty-usuarios-${gid}`)?.remove();
      const us=USUARIOS.find(x=>x.id===u.id);
      const chip=document.createElement('span');
      chip.className='user-chip item-new'; chip.id=`chip-${gid}-${u.id}`;
      chip.innerHTML=`<div class="user-chip-avatar">${us?.avatar?`<img src="${us.avatar}" alt="">`:(u.nombre[0]||'?').toUpperCase()}</div>${u.nombre}<button class="user-chip-remove" onclick="quitarUsuario(${gid},${u.id},'${u.nombre}')"><i class="bi bi-x"></i></button>`;
      cont.appendChild(chip);
    }

    async function quitarUsuario(gid,uid,nombre){
      const fd=new FormData(); fd.append('user_id',uid); fd.append('accion','quitar'); fd.append('csrfmiddlewaretoken',CSRF);
      const url=url.grupoAsignarUsuario.replace('/0/',`/${gid}/`);
      const res=await fetch(url,{method:'POST',body:fd}); const json=await res.json();
      if(!json.success){window.AlertManager.danger('Error.');return;}
      const u=USUARIOS.find(u=>u.id===uid); if(u) u.grupos=u.grupos.filter(g=>g!==gid);
      document.getElementById(`chip-${gid}-${uid}`)?.remove();
      const cont=document.getElementById(`usuarios-grupo-${gid}`);
      if(cont&&!cont.querySelector('.user-chip')){
        const p=document.createElement('p'); p.id=`empty-usuarios-${gid}`;
        p.style.cssText="font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);";
        p.textContent='Sin usuarios asignados'; cont.appendChild(p);
      }
      metaGrupo(gid); stats(); window.AlertManager.warning(`${nombre} removido.`);
    }

    // ── MODAL MÓDULOS ──
    function abrirModalModulos(id,nombre){
      gId=id; gNombre=nombre;
      document.getElementById('modal-m-nombre').textContent=nombre;
      renderModulos();
      new bootstrap.Modal(document.getElementById('modal-modulos')).show();
    }

    function renderModulos(){
      const cont=document.getElementById('lista-m-modal');
      if(!MODULOS.length){cont.innerHTML=`<p style="font-family:'DM Mono',monospace;font-size:.75rem;color:var(--muted);text-align:center;padding:1.5rem 0;">No hay módulos. Créalos en el tab Módulos.</p>`;return;}
      cont.innerHTML=MODULOS.map(m=>{
        const tiene=m.grupos.includes(gId);
        const nElems = m.elementos ? m.elementos.length : 0;
        return `
          <div class="item-row" id="modal-m-${m.id}">
            <div class="d-flex align-items-center gap-2" style="flex:1;min-width:0;">
              <div class="modulo-icon" style="width:34px;height:34px;border-radius:8px;flex-shrink:0;"><i class="bi ${m.icono}"></i></div>
              <div style="min-width:0;">
                <p style="font-weight:700;font-size:.88rem;margin:0;">${m.nombre}</p>
                <p style="font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);margin:0;">
                  ${tiene
                    ? '<span style="color:var(--verde);"><i class="bi bi-check-circle-fill me-1"></i>Con acceso</span>'
                    : 'Sin acceso'}
                  ${nElems ? `<span style="margin-left:.4rem;color:var(--azul);">${nElems} elem.</span>` : ''}
                </p>
              </div>
            </div>
            <div style="display:flex;gap:.35rem;flex-shrink:0;">
              ${tiene && nElems ? `
                <button class="btn-add" style="background:rgba(96,165,250,.1);color:var(--azul);border-color:rgba(96,165,250,.25);"
                        onclick="abrirPermisosElementos(${m.id},'${m.nombre}','${m.icono}')">
                  <i class="bi bi-sliders me-1"></i>Permisos
                </button>` : ''}
              ${tiene
                ?`<button class="btn-outline danger" style="font-size:.75rem;padding:.28rem .7rem;" onclick="revocarM(${m.id},'${m.nombre}','${m.icono}')"><i class="bi bi-x me-1"></i>Revocar</button>`
                :`<button class="btn-add naranja" onclick="asignarM(${m.id},'${m.nombre}','${m.icono}')"><i class="bi bi-plus me-1"></i>Asignar</button>`
              }
            </div>
          </div>`;
      }).join('');;
    }

    async function asignarM(mid,mnombre,micono){
      const fd=new FormData(); fd.append('modulo_id',mid); fd.append('accion','asignar'); fd.append('csrfmiddlewaretoken',CSRF);
      const url=url.grupoGestionarModulo.replace('/0/',`/${gId}/`);
      const res=await fetch(url,{method:'POST',body:fd}); const json=await res.json();
      if(!json.success){window.AlertManager.danger(json.error||'Error.');return;}
      const m=MODULOS.find(m=>m.id===mid); if(m) m.grupos.push(gId);
      renderModulos();
      addChipModulo(gId,mid,mnombre,micono);
      addBadgeGrupoEnModulo(mid,gId,gNombre);
      metaGrupo(gId);
      window.AlertManager.danger(`Acceso a "${mnombre}" concedido.`);
    }

    async function revocarM(mid,mnombre,micono){
      const fd=new FormData(); fd.append('modulo_id',mid); fd.append('accion','revocar'); fd.append('csrfmiddlewaretoken',CSRF);
      const url=url.grupoGestionarModulo.replace('/0/',`/${gId}/`);
      const res=await fetch(url,{method:'POST',body:fd}); const json=await res.json();
      if(!json.success){window.AlertManager.danger('Error.');return;}
      const m=MODULOS.find(m=>m.id===mid); if(m) m.grupos=m.grupos.filter(g=>g!==gId);
      renderModulos();
      document.getElementById(`acceso-chip-${gId}-${mid}`)?.remove();
      const cont=document.getElementById(`modulos-grupo-${gId}`);
      if(cont&&!cont.querySelector('.acceso-chip')){
        const p=document.createElement('p'); p.id=`empty-modulos-${gId}`;
        p.style.cssText="font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);";
        p.textContent='Sin módulos asignados'; cont.appendChild(p);
      }
      removeBadgeGrupoEnModulo(mid,gId);
      metaGrupo(gId);
      window.AlertManager.warning(`Acceso a "${mnombre}" revocado.`);
    }

    async function revocarModulo(gid,mid,mnombre){
      gId=gid;
      await revocarM(mid,mnombre,'');
    }

    function addChipModulo(gid,mid,mnombre,micono){
      const cont=document.getElementById(`modulos-grupo-${gid}`);
      document.getElementById(`empty-modulos-${gid}`)?.remove();
      const chip=document.createElement('span');
      chip.className='acceso-chip item-new'; chip.id=`acceso-chip-${gid}-${mid}`;
      chip.innerHTML=`<i class="bi ${micono}"></i>${mnombre}<button class="acceso-chip-remove" onclick="revocarModulo(${gid},${mid},'${mnombre}')"><i class="bi bi-x"></i></button>`;
      cont.appendChild(chip);
    }

    function addBadgeGrupoEnModulo(mid,gid,gnombre){
      const cont=document.getElementById(`grupos-modulo-${mid}`);
      if(!cont) return;
      document.getElementById(`empty-gmod-${mid}`)?.remove();
      const span=document.createElement('span');
      span.className='badge-grupo-asignado item-new'; span.id=`badge-gmod-${mid}-${gid}`;
      span.innerHTML=`<i class="bi bi-people"></i>${gnombre}`;
      cont.appendChild(span);
    }

    function removeBadgeGrupoEnModulo(mid,gid){
      document.getElementById(`badge-gmod-${mid}-${gid}`)?.remove();
      const cont=document.getElementById(`grupos-modulo-${mid}`);
      if(cont&&!cont.querySelector('.badge-grupo-asignado')){
        const p=document.createElement('p'); p.id=`empty-gmod-${mid}`;
        p.style.cssText="font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);";
        p.textContent='Ningún grupo tiene acceso todavía'; cont.appendChild(p);
      }
    }

    // ════════════ MÓDULOS ════════════
    async function crearModulo(){
      const nombre=document.getElementById('mod-nombre').value.trim();
      const icono=document.getElementById('mod-icono').value.trim()||'bi-grid';
      const url_name=document.getElementById('mod-urlname').value.trim();
      const desc=document.getElementById('mod-descripcion').value.trim();
      if(!nombre){window.AlertManager.danger('Escribe un nombre.');return;}
      const btn=document.getElementById('btn-crear-modulo');
      btn.disabled=true; btn.innerHTML='<span class="spinner-border spinner-border-sm me-1"></span>Creando...';
      const fd=new FormData();
      fd.append('nombre',nombre); fd.append('icono',icono); fd.append('url_name',url_name);
      fd.append('descripcion',desc); fd.append('csrfmiddlewaretoken',CSRF);
      const res=await fetch(url.moduloCrear,{method:'POST',body:fd}); const json=await res.json();
      btn.disabled=false; btn.innerHTML='<i class="bi bi-plus-lg"></i>Crear Módulo';
      if(!json.success){window.AlertManager.danger(json.error||'Error.');return;}
      document.getElementById('mod-nombre').value='';
      document.getElementById('mod-urlname').value='';
      document.getElementById('mod-descripcion').value='';
      document.getElementById('empty-modulos')?.remove();
      insertarTarjetaModulo(json.modulo);
      MODULOS.push({id:json.modulo.id,nombre:json.modulo.nombre,icono:json.modulo.icono,grupos:[]});
      const s=document.getElementById('stat-modulos'); if(s) s.textContent=parseInt(s.textContent)+1;
      window.AlertManager.success(`Módulo "${json.modulo.nombre}" creado.`);
    }

    function insertarTarjetaModulo(m){
      const d=document.createElement('div');
      d.className='modulo-card item-new'; d.id=`modulo-card-${m.id}`;
      d.innerHTML=`
        <div class="modulo-header">
          <div style="display:flex;align-items:center;gap:.85rem;">
            <div class="modulo-icon"><i class="bi ${m.icono}"></i></div>
            <div>
              <p style="font-weight:800;font-size:.98rem;margin:0;">${m.nombre}</p>
              <p style="font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);margin:.1rem 0 0;">
                ${m.slug}${m.url_name?' · <span style="color:var(--azul);">'+m.url_name+'</span>':''}
              </p>
            </div>
          </div>
          <button class="btn-icon-sm rem" onclick="eliminarModulo(${m.id},'${m.nombre}')"><i class="bi bi-trash3"></i></button>
        </div>
        <div class="modulo-body">
          ${m.descripcion?`<p style="font-size:.83rem;color:var(--muted);margin-bottom:.6rem;">${m.descripcion}</p>`:''}
          <p class="subsection"><i class="bi bi-people"></i>Grupos con acceso</p>
          <div id="grupos-modulo-${m.id}">
            <p style="font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);" id="empty-gmod-${m.id}">Ningún grupo tiene acceso todavía</p>
          </div>
        </div>`;
      document.getElementById('lista-modulos').prepend(d);
    }

    async function eliminarModulo(id,nombre){
      if(!confirm(`¿Eliminar el módulo "${nombre}"?`)) return;
      const fd=new FormData(); fd.append('csrfmiddlewaretoken',CSRF);
      const url=url.moduloEliminar.replace('/0/',`/${id}/`);
      const res=await fetch(url,{method:'POST',body:fd}); const json=await res.json();
      if(!json.success){window.AlertManager.danger('Error.');return;}
      document.getElementById(`modulo-card-${id}`)?.remove();
      const idx=MODULOS.findIndex(m=>m.id===id); if(idx>-1) MODULOS.splice(idx,1);
      const s=document.getElementById('stat-modulos'); if(s) s.textContent=Math.max(0,parseInt(s.textContent)-1);
      window.AlertManager.danger(`Módulo "${nombre}" eliminado.`);
    }

    // ── HELPERS ──
    function metaGrupo(gid){
      const meta=document.getElementById(`grupo-meta-${gid}`); if(!meta) return;
      const nU=document.getElementById(`usuarios-grupo-${gid}`)?.querySelectorAll('.user-chip').length||0;
      const nM=document.getElementById(`modulos-grupo-${gid}`)?.querySelectorAll('.acceso-chip').length||0;
      meta.textContent=`${nU} usuario${nU!==1?'s':''} · ${nM} módulo${nM!==1?'s':''}`;
    }

    function stats(){
      let a=0,s=0; USUARIOS.forEach(u=>{if(u.grupos.length>0)a++;else s++;});
      const sA=document.getElementById('stat-asignados'),sS=document.getElementById('stat-sin-grupo');
      if(sA) sA.textContent=a; if(sS) sS.textContent=s;
    }


    // ════════════════════════════════════════════════════════
    //  FASE 2 — ESCANEO Y PERMISOS DE ELEMENTOS
    // ════════════════════════════════════════════════════════

    let moduloActivoId     = null;
    let moduloActivoNombre = '';
    let moduloActivoIcono  = '';

    // ── Escanear template de un módulo ──────────────────────
    async function escanearModulo(mid, mnombre) {
      if (!confirm(`Escanear el template de "${mnombre}"?\n\nSe detectarán automáticamente todos los elementos con data-permiso.`)) return;

      window.AlertManager.info(`Escaneando "${mnombre}"...`);

      const fd = new FormData();
      fd.append('csrfmiddlewaretoken', CSRF);
      const url = url.moduloEscanear.replace('/0/', `/${mid}/`);
      const res  = await fetch(url, { method: 'POST', body: fd });
      const json = await res.json();

      if (!json.success) {
        window.AlertManager.danger(json.error || 'Error al escanear.');
        return;
      }

      const n = json.creados.length;
      const e = json.existentes.length;
      window.AlertManager.info(`"${mnombre}": ${n} nuevo${n!==1?'s':''}, ${e} ya existía${e!==1?'n':''}.`);

      // Actualizar el botón de elementos en la tarjeta
      const btnEl = document.getElementById(`btn-elementos-${mid}`);
      if (btnEl) {
        const total = json.total;
        btnEl.innerHTML = `<i class="bi bi-list-check"></i><span style="font-size:.55rem;margin-left:.1rem;">${total}</span>`;
        btnEl.style.color = 'var(--verde)';
        btnEl.style.borderColor = 'rgba(74,222,128,.3)';
      }

      // Actualizar MODULOS en memoria
      const m = MODULOS.find(m => m.id === mid);
      if (m) m.elementos = json.elementos;

      setTimeout(() => location.reload(), 1200);
    }

    // ── Ver lista de elementos de un módulo ─────────────────
    async function verElementos(mid, mnombre) {
      document.getElementById('modal-elem-nombre').textContent = mnombre;
      const cont = document.getElementById('lista-elementos-modal');
      cont.innerHTML = '<div style="text-align:center;padding:1.5rem;color:var(--muted);"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</div>';
      new bootstrap.Modal(document.getElementById('modal-elementos')).show();

      const url = url.moduloElementos.replace('/0/', `/${mid}/`);
      const res  = await fetch(url);
      const json = await res.json();

      if (!json.success || !json.elementos.length) {
        cont.innerHTML = `<p style="font-family:'DM Mono',monospace;font-size:.75rem;color:var(--muted);text-align:center;padding:1.5rem;">Sin elementos detectados. Usa el botón escanear.</p>`;
        return;
      }

      // Agrupar por tipo
      const grupos = { accion: [], componente: [], dato: [] };
      json.elementos.forEach(e => grupos[e.tipo]?.push(e));

      const tipoInfo = {
        accion:     { icono: 'bi-lightning-fill', color: 'var(--naranja)', label: 'Acciones' },
        componente: { icono: 'bi-puzzle',         color: 'var(--azul)',    label: 'Componentes' },
        dato:       { icono: 'bi-table',          color: 'var(--verde)',   label: 'Datos' },
      };

      cont.innerHTML = Object.entries(grupos).map(([tipo, elems]) => {
        if (!elems.length) return '';
        const info = tipoInfo[tipo];
        return `
          <div style="margin-bottom:1rem;">
            <p style="font-family:'DM Mono',monospace;font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:${info.color};margin-bottom:.5rem;">
              <i class="bi ${info.icono} me-1"></i>${info.label} (${elems.length})
            </p>
            ${elems.map(e => `
              <div style="display:flex;align-items:center;gap:.6rem;padding:.4rem 0;border-bottom:1px solid var(--borde);">
                <span style="font-family:'DM Mono',monospace;font-size:.7rem;color:${info.color};min-width:140px;">${e.clave}</span>
                <span style="font-size:.83rem;font-weight:600;">${e.label}</span>
              </div>`).join('')}
          </div>`;
      }).join('');
    }

    // ── Abrir panel de permisos de elementos para un módulo ─
    async function abrirPermisosElementos(mid, mnombre, micono) {
      moduloActivoId     = mid;
      moduloActivoNombre = mnombre;
      moduloActivoIcono  = micono;

      document.getElementById('perm-modulo-nombre').textContent = mnombre;
      document.getElementById('perm-grupo-nombre').textContent  = gNombre;
      document.getElementById('perm-modulo-icon').innerHTML     = `<i class="bi ${micono}"></i>`;

      // Mostrar panel de permisos, ocultar lista de módulos
      document.getElementById('panel-lista-modulos').style.display    = 'none';
      document.getElementById('panel-permisos-elementos').style.display = 'block';

      // Cargar elementos con sus permisos actuales para este grupo
      await cargarPermisosElementos(mid);
    }

    async function cargarPermisosElementos(mid) {
      const cont = document.getElementById('lista-permisos-elementos');
      cont.innerHTML = '<div style="text-align:center;padding:2rem;color:var(--muted);"><span class="spinner-border spinner-border-sm me-2"></span>Cargando...</div>';

      const url = url.moduloElementos.replace('/0/', `/${mid}/`) + `?grupo_id=${gId}`;
      const res  = await fetch(url);
      const json = await res.json();

      if (!json.success || !json.elementos.length) {
        cont.innerHTML = `
          <div style="text-align:center;padding:2rem;color:var(--muted);">
            <i class="bi bi-puzzle" style="font-size:1.8rem;display:block;margin-bottom:.5rem;"></i>
            <p style="font-weight:700;">Sin elementos detectados</p>
            <p style="font-size:.82rem;">Primero escanea el template desde el tab Módulos</p>
          </div>`;
        return;
      }

      // Agrupar por tipo
      const grupos = { accion: [], componente: [], dato: [] };
      json.elementos.forEach(e => grupos[e.tipo]?.push(e));

      const tipoInfo = {
        accion:     { icono: 'bi-lightning-fill', color: 'var(--naranja)', label: 'Acciones',    dimColor: 'rgba(251,146,60,.08)',   borderColor: 'rgba(251,146,60,.2)' },
        componente: { icono: 'bi-puzzle',         color: 'var(--azul)',    label: 'Componentes', dimColor: 'rgba(96,165,250,.08)',   borderColor: 'rgba(96,165,250,.2)' },
        dato:       { icono: 'bi-table',          color: 'var(--verde)',   label: 'Datos',       dimColor: 'rgba(74,222,128,.08)',   borderColor: 'rgba(74,222,128,.2)' },
      };

      cont.innerHTML = Object.entries(grupos).map(([tipo, elems]) => {
        if (!elems.length) return '';
        const info = tipoInfo[tipo];
        return `
          <div style="margin-bottom:1.25rem;">
            <p style="font-family:'DM Mono',monospace;font-size:.65rem;text-transform:uppercase;letter-spacing:.1em;color:${info.color};margin-bottom:.6rem;display:flex;align-items:center;gap:.4rem;">
              <i class="bi ${info.icono}"></i>${info.label} (${elems.length})
            </p>
            ${elems.map(e => `
              <div style="display:flex;align-items:center;justify-content:space-between;padding:.6rem .75rem;border-radius:8px;background:${info.dimColor};border:1px solid ${info.borderColor};margin-bottom:.35rem;" id="perm-row-${e.id}">
                <span style="font-size:.86rem;font-weight:600;">${e.label}</span>
                <div style="display:flex;gap:.75rem;align-items:center;">
                  ${tipo !== 'dato' ? `
                  <!-- Toggle USAR -->
                  <div style="display:flex;align-items:center;gap:.4rem;">
                    <span style="font-family:'DM Mono',monospace;font-size:.62rem;color:var(--muted);">USAR</span>
                    <label class="toggle-switch" title="Puede usar (interactuar)">
                      <input type="checkbox" ${e.usar ? 'checked' : ''}
                             onchange="guardarPermiso(${e.id}, 'usar', this.checked, ${e.usar}, ${e.ver})">
                      <span class="toggle-slider" style="${e.usar?'background:rgba(74,222,128,.2);border-color:var(--verde);':''}"></span>
                    </label>
                  </div>` : ''}
                  <!-- Toggle VER -->
                  <div style="display:flex;align-items:center;gap:.4rem;">
                    <span style="font-family:'DM Mono',monospace;font-size:.62rem;color:var(--muted);">VER</span>
                    <label class="toggle-switch" title="Puede ver (existe en el DOM)">
                      <input type="checkbox" ${e.ver ? 'checked' : ''}
                             onchange="guardarPermiso(${e.id}, 'ver', this.checked, ${e.usar}, ${e.ver})">
                      <span class="toggle-slider" style="${e.ver?'background:rgba(74,222,128,.2);border-color:var(--verde);':''}"></span>
                    </label>
                  </div>
                </div>
              </div>`).join('')}
          </div>`;
      }).join('');
    }

    function volverAModulos() {
      document.getElementById('panel-permisos-elementos').style.display = 'none';
      document.getElementById('panel-lista-modulos').style.display      = 'block';
    }

    // ── Guardar un permiso individual ────────────────────────
    async function guardarPermiso(elemId, campo, valor, usarActual, verActual) {
      // Lógica: si activas USAR → VER se activa también
      //         si desactivas VER → USAR se desactiva también
      let nuevoVer  = campo === 'ver'  ? valor : verActual;
      let nuevoUsar = campo === 'usar' ? valor : usarActual;

      if (campo === 'usar' && valor === true)  nuevoVer  = true;
      if (campo === 'ver'  && valor === false) nuevoUsar = false;

      const fd = new FormData();
      fd.append('puede_ver',  nuevoVer  ? 'true' : 'false');
      fd.append('puede_usar', nuevoUsar ? 'true' : 'false');
      fd.append('csrfmiddlewaretoken', CSRF);

      const url = url.guardarPermisoElemento.replace('/0/elementos/0/', `/${gId}/elementos/${elemId}/`);
      const res  = await fetch(url, { method: 'POST', body: fd });
      const json = await res.json();

      if (!json.success) { window.AlertManager.danger('Error al guardar.'); return; }

      // ── Actualizar los toggles en el DOM sin re-renderizar ──
      // Esto evita el scroll al inicio y la experiencia de "parpadeo"
      const row = document.getElementById(`perm-row-${elemId}`);
      if (row) {
        const checkboxes = row.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
          const onchangeAttr = cb.getAttribute('onchange') || '';
          if (onchangeAttr.includes("'ver'")) {
            cb.checked = json.puede_ver;
            // Actualizar el slider visual
            const slider = cb.nextElementSibling;
            if (slider) {
              slider.style.background    = json.puede_ver ? 'rgba(74,222,128,.2)' : '';
              slider.style.borderColor   = json.puede_ver ? 'var(--verde)' : '';
            }
          }
          if (onchangeAttr.includes("'usar'")) {
            cb.checked = json.puede_usar;
            const slider = cb.nextElementSibling;
            if (slider) {
              slider.style.background    = json.puede_usar ? 'rgba(74,222,128,.2)' : '';
              slider.style.borderColor   = json.puede_usar ? 'var(--verde)' : '';
            }
          }
        });

        // Actualizar los valores en los atributos onchange para la próxima llamada
        checkboxes.forEach(cb => {
          const attr = cb.getAttribute('onchange') || '';
          // Reemplazar los valores de usarActual y verActual en el onchange
          const newAttr = attr.replace(
            /guardarPermiso\((\d+), '(\w+)', this\.checked, (true|false), (true|false)\)/,
            (match, id, c2, u, v) => {
              const newU = c2 === 'usar' ? String(json.puede_usar) : String(json.puede_usar);
              const newV = c2 === 'ver'  ? String(json.puede_ver)  : String(json.puede_ver);
              return `guardarPermiso(${id}, '${c2}', this.checked, ${newU}, ${newV})`;
            }
          );
          cb.setAttribute('onchange', newAttr);
        });
      }

      window.AlertManager.success(`"${json.elemento}" actualizado.`);
    }

    // Enter
    document.getElementById('nuevo-grupo-nombre').addEventListener('keydown',e=>{if(e.key==='Enter')crearGrupo();});
    document.getElementById('mod-nombre').addEventListener('keydown',e=>{if(e.key==='Enter')crearModulo();});

    // ════════════ EDITAR MÓDULO ════════════
    function abrirEditarModulo(id, nombre, icono, urlname, desc) {
      document.getElementById('edit-id').value          = id;
      document.getElementById('edit-nombre').value      = nombre;
      document.getElementById('edit-icono').value       = icono;
      document.getElementById('edit-urlname').value     = urlname;
      document.getElementById('edit-descripcion').value = desc;
      document.getElementById('edit-icon-prev').className = `bi ${icono}`;
      ocultarEditError();
      new bootstrap.Modal(document.getElementById('modal-editar-modulo')).show();
    }

    function ocultarEditError() {
      document.getElementById('edit-error').style.display = 'none';
    }

    function mostrarEditError(msg) {
      const el = document.getElementById('edit-error');
      document.getElementById('edit-error-msg').textContent = msg;
      el.style.display = 'flex';
    }

    async function guardarEdicionModulo() {
      const id          = document.getElementById('edit-id').value;
      const nombre      = document.getElementById('edit-nombre').value.trim();
      const icono       = document.getElementById('edit-icono').value.trim() || 'bi-grid';
      const url_name    = document.getElementById('edit-urlname').value.trim();
      const descripcion = document.getElementById('edit-descripcion').value.trim();

      if (!nombre) { mostrarEditError('El nombre es requerido.'); return; }

      const btn = document.getElementById('btn-guardar-edicion');
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Guardando...';

      const fd = new FormData();
      fd.append('nombre',      nombre);
      fd.append('icono',       icono);
      fd.append('url_name',    url_name);
      fd.append('descripcion', descripcion);
      fd.append('csrfmiddlewaretoken', CSRF);

      const url = url.moduloEditar.replace('/0/', `/${id}/`);
      const res  = await fetch(url, { method: 'POST', body: fd });
      const json = await res.json();

      btn.disabled = false;
      btn.innerHTML = '<i class="bi bi-check2 me-1"></i>Guardar Cambios';

      if (!json.success) { mostrarEditError(json.error || 'Error al guardar.'); return; }

      // Cerrar modal
      bootstrap.Modal.getInstance(document.getElementById('modal-editar-modulo')).hide();

      // Actualizar la tarjeta en el DOM sin recargar
      const m = json.modulo;
      const card = document.getElementById(`modulo-card-${m.id}`);
      if (card) {
        // Actualizar ícono
        card.querySelector('.modulo-icon i').className = `bi ${m.icono}`;
        // Actualizar nombre
        const nameEl = card.querySelector('.modulo-header p');
        if (nameEl) nameEl.textContent = m.nombre;
        // Actualizar slug y url_name
        const metaEl = card.querySelector('.modulo-header p:nth-child(2)');
        if (metaEl) metaEl.innerHTML = `${m.slug}${m.url_name?' · <span style="color:var(--azul);">' + m.url_name + '</span>':''}`;
        // Actualizar descripción si existe
        const descEl = card.querySelector('.modulo-body p:first-child');
        if (descEl && descEl.style.color.includes('muted') || descEl?.style.color === '') {
          if (m.descripcion) descEl.textContent = m.descripcion;
        }
        // Actualizar botón de editar con nuevos datos
        const editBtn = card.querySelector('.btn-icon-sm:first-child');
        if (editBtn) {
          editBtn.setAttribute('onclick',
            `abrirEditarModulo(${m.id},'${m.nombre}','${m.icono}','${m.url_name}','${m.descripcion}')`
          );
        }
      }

      // Actualizar en el array MODULOS
      const idx = MODULOS.findIndex(x => x.id === m.id);
      if (idx > -1) { MODULOS[idx].nombre = m.nombre; MODULOS[idx].icono = m.icono; }

      window.AlertManager.danger(`Módulo "${m.nombre}" actualizado.`);
    }

})();