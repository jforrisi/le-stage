# Guía: Agregar un Campo al Cabezal de Devoluciones de Compras

## 📋 PROCESO COMPLETO PASO A PASO

### 1️⃣ AGREGAR EL CAMPO EN EL MODELO (`models.py`)

**Ubicación:** `compras/compras_devoluciones/models.py`

**Ejemplo - Agregar un campo `mi_campo_nuevo`:**

```python
class ComprasDevolucionesCabezal(models.Model):
    # ... campos existentes ...
    
    # NUEVO CAMPO
    mi_campo_nuevo = models.CharField(
        max_length=100,
        blank=True,  # Si puede estar vacío
        null=True,   # Si puede ser NULL en la BD
        verbose_name='Mi Campo Nuevo',
        help_text='Descripción del campo',
        default='',  # Valor por defecto (opcional)
    )
```

**Tipos de campos comunes:**
- `CharField(max_length=X)` - Texto corto
- `TextField()` - Texto largo
- `IntegerField()` - Número entero
- `DecimalField(max_digits=15, decimal_places=2)` - Número decimal
- `DateField()` - Fecha
- `DateTimeField()` - Fecha y hora
- `BooleanField()` - Verdadero/Falso
- `ForeignKey(Modelo, on_delete=...)` - Relación con otro modelo

**Parámetros importantes:**
- `blank=True` → Permite que el campo esté vacío en formularios
- `null=True` → Permite NULL en la base de datos
- `default=valor` → Valor por defecto
- `db_column='nombre_columna'` → Nombre de columna en BD (si es diferente)
- `verbose_name='Etiqueta'` → Nombre que se muestra en admin/formularios

---

### 2️⃣ CREAR LA MIGRACIÓN

**Comando:**
```bash
python manage.py makemigrations compras_devoluciones
```

Esto creará un archivo en `compras/compras_devoluciones/migrations/` con un nombre como `000X_add_mi_campo_nuevo.py`

**Si necesitas crear la migración manualmente:**

```python
# compras/compras_devoluciones/migrations/000X_add_mi_campo_nuevo.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('compras_devoluciones', '000X_anterior'),  # Última migración
    ]

    operations = [
        migrations.AddField(
            model_name='comprasdevolucionescabezal',
            name='mi_campo_nuevo',
            field=models.CharField(
                blank=True,
                max_length=100,
                null=True,
                verbose_name='Mi Campo Nuevo'
            ),
        ),
    ]
```

---

### 3️⃣ APLICAR LA MIGRACIÓN

**Comando:**
```bash
python manage.py migrate compras_devoluciones
```

O para aplicar todas:
```bash
python manage.py migrate
```

**⚠️ IMPORTANTE:** Esto modificará la base de datos. Si hay datos existentes:
- Si el campo es `null=True` y `blank=True` → Los registros existentes tendrán NULL
- Si el campo tiene `default=valor` → Los registros existentes tendrán ese valor
- Si el campo NO tiene `null=True` ni `default` → La migración fallará si hay datos

---

### 4️⃣ ACTUALIZAR EL FORMULARIO (`forms.py`)

**Ubicación:** `compras/compras_devoluciones/forms.py`

**Agregar el campo al formulario:**

```python
class ComprasDevolucionesCabezalForm(forms.ModelForm):
    class Meta:
        model = ComprasDevolucionesCabezal
        fields = [
            # ... campos existentes ...
            'mi_campo_nuevo',  # ← AGREGAR AQUÍ
        ]
        widgets = {
            # ... widgets existentes ...
            'mi_campo_nuevo': forms.TextInput(attrs={
                'class': 'form-control form-control-sm',
                'id': 'id_mi_campo_nuevo'
            }),
        }
        labels = {
            # ... labels existentes ...
            'mi_campo_nuevo': 'Mi Campo Nuevo',  # ← AGREGAR AQUÍ
        }
```

---

### 5️⃣ ACTUALIZAR EL TEMPLATE (`form_devolucion.html`)

**Ubicación:** `compras/compras_devoluciones/templates/compras_devoluciones/form_devolucion.html`

**Agregar el campo en el formulario HTML:**

```html
<div class="form-group-compact form-group-medium">
    <label for="{{ form.mi_campo_nuevo.id_for_label }}">Mi Campo Nuevo</label>
    {{ form.mi_campo_nuevo }}
    {% if form.mi_campo_nuevo.errors %}
        <div class="error-message" style="font-size: 0.75rem;">
            {{ form.mi_campo_nuevo.errors }}
        </div>
    {% endif %}
</div>
```

---

### 6️⃣ ACTUALIZAR LA VISTA (si es necesario) (`views.py`)

**Ubicación:** `compras/compras_devoluciones/views.py`

Generalmente NO necesitas cambiar nada aquí, Django maneja automáticamente los campos del formulario.

**Solo si necesitas lógica especial:**

```python
def crear_devolucion(request):
    if request.method == 'POST':
        form = ComprasDevolucionesCabezalForm(request.POST)
        if form.is_valid():
            devolucion = form.save(commit=False)
            # Lógica personalizada con el nuevo campo
            if devolucion.mi_campo_nuevo:
                # hacer algo...
            devolucion.save()
```

---

### 7️⃣ ACTUALIZAR EL ADMIN (opcional) (`admin.py`)

**Ubicación:** `compras/compras_devoluciones/admin.py`

```python
@admin.register(ComprasDevolucionesCabezal)
class ComprasDevolucionesCabezalAdmin(ModelAdmin):
    list_display = [
        'transaccion',
        'numero_documento',
        # ... otros campos ...
        'mi_campo_nuevo',  # ← AGREGAR AQUÍ
    ]
    list_filter = [
        # ... filtros existentes ...
        'mi_campo_nuevo',  # ← AGREGAR AQUÍ (opcional)
    ]
```

---

## 📝 RESUMEN DE ARCHIVOS A MODIFICAR

1. ✅ **models.py** → Agregar el campo al modelo
2. ✅ **makemigrations** → Crear la migración
3. ✅ **migrate** → Aplicar la migración
4. ✅ **forms.py** → Agregar el campo al formulario
5. ✅ **form_devolucion.html** → Agregar el campo en el template
6. ✅ **views.py** → (Opcional) Lógica personalizada
7. ✅ **admin.py** → (Opcional) Mostrar en admin

---

## ⚠️ IMPORTANTE - VALORES POR DEFECTO

**Si ya hay datos en la tabla:**

```python
# ❌ MAL - Causará error si hay datos
mi_campo = models.CharField(max_length=100)  # Sin null ni default

# ✅ BIEN - Opción 1: Permitir NULL
mi_campo = models.CharField(max_length=100, null=True, blank=True)

# ✅ BIEN - Opción 2: Valor por defecto
mi_campo = models.CharField(max_length=100, default='')

# ✅ BIEN - Opción 3: Ambos
mi_campo = models.CharField(max_length=100, null=True, blank=True, default='')
```

---

## 🔍 VERIFICAR QUE FUNCIONA

1. Ejecutar: `python manage.py check` → No debe haber errores
2. Ejecutar: `python manage.py makemigrations` → No debe crear nuevas migraciones
3. Probar en el navegador: `/devoluciones/crear/` → El campo debe aparecer

---

## 📚 EJEMPLOS DE CAMPOS COMUNES

### Campo de texto corto:
```python
codigo = models.CharField(max_length=20, verbose_name='Código')
```

### Campo de texto largo:
```python
observaciones = models.TextField(blank=True, null=True, verbose_name='Observaciones')
```

### Campo numérico:
```python
cantidad = models.DecimalField(max_digits=15, decimal_places=2, default=0)
```

### Campo de fecha:
```python
fecha = models.DateField(verbose_name='Fecha')
```

### Campo booleano:
```python
activo = models.BooleanField(default=True, verbose_name='Activo')
```

### Campo ForeignKey (relación):
```python
proveedor = models.ForeignKey(
    Proveedor,
    on_delete=models.PROTECT,
    verbose_name='Proveedor',
    db_column='id_proveedor'
)
```

---

## 🚨 ERRORES COMUNES

1. **"no such column"** → No ejecutaste `migrate`
2. **"Field already exists"** → Ya existe el campo, revisa el modelo
3. **"NOT NULL constraint failed"** → El campo necesita `null=True` o `default`
4. **"no such table"** → La app no está en `INSTALLED_APPS` o no existe

---

## ✅ CHECKLIST RÁPIDO

- [ ] Campo agregado en `models.py`
- [ ] `makemigrations` ejecutado
- [ ] `migrate` ejecutado
- [ ] Campo agregado en `forms.py` (fields, widgets, labels)
- [ ] Campo agregado en el template HTML
- [ ] Probado en el navegador
- [ ] Sin errores en `python manage.py check`

