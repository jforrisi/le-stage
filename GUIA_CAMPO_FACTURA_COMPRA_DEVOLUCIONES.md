# Guía: Agregar Campo "Factura de Compra" en Devoluciones

## 📋 OBJETIVO
Agregar un campo en el cabezal de devoluciones que permita seleccionar una factura de compra del proveedor seleccionado, mostrando fecha, serie y número.

---

## 1️⃣ AGREGAR EL CAMPO EN EL MODELO

**Archivo:** `compras/compras_devoluciones/models.py`

**En la clase `ComprasDevolucionesCabezal`, agregar:**

```python
from compras.models import ComprasCabezal  # Si no está importado

class ComprasDevolucionesCabezal(models.Model):
    # ... campos existentes ...
    
    # NUEVO CAMPO - Factura de Compra
    factura_compra = models.ForeignKey(
        ComprasCabezal,
        on_delete=models.PROTECT,
        related_name='devoluciones_factura',
        blank=True,
        null=True,
        verbose_name='Factura de Compra',
        help_text='Factura original a la que se hace referencia',
        db_column='factura_compra_id',  # Opcional: nombre de columna en BD
    )
```

**Parámetros importantes:**
- `on_delete=models.PROTECT` → No permite eliminar la factura si hay devoluciones
- `blank=True, null=True` → El campo es opcional
- `related_name='devoluciones_factura'` → Nombre para acceder desde ComprasCabezal

---

## 2️⃣ CREAR Y APLICAR LA MIGRACIÓN

```bash
# Crear la migración
python manage.py makemigrations compras_devoluciones

# Aplicar la migración
python manage.py migrate
```

---

## 3️⃣ AGREGAR AL FORMULARIO

**Archivo:** `compras/compras_devoluciones/forms.py`

**En `ComprasDevolucionesCabezalForm`:**

```python
class ComprasDevolucionesCabezalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar el queryset del campo factura_compra
        # Inicialmente vacío, se llenará con JavaScript según el proveedor
        self.fields['factura_compra'].queryset = ComprasCabezal.objects.none()
        self.fields['factura_compra'].required = False
        self.fields['factura_compra'].widget.attrs['class'] = 'form-control form-control-sm'
        self.fields['factura_compra'].widget.attrs['id'] = 'id_factura_compra'
    
    class Meta:
        model = ComprasDevolucionesCabezal
        fields = [
            # ... campos existentes ...
            'factura_compra',  # ← AGREGAR AQUÍ
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

---

## 4️⃣ CREAR ENDPOINT AJAX PARA OBTENER FACTURAS

**Archivo:** `compras/compras_devoluciones/views.py`

**Agregar esta vista:**

```python
from django.http import JsonResponse
from compras.models import ComprasCabezal

@require_http_methods(["GET"])
def obtener_facturas_proveedor(request):
    """Vista AJAX para obtener facturas de un proveedor"""
    try:
        proveedor_id = request.GET.get('proveedor_id', '').strip()
        
        if not proveedor_id:
            return JsonResponse({'results': []})
        
        # Obtener todas las facturas del proveedor
        facturas = ComprasCabezal.objects.filter(
            id_proveedor_id=proveedor_id
        ).select_related('tipo_documento').order_by('-fecha_documento', '-fchhor')
        
        resultados = []
        for factura in facturas:
            # Formatear la fecha
            fecha_str = factura.fecha_documento.strftime('%d/%m/%Y') if factura.fecha_documento else ''
            
            # Crear texto de visualización: "Fecha - Serie - Número"
            texto_display = f"{fecha_str}"
            if factura.serie_documento:
                texto_display += f" - {factura.serie_documento}"
            texto_display += f" - {factura.numero_documento}"
            
            resultados.append({
                'id': factura.transaccion,  # Usar transaccion como ID
                'transaccion': factura.transaccion,
                'fecha': fecha_str,
                'serie': factura.serie_documento or '',
                'numero': factura.numero_documento,
                'text': texto_display,  # Texto para mostrar en el select
                'tipo_documento': factura.tipo_documento.codigo if factura.tipo_documento else '',
            })
        
        return JsonResponse({'results': resultados})
    except Exception as e:
        import traceback
        print(f"Error en obtener_facturas_proveedor: {e}")
        print(traceback.format_exc())
        return JsonResponse({'results': [], 'error': str(e)}, status=500)
```

**Agregar la URL:**

**Archivo:** `compras/compras_devoluciones/urls.py`

```python
urlpatterns = [
    # ... URLs existentes ...
    path('ajax/obtener-facturas-proveedor/', views.obtener_facturas_proveedor, name='obtener_facturas_proveedor'),
]
```

---

## 5️⃣ AGREGAR AL TEMPLATE HTML

**Archivo:** `compras/compras_devoluciones/templates/compras_devoluciones/form_devolucion.html`

**Agregar después del campo de proveedor:**

```html
<!-- Línea: Factura de Compra (solo se muestra si hay proveedor) -->
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

---

## 6️⃣ AGREGAR JAVASCRIPT PARA CARGAR FACTURAS

**En el mismo template, en la sección `<script>`:**

```javascript
// ========== CARGAR FACTURAS SEGÚN PROVEEDOR ==========
const facturaCompraSelect = document.getElementById('id_factura_compra');
const facturaCompraRow = document.getElementById('factura-compra-row');
const proveedorHiddenInput = document.getElementById('id_proveedor') || document.querySelector('input[name="id_proveedor"]');

function cargarFacturasProveedor(proveedorId) {
    if (!proveedorId || !facturaCompraSelect) {
        // Si no hay proveedor, ocultar el campo
        if (facturaCompraRow) facturaCompraRow.style.display = 'none';
        facturaCompraSelect.innerHTML = '<option value="">---------</option>';
        return;
    }
    
    // Mostrar el campo
    if (facturaCompraRow) facturaCompraRow.style.display = 'flex';
    
    // Mostrar loading
    facturaCompraSelect.innerHTML = '<option value="">Cargando facturas...</option>';
    facturaCompraSelect.disabled = true;
    
    // Llamar al endpoint AJAX
    fetch(`{% url 'compras_devoluciones:obtener_facturas_proveedor' %}?proveedor_id=${proveedorId}`)
        .then(response => response.json())
        .then(data => {
            facturaCompraSelect.innerHTML = '<option value="">---------</option>';
            
            if (data.results && data.results.length > 0) {
                data.results.forEach(factura => {
                    const option = document.createElement('option');
                    option.value = factura.id;  // Usar transaccion como valor
                    option.textContent = factura.text;  // Mostrar: "Fecha - Serie - Número"
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
            facturaCompraSelect.innerHTML = '<option value="">Error al cargar facturas</option>';
            facturaCompraSelect.disabled = false;
        });
}

// Event listener para cuando cambia el proveedor
if (proveedorHiddenInput) {
    // Observar cambios en el proveedor
    let lastProveedorValue = proveedorHiddenInput.value;
    
    // Función para verificar cambios
    function verificarCambioProveedor() {
        const currentValue = proveedorHiddenInput.value;
        if (currentValue !== lastProveedorValue) {
            lastProveedorValue = currentValue;
            cargarFacturasProveedor(currentValue);
        }
    }
    
    // Verificar cada 500ms (por si cambia programáticamente)
    setInterval(verificarCambioProveedor, 500);
    
    // También cuando se selecciona un proveedor desde el autocomplete
    // (esto se llama desde la función seleccionarProveedor)
}

// Modificar la función seleccionarProveedor para cargar facturas
// Buscar en el código existente la función seleccionarProveedor y agregar:
function seleccionarProveedor(proveedor) {
    // ... código existente ...
    
    // NUEVO: Cargar facturas del proveedor
    cargarFacturasProveedor(proveedor.id);
}
```

---

## 7️⃣ ACTUALIZAR LA VISTA PARA PASAR DATOS

**Archivo:** `compras/compras_devoluciones/views.py`

**En la función `crear_devolucion` y `editar_devolucion`:**

No necesitas cambiar nada, Django maneja automáticamente el ForeignKey.

**Solo si quieres precargar facturas en edición:**

```python
def editar_devolucion(request, transaccion):
    devolucion = get_object_or_404(ComprasDevolucionesCabezal, transaccion=transaccion)
    
    if request.method == 'GET':
        form = ComprasDevolucionesCabezalForm(instance=devolucion)
        
        # Precargar facturas del proveedor si existe
        if devolucion.id_proveedor:
            form.fields['factura_compra'].queryset = ComprasCabezal.objects.filter(
                id_proveedor=devolucion.id_proveedor
            ).order_by('-fecha_documento')
```

---

## 📝 RESUMEN DE ARCHIVOS A MODIFICAR

1. ✅ **models.py** → Agregar `factura_compra = models.ForeignKey(...)`
2. ✅ **makemigrations + migrate** → Crear y aplicar migración
3. ✅ **forms.py** → Agregar campo en `fields`, `widgets`, `labels` y configurar queryset
4. ✅ **views.py** → Agregar función `obtener_facturas_proveedor`
5. ✅ **urls.py** → Agregar ruta para el endpoint AJAX
6. ✅ **form_devolucion.html** → Agregar campo HTML y JavaScript

---

## 🔍 VERIFICACIÓN

1. Ejecutar: `python manage.py check` → Sin errores
2. Ejecutar: `python manage.py makemigrations` → Debe crear la migración
3. Ejecutar: `python manage.py migrate` → Debe aplicarse correctamente
4. Probar en navegador:
   - Seleccionar proveedor → Debe aparecer el campo "Factura de Compra"
   - El select debe cargar las facturas del proveedor
   - Debe mostrar: "Fecha - Serie - Número"

---

## 💡 TIPS ADICIONALES

### Si quieres que el campo sea requerido:
```python
# En forms.py
self.fields['factura_compra'].required = True

# En models.py (opcional, pero mejor en forms)
factura_compra = models.ForeignKey(
    ...,
    # quitar blank=True y null=True si es requerido
)
```

### Si quieres filtrar solo facturas (no movimientos):
```python
# En obtener_facturas_proveedor
facturas = ComprasCabezal.objects.filter(
    id_proveedor_id=proveedor_id,
    tipo_documento__codigo__in=['facprov', 'factimp']  # Solo facturas
)
```

### Si quieres mostrar más información en el select:
```python
# En obtener_facturas_proveedor, modificar texto_display:
texto_display = f"{factura.transaccion} - {fecha_str} - {factura.numero_documento}"
```

---

## ⚠️ ERRORES COMUNES

1. **"Select no se actualiza"** → Verificar que el JavaScript se ejecute después de seleccionar proveedor
2. **"No aparecen facturas"** → Verificar que el proveedor_id se pase correctamente al endpoint
3. **"Error 404 en AJAX"** → Verificar que la URL esté correctamente configurada en urls.py

