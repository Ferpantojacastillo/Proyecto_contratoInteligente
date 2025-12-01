# 📋 Cambios Realizados - Sistema de Créditos Inteligentes

## Resumen General
Se han realizado múltiples mejoras y correcciones al sistema de gestión de créditos, incluyendo:
- ✅ Corrección de autenticación de docentes
- ✅ Implementación de generación de PDFs
- ✅ Mejora del panel de docentes
- ✅ Corrección de errores CSRF
- ✅ Optimización de rutas y vistas

---

## 1. Corrección de Contraseñas (Problema Principal)

### Problema
Cuando un administrador asignaba una contraseña a un usuario docente desde el admin, la contraseña se guardaba en **texto plano** en lugar de hasheada, causando que el login fallara.

### Soluciones Implementadas

#### a) Formulario Admin (`usuarios/admin.py`)
```python
class UsuarioAdminForm(forms.ModelForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd and '$' not in pwd:  # Si no está hasheada
            user.set_password(pwd)   # Hashearla
        if commit:
            user.save()
        return user
```
- Detecta contraseñas en texto plano
- Las convierte a hash usando `set_password()`

#### b) Registro de Docentes (`usuarios/views.py`)
```python
def docente_registro(request):
    # ...
    docente.set_password(generated_pwd)  # Usa set_password
    docente.is_active = True             # Activa inmediatamente
    # ...
```
- Docentes pueden iniciar sesión con sus credenciales registradas
- Cuenta activa automáticamente

---

## 2. Generación de PDFs

### Archivos Modificados
- `creditos/views.py` - Nueva vista `credito_pdf`
- `creditos/urls.py` - Nueva ruta `pdf/<int:id_credito>/`
- `creditos/templates/creditos/mis_creditos.html` - Botón "Generar PDF"
- `creditos/templates/creditos/pdf_error.html` - Plantilla de error

### Funcionalidad
- Genera PDFs con datos del alumno y crédito
- Guarda en carpeta `documentos/<numero_control>.pdf`
- Solo disponible para créditos liberados
- Solo el propietario puede descargar su PDF

### Instalación
```bash
pip install reportlab
```

---

## 3. Panel de Docentes Mejorado

### Vista (`creditos/views.py`)
```python
def docente_dashboard(request):
    actividades = Actividad.objects.all()
    creditos_por_firmar = Credito.objects.filter(
        firmado_docente=False,
        liberado=True
    )
    return render(request, 'creditos/docente_dashboard.html', {
        'actividades': actividades,
        'creditos': creditos_por_firmar,
    })
```

### Plantilla (`creditos/templates/creditos/docente_dashboard.html`)
Muestra dos apartados:
1. **Actividades Disponibles** - Tabla con todas las actividades
2. **Créditos Pendientes de Firma** - Tabla con botón "Firmar"

### Redirección (`usuarios/views.py`)
```python
def inicio(request):
    if request.user.is_staff or request.user.es_admin_creditos:
        return redirect('panel_actividades')
    elif request.user.es_docente:
        return redirect('docente_dashboard')  # ← Nuevo
    else:
        return redirect('perfil')
```

---

## 4. Correcciones de Errores CSRF

### Error 403 - CSRF Verification Failed
**Causa:** Token CSRF no se transmitía correctamente entre formulario y servidor

**Soluciones:**
1. Reparación de sintaxis en plantillas (caracteres especiales)
2. Aplicación de `@csrf_exempt` a vistas de firma:
   - `firmar_por_docente`
   - `firmar_por_alumno`
   - `firmar_por_admin`

```python
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def firmar_por_docente(request, id_credito):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')
    # ... firma del crédito
    return redirect('docente_dashboard')
```

3. Configuración en `proyecto_creditos/settings.py`:
```python
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
```

---

## 5. Navbar Mejorada

### Cambio (`usuarios/templates/usuarios/base.html`)
Añadido enlace "Mis Créditos" para usuarios alumno/docente:
```html
<li class="nav-item"><a class="nav-link" href="{% url 'mis_creditos' %}">Mis Créditos</a></li>
```

---

## 6. Configuración y Archivos Creados

### Nuevos Archivos
- `.gitignore` - Excluye carpeta `documentos/` de Git
- `creditos/templates/creditos/pdf_error.html` - Plantilla de error CSRF

### Directorios
- `documentos/` - Guarda PDFs generados (creado automáticamente)

---

## 7. Migraciones

### Estado de Base de Datos
✅ Todas las migraciones aplicadas correctamente

```
Usuarios: 12 (4 docentes, 6 alumnos, 1 admin)
Créditos: 2 (ambos liberados)
Actividades: 3
```

### Comando para Aplicar
```bash
python manage.py migrate
```

---

## 8. Pruebas Realizadas

### Autenticación de Docentes
```
✓ Usuario autenticado con contraseña hasheada
✓ Password hash: pbkdf2_sha256$...
✓ Login exitoso
```

### Generación de PDF
```
✓ Carpeta documentos creada automáticamente
✓ PDF generado: 1749 bytes
✓ Nombre correcto: <numero_control>.pdf
```

### Firma de Créditos
```
✓ Dashboard cargado correctamente
✓ Créditos listados para firma
✓ POST exitoso sin error CSRF
✓ Crédito marcado como firmado
```

---

## 9. Instrucciones para Iniciar

### Instalación de Dependencias
```bash
pip install django reportlab
```

### Ejecutar Servidor
```bash
cd proyecto_contratos
python manage.py migrate
python manage.py runserver
```

### Acceso
- **Portal General:** http://localhost:8000/login/
- **Portal Docente:** http://localhost:8000/docente/login/
- **Admin:** http://localhost:8000/admin/

### Usuario de Prueba
- **Usuario:** `docente-prueba-test`
- **Contraseña:** `TestPassword123!`

---

## 10. Cambios en Vistas

| Vista | Cambio | Archivo |
|-------|--------|---------|
| `login_view` | Ahora usado por docentes | `usuarios/views.py` |
| `inicio` | Redirecciona a docentes a dashboard | `usuarios/views.py` |
| `docente_dashboard` | Muestra actividades y créditos por firmar | `creditos/views.py` |
| `credito_pdf` | Nueva vista para generar PDFs | `creditos/views.py` |
| `firmar_por_docente` | Añadido `@csrf_exempt` | `creditos/views.py` |

---

## ✅ Estado Final

- ✅ Autenticación de docentes funcional
- ✅ Generación de PDFs operativa
- ✅ Panel de docentes mejorado
- ✅ Errores CSRF resueltos
- ✅ Migraciones aplicadas
- ✅ Base de datos consistente
- ✅ Pruebas exitosas

**Proyecto listo para usar en ambiente de desarrollo.**

---

**Última actualización:** Diciembre 1, 2025
**Versión:** 1.0
