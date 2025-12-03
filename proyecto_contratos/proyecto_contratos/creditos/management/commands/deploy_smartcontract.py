from django.core.management.base import BaseCommand, CommandError
import json
import os


class Command(BaseCommand):
    help = 'Despliega el smart contract de Algorand usando proyecto_creditos/src/SmartContract1.deploy_contract'

    def add_arguments(self, parser):
        parser.add_argument('--admin-mnemonic', dest='admin_mn', help='Mnemonic del admin (opcional, usa el de SmartContract1 si no se proporciona)')
        parser.add_argument('--student-mnemonic', dest='student_mn', help='Mnemonic del student (opcional)')
        parser.add_argument('--officer-mnemonic', dest='officer_mn', help='Mnemonic del officer (opcional)')
        parser.add_argument('--doc-path', dest='doc_path', help='Ruta al PDF a incluir en el contrato (por defecto: docs/plan_estudios.pdf en repo)', default=None)
        parser.add_argument('--teal-dir', dest='teal_dir', help='Directorio donde están los archivos .teal (opcional)')
        parser.add_argument('--save-to', dest='save_to', help='Guardar resultado JSON con app_id en esta ruta (opcional)')

    def handle(self, *args, **options):
        # Import here to avoid heavy imports during manage.py boot
        try:
            from proyecto_creditos.src import SmartContract1
        except Exception as e:
            raise CommandError(f'No se pudo importar SmartContract1: {e}')

        admin_mn = options.get('admin_mn') or getattr(SmartContract1, 'ADMIN_MNEMONIC', None)
        student_mn = options.get('student_mn') or getattr(SmartContract1, 'STUDENT_MNEMONIC', None)
        officer_mn = options.get('officer_mn') or getattr(SmartContract1, 'OFFICER_MNEMONIC', None)
        doc_path = options.get('doc_path') or os.path.join(os.getcwd(), 'docs', 'plan_estudios.pdf')
        teal_dir = options.get('teal_dir')

        if not admin_mn or not student_mn or not officer_mn:
            self.stdout.write(self.style.WARNING('Aviso: no se proporcionaron todos los mnemonics; usando valores embebidos en SmartContract1 si existen.'))

        if not os.path.exists(doc_path):
            raise CommandError(f'Documento no encontrado: {doc_path}')

        self.stdout.write('Iniciando despliegue del contrato (esto puede tardar)...')
        try:
            app_id, doc_hash = SmartContract1.deploy_contract(admin_mn, student_mn, officer_mn, doc_path, teal_dir=teal_dir)
        except Exception as e:
            raise CommandError(f'Error durante deploy: {e}')

        result = {
            'app_id': app_id,
            'doc_hash': doc_hash.hex() if isinstance(doc_hash, (bytes, bytearray)) else str(doc_hash),
            'doc_path': os.path.abspath(doc_path),
        }

        self.stdout.write(self.style.SUCCESS(f'Despliegue completado. app_id={app_id}'))
        self.stdout.write(json.dumps(result, indent=2))

        save_to = options.get('save_to')
        if save_to:
            try:
                with open(save_to, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2)
                self.stdout.write(self.style.SUCCESS(f'Resultado guardado en: {save_to}'))
            except Exception as e:
                raise CommandError(f'No se pudo guardar resultado: {e}')

        # Show snippet to add to settings.py
        self.stdout.write('\nSugerencia: añade a `settings.py` lo siguiente (usa APP_ID obtenido):')
        self.stdout.write("""
SMART_CONTRACT = {
    'ENABLED': True,
    'APP_ID': %s,
    'SIGNER_MNEMONIC': '<tu_mnemonic_para_firmar_si_deseas>'
}
""" % app_id)
