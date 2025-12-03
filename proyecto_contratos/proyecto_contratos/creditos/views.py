from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from usuarios.models import Usuario
from actividades.models import Actividad
from .models import Credito, SolicitudCredito
from django.http import HttpResponseForbidden
from django.db.models import Q



@login_required
def crear_credito(request):
    usuarios = Usuario.objects.filter(es_alumno=True)
    actividades = Actividad.objects.all().order_by("nombre")

    if request.method == "POST":
        alumno_id = request.POST.get("alumno_id")
        actividad_id = request.POST.get("actividad_id")
        nombre_manual = request.POST.get("nombre")
        tipo = request.POST.get("tipo")
        semestre = request.POST.get("semestre")
        fecha_liberacion = request.POST.get("fecha_liberacion")

        alumno = Usuario.objects.get(id=alumno_id)
        numero = alumno.numero_control

        # Si se seleccionó actividad, usar su nombre (incluir convo si existe)
        if actividad_id:
            actividad = Actividad.objects.get(id=actividad_id)
            if getattr(actividad, 'convo', None):
                nombre_final = f"{actividad.nombre} {actividad.convo}"
            else:
                nombre_final = actividad.nombre
        else:
            nombre_final = nombre_manual

        Credito.objects.create(
            alumno=alumno,
            nombre=nombre_final,
            tipo=tipo,
            semestre=semestre,
            numero_control=numero,
            fecha_liberacion=fecha_liberacion,
        )

        return redirect("mis_creditos")

@login_required
def mis_creditos(request):
    user = request.user
    # Mostrar créditos asignados al usuario o créditos sin alumno pero con número de control igual al usuario
    qs = Q(alumno=user)
    if getattr(user, 'numero_control', None):
        qs = qs | (Q(alumno__isnull=True) & Q(numero_control=user.numero_control))
    creditos = Credito.objects.filter(qs).order_by('-id')
    return render(request, 'creditos/mis_creditos.html', {
        'creditos': creditos
    })
    qs = Q(alumno=user)
    if getattr(user, 'numero_control', None):
        qs = qs | (Q(alumno__isnull=True) & Q(numero_control=user.numero_control))
    creditos = Credito.objects.filter(qs).order_by('-id')
    return render(request, 'creditos/mis_creditos.html', {
        'creditos': creditos
    })


@login_required
def asignar_credito(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)

    # If confirm posted, perform assignment
    if request.method == 'POST' and request.POST.get('confirm'):
        alumno_id = request.POST.get('alumno_id')
        try:
            alumno = Usuario.objects.get(id=alumno_id)
        except Usuario.DoesNotExist:
            messages.error(request, 'Alumno no encontrado para la confirmación.')
            return redirect('asignar_credito', id_credito)

        credito.alumno = alumno
        credito.numero_control = alumno.numero_control
        credito.liberado = True
        credito.fecha_liberacion = timezone.now().date()
        credito.save()
        messages.success(request, f'Crédito asignado y liberado a {alumno.username} ({alumno.numero_control}).')
        return redirect('lista_creditos_admin')

    confirm_user = None
    numero_control = request.POST.get('numero_control') or request.GET.get('numero_control')
    nombre = request.POST.get('nombre')

    # If a numero_control was provided, try exact match
    if numero_control:
        try:
            confirm_user = Usuario.objects.get(numero_control=numero_control, es_alumno=True)
        except Usuario.DoesNotExist:
            confirm_user = None
            messages.info(request, f'No se encontró alumno con número de control {numero_control}.')

    # If no exact match but a nombre partial provided, attempt search
    if not confirm_user and nombre:
        qs = Usuario.objects.filter(username__icontains=nombre, es_alumno=True)
        if qs.count() == 1:
            confirm_user = qs.first()
        elif qs.count() > 1:
            # take first but notify
            confirm_user = qs.first()
            messages.info(request, 'Se encontraron varias coincidencias; usando la primera.')

    return render(request, 'creditos/asignar_credito.html', {
        'credito': credito,
        'confirm_user': confirm_user,
        'numero_control': numero_control,
        'nombre': nombre,
    })


@login_required
def panel_creditos(request):
    creditos = Credito.objects.all().order_by('-id')
    return render(request, 'creditos/panel_creditos.html', {'creditos': creditos})


@login_required
def lista_creditos_admin(request):
    creditos = Credito.objects.all().order_by('-id')
    return render(request, 'creditos/lista_creditos_admin.html', {'creditos': creditos})


@login_required
def solicitar_credito(request):
    if request.method == 'POST':
        # Minimal handling: create a SolicitudCredito if posted
        alumno = request.user
        nombre = request.POST.get('nombre')
        tipo = request.POST.get('tipo')
        semestre = request.POST.get('semestre')
        numero_control = request.POST.get('numero_control', alumno.numero_control if hasattr(alumno, 'numero_control') else '')
        SolicitudCredito.objects.create(alumno=alumno, nombre=nombre, tipo=tipo, semestre=semestre, numero_control=numero_control)
        messages.success(request, 'Solicitud enviada.')
        return redirect('mis_creditos')
    return render(request, 'creditos/solicitar_credito.html')


@login_required
def lista_solicitudes(request):
    solicitudes = SolicitudCredito.objects.all().order_by('-creado_en')
    return render(request, 'creditos/lista_solicitudes.html', {'solicitudes': solicitudes})


@login_required
def aprobar_solicitud(request, id_solicitud):
    s = get_object_or_404(SolicitudCredito, id=id_solicitud)
    s.estado = 'aprobado'
    s.revisado_por = request.user
    s.revisado_en = timezone.now()
    s.save()
    messages.success(request, 'Solicitud aprobada.')
    return redirect('lista_solicitudes')


@login_required
def rechazar_solicitud(request, id_solicitud):
    s = get_object_or_404(SolicitudCredito, id=id_solicitud)
    s.estado = 'rechazado'
    s.revisado_por = request.user
    s.revisado_en = timezone.now()
    s.save()
    messages.success(request, 'Solicitud rechazada.')
    return redirect('lista_solicitudes')


@login_required
def contrato(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    return render(request, 'creditos/contrato.html', {'credito': credito})


@login_required
def liberar_credito(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')
    credito.liberado = True
    credito.fecha_liberacion = timezone.now().date()
    credito.save()
    messages.success(request, 'Crédito liberado.')
    return redirect('lista_creditos_admin')


@login_required
def eliminar_credito(request, id_credito):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')
    credito = get_object_or_404(Credito, id=id_credito)
    credito.delete()
    messages.success(request, 'Crédito eliminado.')
    return redirect('lista_creditos_admin')


@login_required
def lista_creditos_docente(request):
    creditos = Credito.objects.all().order_by('-id')
    return render(request, 'creditos/lista_creditos_docente.html', {'creditos': creditos})


@login_required
def docente_asignar(request):
    """Lista de créditos para que el docente pueda asignar (liberar) a alumnos.
    Solo accesible para usuarios con `es_docente=True`.
    """
    if not request.user.es_docente:
        return HttpResponseForbidden('Permisos insuficientes')

    creditos = Credito.objects.filter(liberado=False).order_by('-id')
    return render(request, 'creditos/lista_creditos_docente_asignar.html', {'creditos': creditos})


@login_required
def docente_liberar_credito(request, id_credito):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')

    if not getattr(request.user, 'es_docente', False):
        return HttpResponseForbidden('Permisos insuficientes')

    credito = get_object_or_404(Credito, id=id_credito)
    credito.liberado = True
    credito.fecha_liberacion = timezone.now().date()
    credito.save()
    messages.success(request, 'Crédito liberado por docente.')
    return redirect('docente_asignar')


@login_required
def firmar_por_docente(request, id_credito):
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')
    
    credito = get_object_or_404(Credito, id=id_credito)
    # El docente solo puede firmar si el crédito fue asignado por el admin (liberado)
    if not credito.liberado:
        messages.error(request, 'El crédito no ha sido liberado por el administrador aún.')
        return redirect('docente_dashboard')
    
    credito.firmado_docente = True
    credito.firmado_docente_por = request.user
    credito.firmado_docente_en = timezone.now()
    credito.save()
    messages.success(request, 'Crédito firmado por docente.')
    return redirect('docente_dashboard')


@login_required
def firmar_por_alumno(request, id_credito):
    # Sólo aceptar POST para firmar
    if request.method != 'POST':
        return HttpResponseForbidden('Use POST')

    credito = get_object_or_404(Credito, id=id_credito)

    # Verificar que el usuario es el alumno asignado o que el número de control coincide
    usuario = request.user
    numero_ok = credito.numero_control and usuario.numero_control and credito.numero_control.strip() == usuario.numero_control.strip()
    if not (credito.alumno == usuario or numero_ok):
        messages.error(request, 'No tienes permiso para firmar este crédito.')
        return redirect('mis_creditos')

    # Si el crédito no tiene alumno asignado, asignarlo al firmante
    if credito.alumno is None:
        credito.alumno = usuario

    credito.firmado_alumno = True
    credito.firmado_alumno_por = usuario
    credito.firmado_alumno_en = timezone.now()
    credito.save()
    messages.success(request, 'Crédito firmado por alumno.')
    return redirect('mis_creditos')


@login_required
def firmar_por_admin(request, id_credito):
    credito = get_object_or_404(Credito, id=id_credito)
    credito.firmado_admin = True
    credito.firmado_admin_por = request.user
    credito.firmado_admin_en = timezone.now()
    credito.save()
    messages.success(request, 'Crédito firmado por admin.')
    return redirect('lista_creditos_admin')


from usuarios.views import login_view as usuarios_login_view


def docente_login(request):
    # Delegate to the usuarios app login_view so behaviour and templates stay consistent
    return usuarios_login_view(request)


@login_required
def docente_dashboard(request):
    # Obtener todas las actividades
    actividades = Actividad.objects.all().order_by('nombre')
    
    # Obtener créditos pendientes de firma por el docente:
    # - El crédito debe estar liberado (asignado por admin)
    # - Aún no ha sido firmado por el docente (firmado_docente = False)
    creditos_por_firmar = Credito.objects.filter(
        liberado=True,
        firmado_docente=False
    ).order_by('-id')
    
    return render(request, 'creditos/docente_dashboard.html', {
        'actividades': actividades,
        'creditos': creditos_por_firmar,
    })


@login_required
def wallet(request):
    return render(request, 'creditos/wallet.html')


@login_required
def credito_pdf(request, id_credito):
    """Descarga el PDF de plan de estudios firmado (desde proyecto_creditos/src/docs/plan_estudios.pdf).

    Solo se descarga si AMBOS (alumno y docente) han firmado el crédito.
    """
    import os
    from pathlib import Path
    from django.http import HttpResponse
    from django.conf import settings

    credito = get_object_or_404(Credito, id=id_credito)

    # Solo el alumno propietario puede descargar su PDF
    if credito.alumno != request.user:
        messages.error(request, 'No tienes permiso para descargar este documento.')
        return redirect('mis_creditos')
    
    # El PDF solo se descarga si AMBOS firman (alumno Y docente)
    if not (credito.firmado_alumno and credito.firmado_docente):
        messages.error(request, 'El crédito debe estar firmado por ti (alumno) y por el docente para descargar el PDF.')
        return redirect('mis_creditos')

    # Ubicar el PDF en proyecto_creditos/src/docs/plan_estudios.pdf
    pdf_path = Path(settings.BASE_DIR).parent / 'proyecto_creditos' / 'src' / 'docs' / 'plan_estudios.pdf'
    
    # Si no existe en esa ruta, intentar buscar en ruta relativa
    if not pdf_path.exists():
        pdf_path = Path(settings.BASE_DIR) / 'proyecto_creditos' / 'src' / 'docs' / 'plan_estudios.pdf'
    
    if not pdf_path.exists():
        messages.error(request, 'El archivo PDF no se encontró en el servidor.')
        return redirect('mis_creditos')

    # Crear carpeta documentos si no existe (en la raíz del proyecto, al lado de manage.py)
    docs_dir = Path(settings.BASE_DIR) / 'documentos'
    docs_dir.mkdir(exist_ok=True)

    # Leer el PDF del servidor
    try:
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
    except Exception as e:
        messages.error(request, f'Error al leer el PDF: {e}')
        return redirect('mis_creditos')

    # Si tanto alumno como docente firmaron, generar una página de firmas y anexarla
    if credito.firmado_alumno and credito.firmado_docente:
        try:
            import io
            # Crear página de firma con ReportLab
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4
            except Exception:
                raise RuntimeError('ReportLab no está instalado; instala reportlab para generar firmas en PDF')

            sig_buf = io.BytesIO()
            c = canvas.Canvas(sig_buf, pagesize=A4)
            c.setFont('Helvetica-Bold', 14)
            c.drawString(72, 800, 'Firmas del Contrato')
            c.setFont('Helvetica', 12)
            y = 760
            # Datos de firma alumno
            alumno_name = credito.firmado_alumno_por.get_full_name() if credito.firmado_alumno_por else (credito.alumno.get_full_name() if credito.alumno else '')
            alumno_time = credito.firmado_alumno_en.strftime('%Y-%m-%d %H:%M:%S') if credito.firmado_alumno_en else ''
            c.drawString(72, y, f'Alumno: {alumno_name}'); y -= 20
            c.drawString(72, y, f'Firmado en: {alumno_time}'); y -= 30

            # Datos de firma docente
            docente_name = credito.firmado_docente_por.get_full_name() if credito.firmado_docente_por else ''
            docente_time = credito.firmado_docente_en.strftime('%Y-%m-%d %H:%M:%S') if credito.firmado_docente_en else ''
            c.drawString(72, y, f'Docente: {docente_name}'); y -= 20
            c.drawString(72, y, f'Firmado en: {docente_time}'); y -= 30

            # Añadir sello/nota
            c.setFont('Helvetica-Oblique', 10)
            c.drawString(72, y, 'Este documento está firmado electrónicamente por alumno y docente según registro interno.')
            c.showPage(); c.save()
            sig_buf.seek(0)

            # Intentar concatenar usando PyPDF2
            try:
                from PyPDF2 import PdfReader, PdfWriter
            except Exception:
                raise RuntimeError('PyPDF2 no está instalado; instala PyPDF2 para combinar PDFs')

            reader_orig = PdfReader(io.BytesIO(pdf_content))
            reader_sig = PdfReader(sig_buf)
            writer = PdfWriter()
            for p in reader_orig.pages:
                writer.add_page(p)
            for p in reader_sig.pages:
                writer.add_page(p)

            out_buf = io.BytesIO()
            writer.write(out_buf)
            pdf_content = out_buf.getvalue()
        except Exception as e:
            # Si algo falla, seguimos con el PDF original y registramos advertencia
            print('No se pudo anexar página de firmas:', e)

    # Nombre único por crédito: número de control + id del crédito
    numero_control = request.user.numero_control or request.user.username
    safe_num = (str(numero_control).replace(' ', '_'))
    filename = f"{safe_num}-credito-{credito.id}.pdf"
    filepath = docs_dir / filename

    # Guardar una copia en la carpeta documentos del proyecto para registro
    try:
        with open(filepath, 'wb') as f:
            f.write(pdf_content)
    except Exception as e:
        messages.warning(request, f'No se pudo guardar copia en documentos: {e}')

    # También guardar una copia en la carpeta 'Documents' del usuario del sistema (si existe)
    try:
        user_docs = Path.home() / 'Documents'
        user_docs.mkdir(parents=True, exist_ok=True)
        user_filepath = user_docs / filename
        with open(user_filepath, 'wb') as f2:
            f2.write(pdf_content)
    except Exception:
        # No bloquear si no se pudo escribir en Documents; sólo informamos con mensaje opcional
        user_filepath = None
    # If SMART_CONTRACT is enabled, generate a smart-contract PDF that includes
    # TEAL sources and metadata. If DEPLOY_PER_CREDITO is True, attempt deploy
    # and include the returned app_id/doc_hash; otherwise include APP_ID from settings.
    sc_cfg = getattr(settings, 'SMART_CONTRACT', None) or {}
    if sc_cfg.get('ENABLED'):
        try:
            # Prepare metadata
            import hashlib
            from proyecto_creditos.src import SmartContract1

            app_id = sc_cfg.get('APP_ID')
            doc_hash = hashlib.sha256(pdf_content).digest()

            # If configured to deploy per crédito, attempt to deploy using mnemonics
            if sc_cfg.get('DEPLOY_PER_CREDITO'):
                admin_m = sc_cfg.get('ADMIN_MNEMONIC') or None
                student_m = sc_cfg.get('STUDENT_MNEMONIC') or None
                officer_m = sc_cfg.get('OFFICER_MNEMONIC') or None
                try:
                    deployed_app_id, deployed_doc_hash = SmartContract1.deploy_contract(
                        admin_m, student_m, officer_m, str(filepath)
                    )
                    app_id = deployed_app_id
                    doc_hash = deployed_doc_hash
                except Exception as e:
                    print('Warning: deploy per crédito failed:', e)
                    messages.warning(request, f'Despliegue del contrato por crédito falló: {e}')

            # Optionally sign on-chain with SIGNER_MNEMONIC
            signer_m = sc_cfg.get('SIGNER_MNEMONIC')
            if signer_m and app_id:
                try:
                    signer_sk, signer_addr = SmartContract1.load_account(signer_m)
                    SmartContract1.sign_document(signer_sk, signer_addr, app_id, doc_hash)
                except Exception as e:
                    print('Warning: signing failed:', e)
                    messages.warning(request, f'Firma on-chain fallida: {e}')

            # Build smart-contract PDF with TEAL source
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4
            except Exception:
                messages.error(request, 'ReportLab no está instalado; instala reportlab para generar el contrato en PDF.')
                return redirect('mis_creditos')

            smart_filename = f"{safe_num}-credito-{credito.id}-smartcontract.pdf"
            smart_filepath = docs_dir / smart_filename
            c = canvas.Canvas(str(smart_filepath), pagesize=A4)
            c.setFont('Helvetica-Bold', 14)
            c.drawString(72, 800, 'Contrato Inteligente - Información')
            c.setFont('Helvetica', 11)
            y = 780
            meta_lines = [
                f'Alumno: {request.user.get_full_name() or request.user.username}',
                f'Número de control: {numero_control}',
                f'Crédito: {credito.nombre}',
                f'Tipo: {credito.get_tipo_display()}',
                f'Semestre: {credito.semestre}',
                f'Fecha de liberación: {credito.fecha_liberacion or "--"}',
                f'App ID: {app_id or "(no deploy)"}',
                f'Doc hash: {doc_hash.hex() if isinstance(doc_hash, (bytes, bytearray)) else str(doc_hash)}',
            ]
            for ln in meta_lines:
                c.drawString(72, y, ln)
                y -= 16
                if y < 72:
                    c.showPage(); y = 800

            # Attach TEAL sources (read-only, do not move files)
            try:
                teal_dir = os.path.abspath(os.path.join(os.path.dirname(SmartContract1.__file__), '..', 'teal'))
                if os.path.isdir(teal_dir):
                    c.showPage(); c.setFont('Helvetica-Bold', 12); c.drawString(72, 800, 'TEAL Source Files:')
                    y = 780; c.setFont('Courier', 8)
                    for fname in sorted(os.listdir(teal_dir)):
                        if not fname.endswith('.teal'):
                            continue
                        path_teal = os.path.join(teal_dir, fname)
                        c.drawString(72, y, f'--- {fname} ---')
                        y -= 12
                        with open(path_teal, 'r', encoding='utf-8', errors='ignore') as tf:
                            for line in tf:
                                # wrap long lines
                                for chunk in [line[i:i+100] for i in range(0, len(line), 100)]:
                                    c.drawString(72, y, chunk.rstrip())
                                    y -= 10
                                    if y < 72:
                                        c.showPage(); c.setFont('Courier', 8); y = 800
                        y -= 8
            except Exception as e:
                print('No se pudieron adjuntar archivos TEAL:', e)

            c.showPage(); c.save()

            # Save a copy to user's Documents as well
            try:
                if smart_filepath.exists():
                    user_smart = Path.home() / 'Documents' / smart_filepath.name
                    with open(smart_filepath, 'rb') as srf, open(user_smart, 'wb') as usf:
                        usf.write(srf.read())
            except Exception:
                pass

            # Return the smart-contract PDF
            try:
                with open(smart_filepath, 'rb') as sf:
                    data = sf.read()
                response = HttpResponse(data, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{smart_filepath.name}"'
                messages.success(request, f'Contrato inteligente generado: {smart_filepath.name}')
                return response
            except Exception as e:
                messages.error(request, f'Error al preparar la descarga del smart contract: {e}')
                return redirect('mis_creditos')

        except Exception as e:
            print('Error al generar contrato inteligente:', e)
            messages.warning(request, f'No se pudo generar contrato inteligente: {e}')

    # If not enabled or generation failed, return the base PDF
    try:
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        if user_filepath:
            messages.success(request, f'PDF descargado y guardado en: {user_filepath}')
        else:
            messages.success(request, f'PDF descargado: {filename}')
        return response
    except Exception as e:
        messages.error(request, f'Error al preparar la descarga: {e}')
        return redirect('mis_creditos')

