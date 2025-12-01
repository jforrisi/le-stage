document.addEventListener('DOMContentLoaded', function() {
    const selectProveedor = document.getElementById('nuevo-proveedor-select');
    const inputCodigo = document.getElementById('nuevo-codigo-proveedor');
    const btnAgregar = document.getElementById('btn-agregar-codigo');
    const btnBuscar = document.querySelector('.btn-buscar-proveedor');
    const tbody = document.getElementById('codigos-proveedor-tbody');
    const modal = document.getElementById('modal-buscar-proveedor');
    const inputBusqueda = document.getElementById('busqueda-proveedor-input');
    const resultadosDiv = document.getElementById('resultados-proveedores');
    let selectActual = null;
    let filaEditando = null;

    // Cargar proveedores activos en el select
    if (selectProveedor) {
        cargarProveedores();
    }

    // Agregar código proveedor
    if (btnAgregar) {
        btnAgregar.addEventListener('click', function() {
            agregarCodigoProveedor();
        });
    }

    // Enter en el campo código
    if (inputCodigo) {
        inputCodigo.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                agregarCodigoProveedor();
            }
        });
    }

    // Abrir modal de búsqueda con F2 o clic
    if (selectProveedor) {
        selectProveedor.addEventListener('keydown', function(e) {
            if (e.key === 'F2') {
                e.preventDefault();
                abrirModalBusqueda(selectProveedor);
            }
        });
    }

    if (btnBuscar) {
        btnBuscar.addEventListener('click', function() {
            abrirModalBusqueda(selectProveedor);
        });
    }

    // Editar código desde la tabla
    if (tbody) {
        tbody.addEventListener('click', function(e) {
            if (e.target.closest('.btn-editar-codigo')) {
                editarCodigo(e.target.closest('tr'));
            } else if (e.target.closest('.btn-eliminar-codigo')) {
                eliminarCodigo(e.target.closest('tr'));
            }
        });
    }

    // Cerrar modal
    if (modal) {
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', cerrarModal);
        }
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                cerrarModal();
            }
        });
    }

    // Búsqueda de proveedores
    if (inputBusqueda) {
        let searchTimeout;
        inputBusqueda.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    buscarProveedores(query);
                }, 300);
            } else if (query.length === 0) {
                buscarProveedores('');
            }
        });

        inputBusqueda.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const primeraOpcion = resultadosDiv.querySelector('.resultado-item');
                if (primeraOpcion) {
                    seleccionarProveedor(primeraOpcion.dataset.proveedorId, primeraOpcion.dataset.proveedorText);
                }
            } else if (e.key === 'Escape') {
                cerrarModal();
            }
        });
    }

    function cargarProveedores() {
        if (!selectProveedor) return;
        
        console.log('Cargando proveedores...');
        
        fetch('/buscar-proveedores/')
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('Datos recibidos:', data);
                if (!data) {
                    console.warn('No se recibieron datos');
                    selectProveedor.innerHTML = '<option value="">No hay proveedores disponibles</option>';
                    return;
                }
                
                if (!data.results || data.results.length === 0) {
                    console.warn('No hay proveedores en los resultados');
                    selectProveedor.innerHTML = '<option value="">No hay proveedores disponibles</option>';
                    return;
                }
                
                const currentValue = selectProveedor.value; // Guardar valor actual
                selectProveedor.innerHTML = '<option value="">Seleccione un proveedor...</option>';
                
                data.results.forEach(proveedor => {
                    const option = document.createElement('option');
                    option.value = proveedor.id;
                    option.textContent = proveedor.text || `${proveedor.codigo} - ${proveedor.razon || proveedor.nombre_comercial || 'Sin nombre'}`;
                    selectProveedor.appendChild(option);
                });
                
                console.log('Proveedores cargados:', data.results.length);
                
                // Restaurar valor si existía
                if (currentValue) {
                    selectProveedor.value = currentValue;
                }
            })
            .catch(error => {
                console.error('Error al cargar proveedores:', error);
                console.error('Stack:', error.stack);
                selectProveedor.innerHTML = '<option value="">Error al cargar proveedores</option>';
            });
    }

    function agregarCodigoProveedor() {
        if (!selectProveedor || !inputCodigo || !tbody) return;
        
        const proveedorId = selectProveedor.value;
        const codigo = inputCodigo.value.trim();

        if (!proveedorId) {
            alert('Por favor seleccione un proveedor');
            return;
        }

        if (!codigo) {
            alert('Por favor ingrese el código del proveedor');
            return;
        }

        // Verificar si ya existe este proveedor (un proveedor solo puede aparecer una vez por artículo)
        const filasExistentes = tbody.querySelectorAll('tr');
        for (let fila of filasExistentes) {
            if (fila.dataset.proveedorId === proveedorId) {
                alert('Este proveedor ya tiene asignado un código. Edítelo si desea modificarlo.');
                return;
            }
        }

        // Obtener nombre del proveedor
        const proveedorOption = selectProveedor.options[selectProveedor.selectedIndex];
        const proveedorNombre = proveedorOption.textContent;

        // Agregar fila a la tabla
        agregarFilaTabla(proveedorId, proveedorNombre, codigo);

        // Limpiar formulario
        selectProveedor.value = '';
        inputCodigo.value = '';
        selectProveedor.focus();
    }

    function agregarFilaTabla(proveedorId, proveedorNombre, codigo) {
        if (!tbody) return;
        
        const tr = document.createElement('tr');
        tr.dataset.proveedorId = proveedorId;
        tr.dataset.codigo = codigo;
        tr.innerHTML = `
            <td>
                <input type="hidden" name="proveedores" value="${proveedorId}">
                <span class="proveedor-nombre">${proveedorNombre}</span>
            </td>
            <td>
                <input type="hidden" name="codigos" value="${codigo}">
                <span class="codigo-valor">${codigo}</span>
            </td>
            <td>
                <button type="button" class="btn btn-sm btn-warning btn-editar-codigo" title="Editar">
                    <span class="material-symbols-outlined">edit</span>
                </button>
                <button type="button" class="btn btn-sm btn-danger btn-eliminar-codigo" title="Eliminar">
                    <span class="material-symbols-outlined">delete</span>
                </button>
            </td>
        `;
        
        // Si hay empty state, eliminarlo
        const emptyState = tbody.parentElement.querySelector('.empty-state-small');
        if (emptyState) {
            emptyState.remove();
        }
        
        tbody.appendChild(tr);
    }

    function editarCodigo(fila) {
        if (!fila) return;
        
        filaEditando = fila;
        const proveedorId = fila.dataset.proveedorId;
        const codigo = fila.dataset.codigo;
        
        // Cambiar a modo edición
        const tdProveedor = fila.querySelector('td:first-child');
        const tdCodigo = fila.querySelector('td:nth-child(2)');
        const tdAcciones = fila.querySelector('td:last-child');
        
        // Guardar valores originales
        const proveedorNombre = tdProveedor.querySelector('.proveedor-nombre').textContent;
        
        // Crear select para proveedor
        const selectWrapper = document.createElement('div');
        selectWrapper.className = 'proveedor-select-wrapper';
        selectWrapper.innerHTML = `
            <select class="form-control proveedor-select-edit" style="flex: 1;">
                <option value="${proveedorId}" selected>${proveedorNombre}</option>
            </select>
            <button type="button" class="btn btn-sm btn-info btn-buscar-proveedor-edit" title="Presione F2 o haga clic para buscar">
                <span class="material-symbols-outlined">search</span>
            </button>
        `;
        
        // Cargar opciones en el select
        cargarProveedoresEnSelect(selectWrapper.querySelector('select'));
        
        // Reemplazar contenido
        tdProveedor.innerHTML = '';
        tdProveedor.appendChild(selectWrapper);
        
        // Input para código
        tdCodigo.innerHTML = `<input type="text" class="form-control codigo-edit-input" value="${codigo}">`;
        
        // Botones de guardar/cancelar
        tdAcciones.innerHTML = `
            <button type="button" class="btn btn-sm btn-success btn-guardar-codigo" title="Guardar">
                <span class="material-symbols-outlined">check</span>
            </button>
            <button type="button" class="btn btn-sm btn-secondary btn-cancelar-codigo" title="Cancelar">
                <span class="material-symbols-outlined">close</span>
            </button>
        `;
        
        // Event listeners
        selectWrapper.querySelector('.btn-buscar-proveedor-edit').addEventListener('click', function() {
            abrirModalBusqueda(selectWrapper.querySelector('select'));
        });
        
        selectWrapper.querySelector('select').addEventListener('keydown', function(e) {
            if (e.key === 'F2') {
                e.preventDefault();
                abrirModalBusqueda(this);
            }
        });
        
        tdAcciones.querySelector('.btn-guardar-codigo').addEventListener('click', function() {
            guardarEdicion(fila);
        });
        
        tdAcciones.querySelector('.btn-cancelar-codigo').addEventListener('click', function() {
            cancelarEdicion(fila, proveedorId, proveedorNombre, codigo);
        });
        
        // Focus en el input de código
        tdCodigo.querySelector('input').focus();
    }

    function guardarEdicion(fila) {
        if (!fila) return;
        
        const select = fila.querySelector('.proveedor-select-edit');
        const input = fila.querySelector('.codigo-edit-input');
        
        if (!select || !input) return;
        
        const nuevoProveedorId = select.value;
        const nuevoCodigo = input.value.trim();
        
        if (!nuevoProveedorId) {
            alert('Por favor seleccione un proveedor');
            return;
        }
        
        if (!nuevoCodigo) {
            alert('Por favor ingrese el código del proveedor');
            return;
        }
        
        // Actualizar datos
        const proveedorOption = select.options[select.selectedIndex];
        const proveedorNombre = proveedorOption.textContent;
        
        fila.dataset.proveedorId = nuevoProveedorId;
        fila.dataset.codigo = nuevoCodigo;
        
        // Restaurar vista normal
        fila.querySelector('td:first-child').innerHTML = `
            <input type="hidden" name="proveedores" value="${nuevoProveedorId}">
            <span class="proveedor-nombre">${proveedorNombre}</span>
        `;
        
        fila.querySelector('td:nth-child(2)').innerHTML = `
            <input type="hidden" name="codigos" value="${nuevoCodigo}">
            <span class="codigo-valor">${nuevoCodigo}</span>
        `;
        
        fila.querySelector('td:last-child').innerHTML = `
            <button type="button" class="btn btn-sm btn-warning btn-editar-codigo" title="Editar">
                <span class="material-symbols-outlined">edit</span>
            </button>
            <button type="button" class="btn btn-sm btn-danger btn-eliminar-codigo" title="Eliminar">
                <span class="material-symbols-outlined">delete</span>
            </button>
        `;
        
        filaEditando = null;
    }

    function cancelarEdicion(fila, proveedorId, proveedorNombre, codigo) {
        if (!fila) return;
        
        fila.dataset.proveedorId = proveedorId;
        fila.dataset.codigo = codigo;
        
        fila.querySelector('td:first-child').innerHTML = `
            <input type="hidden" name="proveedores" value="${proveedorId}">
            <span class="proveedor-nombre">${proveedorNombre}</span>
        `;
        
        fila.querySelector('td:nth-child(2)').innerHTML = `
            <input type="hidden" name="codigos" value="${codigo}">
            <span class="codigo-valor">${codigo}</span>
        `;
        
        fila.querySelector('td:last-child').innerHTML = `
            <button type="button" class="btn btn-sm btn-warning btn-editar-codigo" title="Editar">
                <span class="material-symbols-outlined">edit</span>
            </button>
            <button type="button" class="btn btn-sm btn-danger btn-eliminar-codigo" title="Eliminar">
                <span class="material-symbols-outlined">delete</span>
            </button>
        `;
        
        filaEditando = null;
    }

    function eliminarCodigo(fila) {
        if (!fila || !tbody) return;
        
        if (confirm('¿Está seguro que desea eliminar este código de proveedor?')) {
            fila.remove();
            
            // Si no hay más filas, mostrar empty state
            if (tbody.children.length === 0) {
                const tabla = document.getElementById('tabla-codigos-proveedor');
                if (tabla && tabla.parentElement) {
                    const emptyState = document.createElement('div');
                    emptyState.className = 'empty-state-small';
                    emptyState.innerHTML = '<p>No hay códigos de proveedor asociados. Agregue uno usando el formulario de arriba.</p>';
                    tabla.parentElement.appendChild(emptyState);
                }
            }
        }
    }

    function cargarProveedoresEnSelect(select) {
        if (!select) return;
        
        fetch('/buscar-proveedores/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (!data || !data.results) {
                    return;
                }
                
                const currentValue = select.value;
                // Mantener la opción actual si existe
                const currentOption = select.querySelector(`option[value="${currentValue}"]`);
                
                // Agregar todas las opciones (evitando duplicados)
                data.results.forEach(proveedor => {
                    if (!select.querySelector(`option[value="${proveedor.id}"]`)) {
                        const option = document.createElement('option');
                        option.value = proveedor.id;
                        option.textContent = proveedor.text;
                        if (proveedor.id == currentValue) {
                            option.selected = true;
                        }
                        select.appendChild(option);
                    }
                });
                
                // Restaurar selección si existía
                if (currentValue && select.querySelector(`option[value="${currentValue}"]`)) {
                    select.value = currentValue;
                }
            })
            .catch(error => {
                console.error('Error al cargar proveedores:', error);
            });
    }

    function abrirModalBusqueda(select) {
        if (!select || !modal) return;
        selectActual = select;
        modal.style.display = 'flex';
        if (inputBusqueda) {
            inputBusqueda.value = '';
            inputBusqueda.focus();
        }
        buscarProveedores('');
    }

    function cerrarModal() {
        if (modal) {
            modal.style.display = 'none';
        }
        selectActual = null;
        if (inputBusqueda) {
            inputBusqueda.value = '';
        }
        if (resultadosDiv) {
            resultadosDiv.innerHTML = '';
        }
    }

    function buscarProveedores(query) {
        if (!resultadosDiv) return;
        
        const url = `/buscar-proveedores/?q=${encodeURIComponent(query)}`;
        
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                mostrarResultados(data.results || []);
            })
            .catch(error => {
                console.error('Error al buscar proveedores:', error);
                resultadosDiv.innerHTML = '<div class="no-results">Error al buscar proveedores</div>';
            });
    }

    function mostrarResultados(resultados) {
        if (!resultadosDiv) return;
        
        resultadosDiv.innerHTML = '';
        
        if (resultados.length === 0) {
            resultadosDiv.innerHTML = '<div class="no-results">No se encontraron proveedores</div>';
            return;
        }

        resultados.forEach(proveedor => {
            const item = document.createElement('div');
            item.className = 'resultado-item';
            item.dataset.proveedorId = proveedor.id;
            item.dataset.proveedorText = proveedor.text;
            item.innerHTML = `
                <div class="resultado-codigo">${proveedor.codigo}</div>
                <div class="resultado-nombre">${proveedor.razon || proveedor.nombre_comercial}</div>
            `;
            item.addEventListener('click', function() {
                seleccionarProveedor(proveedor.id, proveedor.text);
            });
            resultadosDiv.appendChild(item);
        });
    }

    function seleccionarProveedor(proveedorId, proveedorText) {
        if (!selectActual) return;
        
        // Si es el select principal, actualizar valor directamente
        if (selectActual.id === 'nuevo-proveedor-select') {
            // Verificar si la opción ya existe
            let optionExists = false;
            for (let option of selectActual.options) {
                if (option.value == proveedorId) {
                    option.selected = true;
                    optionExists = true;
                    break;
                }
            }
            // Si no existe, agregarla
            if (!optionExists) {
                const option = document.createElement('option');
                option.value = proveedorId;
                option.textContent = proveedorText;
                option.selected = true;
                selectActual.appendChild(option);
            }
            // Asegurar que el valor esté seleccionado
            selectActual.value = proveedorId;
            // Disparar evento change
            selectActual.dispatchEvent(new Event('change'));
        } else {
            // Para selects de edición, reemplazar opciones
            const currentValue = selectActual.value;
            selectActual.innerHTML = '';
            const option = document.createElement('option');
            option.value = proveedorId;
            option.textContent = proveedorText;
            option.selected = true;
            selectActual.appendChild(option);
            // Cargar todas las opciones después
            cargarProveedoresEnSelect(selectActual);
            // Restaurar selección
            setTimeout(() => {
                selectActual.value = proveedorId;
            }, 100);
        }
        cerrarModal();
    }
});

