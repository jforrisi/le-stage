# Guía de Verificación Paso a Paso - Campo Factura de Compra

## ✅ CHECKLIST DE VERIFICACIÓN

Sigue estos pasos en orden y verifica cada uno antes de continuar.

---

## PASO 1: Agregar Campo en Modelo

### ✅ 1.1 Agregar el campo en `models.py`

**Archivo:** `compras/compras_devoluciones/models.py`

```python
from compras.models import ComprasCabezal  # Verificar que esté importado

class ComprasDevolucionesCabezal(models.Model):
    # ... campos existentes ...
    
    factura_compra = models.ForeignKey(
        ComprasCabezal,
        on_delete=models.PROTECT,
        related_name='devoluciones_factura',
        blank=True,
        null=True,
        verbose_name='Factura de Compra',
        help_text='Factura original a la que se hace referencia',
    )
```

### 🔍 VERIFICACIÓN 1:
```bash
python manage.py check
```
**Resultado esperado:** `System check identified no issues (0 silenced).`

Si hay errores, corrígelos antes de continuar.

---

## PASO 2: Crear Migración

### ✅ 2.1 Crear la migración
```bash
python manage.py makemigrations compras_devoluciones
```

**Resultado esperado:** 
```
Migrations for 'compras_devoluciones':
  compras_devoluciones/migrations/000X_add_factura_compra.py
    - Add field factura_compra to comprasdevolucionescabezal
```

### 🔍 VERIFICACIÓN 2:
- ✅ Se creó el archivo de migración
- ✅ El nombre del campo es correcto (`factura_compra`)

---

## PASO 3: Aplicar Migración

### ✅ 3.1 Aplicar la migración
```bash
python manage.py migrate compras_devoluciones
```

**Resultado esperado:**
```
Running migrations:
  Applying compras_devoluciones.000X_add_factura_compra... OK
```

### 🔍 VERIFICACIÓN 3:
```bash
python manage.py dbshell
```
Luego ejecutar:
```sql
.schema compras_devoluciones_cabezal
```
**Resultado esperado:** Debe aparecer la columna `factura_compra_id` (o el nombre que hayas puesto)

**Salir de dbshell:**
```sql
.quit
```

---

## PASO 4: Agregar al Formulario

### ✅ 4.1 Modificar `forms.py`

**Archivo:** `compras/compras_devoluciones/forms.py`

```python
class ComprasDevolucionesCabezalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar factura_compra
        self.fields['factura_compra'].queryset = ComprasCabezal.objects.none()
        self.fields['factura_compra'].required = False
        self.fields['factura_compra'].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['factura_compra'].widget.attrs['id'] = 'id_factura_compra'
    
    class Meta:
        model = ComprasDevolucionesCabezal
        fields = [
            # ... campos existentes ...
            'factura_compra',  # ← AGREGAR
        ]
        widgets = {
            # ... widgets existentes ...
            'factura_compra': forms.Select(attrs={
                'class': 'form-control form-control-sm',
                'id': 'id_factura_compra'
            }),
        }
        labels = {
            # ... labels existentes ...
            'factura_compra': 'Factura de Compra',
        }
```

### 🔍 VERIFICACIÓN 4:
```bash
python manage.py check
python manage.py shell
```

En el shell de Python:
```python
from compras.compras_devoluciones.forms import ComprasDevolucionesCabezalForm
form = ComprasDevolucionesCabezalForm()
print('factura_compra' in form.fields)
# Debe imprimir: True
exit()
```

---

## PASO 5: Crear Endpoint AJAX

### ✅ 5.1 Agregar función en `views.py`

**Archivo:** `compras/compras_devoluciones/views.py`

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from compras.models import ComprasCabezal

@require_http_methods(["GET"])
def obtener_facturas_proveedor(request):
    """Vista AJAX para obtener facturas de un proveedor"""
    try:
        proveedor_id = request.GET.get('proveedor_id', '').strip()
        
        if not proveedor_id:
            return JsonResponse({'results': []})
        
        facturas = ComprasCabezal.objects.filter(
            id_proveedor_id=proveedor_id
        ).select_related('tipo_documento').order_by('-fecha_documento', '-fchhor')
        
        resultados = []
        for factura in facturas:
            fecha_str = factura.fecha_documento.strftime('%d/%m/%Y') if factura.fecha_documento else ''
            
            texto_display = f"{fecha_str}"
            if factura.serie_documento:
                texto_display += f" - {factura.serie_documento}"
            texto_display += f" - {factura.numero_documento}"
            
            resultados.append({
                'id': factura.transaccion,
                'transaccion': factura.transaccion,
                'fecha': fecha_str,
                'serie': factura.serie_documento or '',
                'numero': factura.numero_documento,
                'text': texto_display,
            })
        
        return JsonResponse({'results': resultados})
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)
```

### ✅ 5.2 Agregar URL

**Archivo:** `compras/compras_devoluciones/urls.py`

```python
urlpatterns = [
    # ... URLs existentes ...
    path('ajax/obtener-facturas-proveedor/', views.obtener_facturas_proveedor, name='obtener_facturas_proveedor'),
]
```

### 🔍 VERIFICACIÓN 5:

**5.1 Verificar que el servidor arranca:**
```bash
python manage.py runserver
```
**Resultado esperado:** Servidor arranca sin errores

**5.2 Probar el endpoint directamente en el navegador:**
```
http://127.0.0.1:8000/devoluciones/ajax/obtener-facturas-proveedor/?proveedor_id=1
```
**Resultado esperado:** JSON con facturas o `{"results": []}` si no hay facturas

**Si hay error 404:** Verificar que la URL esté correcta en `urls.py`

**Si hay error 500:** Revisar la consola del servidor para ver el error

---

## PASO 6: Agregar al Template HTML

### ✅ 6.1 Agregar el campo en el HTML

**Archivo:** `compras/compras_devoluciones/templates/compras_devoluciones/form_devolucion.html`

Agregar después del campo de proveedor:

```html
<!-- Factura de Compra -->
<div class="form-row-compact" id="factura-compra-row" style="display: none;">
    <div class="form-group-compact form-group-large" style="flex: 1;">
        <label for="{{ form.factura_compra.id_for_label }}">Factura de Compra</label>
        {{ form.factura_compra }}
        {% if form.factura_compra.errors %}
            <div class="error-message" style="font-size: 0.75rem;">
                {{ form.factura_compra.errors }}
            </div>
        {% endif %}
    </div>
</div>
```

### 🔍 VERIFICACIÓN 6:

**6.1 Recargar la página de crear devolución:**
```
http://127.0.0.1:8000/devoluciones/crear/
```

**Resultado esperado:**
- ✅ La página carga sin errores
- ✅ No aparece el campo "Factura de Compra" (porque está oculto inicialmente)

**Si hay error:** Revisar la consola del servidor

---

## PASO 7: Agregar JavaScript

### ✅ 7.1 Agregar función JavaScript

**En el mismo template, en la sección `<script>`:**

```javascript
// ========== CARGAR FACTURAS SEGÚN PROVEEDOR ==========
const facturaCompraSelect = document.getElementById('id_factura_compra');
const facturaCompraRow = document.getElementById('factura-compra-row');
const proveedorHiddenInput = document.getElementById('id_proveedor') || 
                             document.querySelector('input[name="id_proveedor"]');

function cargarFacturasProveedor(proveedorId) {
    if (!proveedorId || !facturaCompraSelect) {
        if (facturaCompraRow) facturaCompraRow.style.display = 'none';
        if (facturaCompraSelect) {
            facturaCompraSelect.innerHTML = '<option value="">---------</option>';
        }
        return;
    }
    
    // Mostrar el campo
    if (facturaCompraRow) facturaCompraRow.style.display = 'flex';
    
    // Mostrar loading
    if (facturaCompraSelect) {
        facturaCompraSelect.innerHTML = '<option value="">Cargando facturas...</option>';
        facturaCompraSelect.disabled = true;
    }
    
    // Llamar al endpoint AJAX
    const url = `{% url 'compras_devoluciones:obtener_facturas_proveedor' %}?proveedor_id=${proveedorId}`;
    console.log('Cargando facturas desde:', url);  // Para debug
    
    fetch(url)
        .then(response => {
            console.log('Response status:', response.status);  // Para debug
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data);  // Para debug
            
            if (!facturaCompraSelect) return;
            
            facturaCompraSelect.innerHTML = '<option value="">---------</option>';
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(factura => {
                    const option = document.createElement('option');
                    option.value = factura.id;
                    option.textContent = factura.text;
                    facturaCompraSelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No hay facturas disponibles';
                facturaCompraSelect.appendChild(option);
            }
            
            facturaCompraSelect.disabled = false;
        })
        .catch(error => {
            console.error('Error cargando facturas:', error);
            if (facturaCompraSelect) {
                facturaCompraSelect.innerHTML = '<option value="">Error al cargar facturas</option>';
                facturaCompraSelect.disabled = false;
            }
        });
}

// Observar cambios en el proveedor
if (proveedorHiddenInput) {
    let lastProveedorValue = proveedorHiddenInput.value;
    
    function verificarCambioProveedor() {
        const currentValue = proveedorHiddenInput.value;
        if (currentValue !== lastProveedorValue) {
            console.log('Proveedor cambió de', lastProveedorValue, 'a', currentValue);  // Para debug
            lastProveedorValue = currentValue;
            cargarFacturasProveedor(currentValue);
        }
    }
    
    // Verificar cada 500ms
    setInterval(verificarCambioProveedor, 500);
    
    // También verificar al cargar la página
    if (proveedorHiddenInput.value) {
        cargarFacturasProveedor(proveedorValue.value);
    }
}

// Si tienes una función seleccionarProveedor, modifícala:
// function seleccionarProveedor(proveedor) {
//     // ... código existente ...
//     cargarFacturasProveedor(proveedor.id);  // ← AGREGAR ESTA LÍNEA
// }
```

### 🔍 VERIFICACIÓN 7:

**7.1 Abrir la consola del navegador (F12)**

**7.2 Recargar la página:**
```
http://127.0.0.1:8000/devoluciones/crear/
```

**7.3 Seleccionar un proveedor**

**Resultado esperado:**
- ✅ Aparece el campo "Factura de Compra"
- ✅ En la consola del navegador aparecen los logs:
  - `"Cargando facturas desde: ..."`
  - `"Response status: 200"`
  - `"Datos recibidos: {results: [...]}"`
- ✅ El select se llena con las facturas del proveedor
- ✅ Cada opción muestra: "Fecha - Serie - Número"

**Si no funciona:**
- Revisar la consola del navegador para ver errores
- Verificar que el `proveedorHiddenInput` tenga el ID correcto
- Verificar que la URL del endpoint sea correcta

---

## PASO 8: Prueba Completa

### ✅ 8.1 Flujo completo

1. Ir a: `http://127.0.0.1:8000/devoluciones/crear/`
2. Seleccionar un proveedor
3. Verificar que aparece "Factura de Compra"
4. Verificar que se cargan las facturas
5. Seleccionar una factura
6. Llenar el resto del formulario
7. Guardar

### 🔍 VERIFICACIÓN 8:

**8.1 Verificar en la base de datos:**
```bash
python manage.py shell
```

```python
from compras.compras_devoluciones.models import ComprasDevolucionesCabezal
ultima = ComprasDevolucionesCabezal.objects.last()
print(f"Factura compra: {ultima.factura_compra}")
print(f"Transacción factura: {ultima.factura_compra.transaccion if ultima.factura_compra else None}")
exit()
```

**Resultado esperado:** Debe mostrar la factura seleccionada

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "no such column: factura_compra_id"
**Solución:** No ejecutaste `migrate`. Ejecuta: `python manage.py migrate`

### Error: "Field 'factura_compra' doesn't exist"
**Solución:** No agregaste el campo en `forms.py` → `fields = [...]`

### Error 404 en el endpoint AJAX
**Solución:** Verifica que la URL esté en `urls.py` y que el `app_name` sea correcto

### El select no se llena
**Solución:** 
- Abre la consola del navegador (F12)
- Revisa si hay errores JavaScript
- Verifica que el `proveedorHiddenInput` tenga el valor correcto
- Prueba el endpoint directamente en el navegador

### El campo no aparece cuando selecciono proveedor
**Solución:**
- Verifica que `facturaCompraRow` exista en el HTML
- Verifica que el JavaScript se ejecute (revisa consola)
- Verifica que `proveedorHiddenInput.value` tenga un valor

---

## ✅ CHECKLIST FINAL

- [ ] Modelo actualizado
- [ ] Migración creada y aplicada
- [ ] Formulario actualizado
- [ ] Endpoint AJAX funciona
- [ ] Campo aparece en el HTML
- [ ] JavaScript carga facturas
- [ ] Se puede guardar con factura seleccionada
- [ ] Se guarda correctamente en la BD

---

## 📝 NOTAS

- Si algo no funciona, **NO continúes al siguiente paso**. Arréglalo primero.
- Usa la consola del navegador (F12) para ver errores JavaScript
- Usa la consola del servidor para ver errores Python
- Los `console.log()` en el JavaScript te ayudan a debuggear

