import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
from app.core.config import settings
import os
import json
import traceback
from datetime import datetime, timedelta


class GoogleSheetsService:
    def __init__(self):
        self.client = None
        self.sheet = None
        self.spreadsheets = {}  # Cache de spreadsheets abiertos
        # Cache de datos con expiración
        self._cache_menciones = None
        self._cache_menciones_timestamp = None
        self._cache_clientes = None
        self._cache_clientes_timestamp = None
        self._cache_ttl = timedelta(minutes=5)  # Cache válido por 5 minutos
        self._connect()
    
    def _connect(self):
        """Conecta a Google Sheets usando service account"""
        try:
            print("🔍 [DEBUG] Iniciando conexión a Google Sheets...", flush=True)
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            creds = None
            
            # Log de variables para depuración en Render
            print(f"🔍 [DEBUG] GOOGLE_SA_FILE env: {os.getenv('GOOGLE_SA_FILE')}", flush=True)
            print(f"🔍 [DEBUG] settings.SERVICE_ACCOUNT_FILE: {settings.SERVICE_ACCOUNT_FILE}", flush=True)
            
            # 1. Intentar por archivo (Secret File en Render)
            target_file = settings.SERVICE_ACCOUNT_FILE or '/etc/secrets/GOOGLE_SERVICE_ACCOUNT'
            if os.path.exists(target_file):
                try:
                    creds = Credentials.from_service_account_file(target_file, scopes=scopes)
                    print(f"✅ [GOOGLE SHEETS] Conectado usando archivo: {target_file}", flush=True)
                except Exception as e:
                    print(f"⚠️ [GOOGLE SHEETS] Error cargando archivo {target_file}: {e}", flush=True)
            else:
                print(f"❌ [DEBUG] El archivo secreto NO existe en: {target_file}", flush=True)

            # 2. Intentar por JSON directo (Variable de entorno)
            if not creds:
                json_data = settings.SERVICE_ACCOUNT_JSON or os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON') or os.getenv('GOOGLE_SERVICE_ACCOUNT')
                if json_data and '{' in json_data:
                    try:
                        info = json.loads(json_data.strip())
                        if 'private_key' in info:
                            info['private_key'] = info['private_key'].replace('\\n', '\n')
                        creds = Credentials.from_service_account_info(info, scopes=scopes)
                        print("✅ Credenciales cargadas desde JSON directo")
                    except Exception as e:
                        print(f"⚠️ Error cargando JSON directo: {e}")

            if not creds:
                print("❌ No se pudieron cargar credenciales de Google Sheets")
                raise ValueError("Credenciales no disponibles")

            self.client = gspread.authorize(creds)
            
            # Inicializar spreadsheets principales
            for key, config in settings.SHEETS.items():
                try:
                    self.spreadsheets[key] = self.client.open_by_key(config['id'])
                    print(f"✅ Spreadsheet '{key}' abierto correctamente")
                except Exception as e:
                    print(f"⚠️ Error abriendo spreadsheet '{key}': {e}")
            
            # Set default sheet (certificados)
            if 'certificados' in self.spreadsheets:
                self.sheet = self.spreadsheets['certificados'].sheet1
            
            print("🚀 Conexión a Google Sheets completada exitosamente")

        except Exception as e:
            print(f"🛑 ERROR CRÍTICO EN CONEXIÓN A GOOGLE SHEETS: {e}")
            traceback.print_exc()
            # No levantamos excepción para que la app no muera, pero el servicio no funcionará
            self.client = None
            raise Exception(f"Error conectando a Google Sheets: {str(e)}")
    
    def get_all_certificates(self) -> List[Dict]:
        """Obtiene todos los certificados desde la hoja principal"""
        try:
            records = self.sheet.get_all_records()
            return records
        except Exception as e:
            raise Exception(f"Error obteniendo certificados: {str(e)}")
    
    def get_all_certificates_qr(self) -> List[Dict]:
        """Obtiene todos los certificados desde la hoja CERTIFICADOS QR"""
        try:
            # Obtener el spreadsheet de certificados
            spreadsheet = self.spreadsheets.get('certificados')
            if not spreadsheet:
                sheet_id = settings.SHEETS['certificados']['id']
                spreadsheet = self.client.open_by_key(sheet_id)
                self.spreadsheets['certificados'] = spreadsheet
            
            # Obtener la hoja CERTIFICADOS QR
            worksheet_qr = spreadsheet.worksheet('CERTIFICADOS QR')
            records = worksheet_qr.get_all_records()
            
            # Mapear los campos de CERTIFICADOS QR al formato esperado por el frontend
            certificados_mapeados = []
            for record in records:
                # Separar nombre completo en nombres y apellidos
                nombre_completo = record.get('NOMBRE COMPLETO DEL CLIENTE', '') or record.get('NOMBRE COMPLETO', '') or ''
                nombres = ''
                apellidos = ''
                if nombre_completo:
                    partes = nombre_completo.split(' ', 1)
                    if len(partes) >= 2:
                        nombres = partes[0]
                        apellidos = ' '.join(partes[1:])
                    else:
                        nombres = nombre_completo
                
                certificado_mapeado = {
                    'codigo': record.get('CODIGO', '') or record.get('codigo', ''),
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'dni': record.get('DNI DEL CLIENTE', '') or record.get('DNI', '') or record.get('dni', ''),
                    'curso': record.get('CURSO', '') or record.get('curso', ''),
                    'fecha_emision': record.get('FECHA EMISION', '') or record.get('FECHA EMISIÓN', '') or record.get('fecha_emision', ''),
                    'horas': record.get('HORAS', '') or record.get('horas', ''),
                    'estado': record.get('ESTADO', 'VALIDO') or record.get('estado', 'VALIDO'),
                    'pdf_url': record.get('PDF_URL', '') or record.get('pdf_url', ''),
                    # Campos adicionales de CERTIFICADOS QR
                    'nombre_completo': nombre_completo,
                    'celular': record.get('CELULAR DEL CLIENTE', '') or record.get('celular', ''),
                    'correo': record.get('CORREO DEL CLIENTE', '') or record.get('correo', ''),
                    'nro': record.get('NRO', '') or record.get('nro', ''),
                    'especialidad': record.get('ESPECIALIDAD', '') or record.get('especialidad', ''),
                    'p_certificado': record.get('P. CERTIFICADO', '') or record.get('p_certificado', ''),
                    'mencion': record.get('MENCIÓN', '') or record.get('mencion', ''),
                    'f_inicio': record.get('F. INICIO', '') or record.get('f_inicio', ''),
                    'f_termino': record.get('F. TÉRMINO', '') or record.get('f_termino', ''),
                }
                certificados_mapeados.append(certificado_mapeado)
            
            return certificados_mapeados
        except Exception as e:
            raise Exception(f"Error obteniendo certificados desde CERTIFICADOS QR: {str(e)}")
    
    def get_certificate_by_code(self, codigo: str) -> Optional[Dict]:
        """Busca un certificado por código en CERTIFICADOS QR"""
        try:
            print(f"DEBUG get_certificate_by_code: Buscando codigo={codigo}")
            # Buscar primero en CERTIFICADOS QR (donde se guardan los certificados ahora)
            spreadsheet = self.spreadsheets.get('certificados')
            if not spreadsheet:
                sheet_id = settings.SHEETS['certificados']['id']
                spreadsheet = self.client.open_by_key(sheet_id)
                self.spreadsheets['certificados'] = spreadsheet
            
            try:
                worksheet_qr = spreadsheet.worksheet('CERTIFICADOS QR')
                print(f"DEBUG get_certificate_by_code: Hoja CERTIFICADOS QR obtenida")
                records = worksheet_qr.get_all_records()
                print(f"DEBUG get_certificate_by_code: Total de registros en CERTIFICADOS QR: {len(records)}")
                
                for record in records:
                    # Buscar por código (puede estar en diferentes columnas)
                    codigo_record = (
                        record.get("CODIGO", "") or 
                        record.get("CÓDIGO", "") or 
                        record.get("codigo", "")
                    )
                    codigo_clean = str(codigo_record).strip() if codigo_record else ""
                    codigo_buscar = codigo.strip()
                    
                    print(f"DEBUG get_certificate_by_code: Comparando '{codigo_clean}' con '{codigo_buscar}'")
                    
                    if codigo_clean and codigo_clean.lower() == codigo_buscar.lower():
                        print(f"DEBUG get_certificate_by_code: Certificado encontrado!")
                        # Separar nombre completo en nombres y apellidos
                        nombre_completo = record.get('NOMBRE COMPLETO DEL CLIENTE', '') or record.get('NOMBRE COMPLETO', '') or ''
                        nombres = ''
                        apellidos = ''
                        if nombre_completo:
                            partes = nombre_completo.split(' ', 1)
                            if len(partes) >= 2:
                                nombres = partes[0]
                                apellidos = ' '.join(partes[1:])
                            else:
                                nombres = nombre_completo
                        
                        # Mapear a formato esperado (incluyendo todos los campos de la mención)
                        # Asegurar que horas sea string o None
                        horas_value = record.get('HORAS', '') or record.get('horas', '')
                        if horas_value:
                            horas_value = str(horas_value) if not isinstance(horas_value, str) else horas_value
                        else:
                            horas_value = None
                        
                        return {
                            'codigo': codigo_clean or '',
                            'nombres': nombres or '',
                            'apellidos': apellidos or '',
                            'nombre_completo': nombre_completo or '',
                            'dni': record.get('DNI DEL CLIENTE', '') or record.get('DNI', '') or record.get('dni', '') or '',
                            'curso': record.get('CURSO', '') or record.get('P. CERTIFICADO', '') or record.get('curso', '') or '',
                            'fecha_emision': record.get('FECHA EMISION', '') or record.get('FECHA EMISIÓN', '') or record.get('F. EMISIÓN', '') or record.get('fecha_emision', '') or '',
                            'horas': horas_value,
                            'estado': record.get('ESTADO', 'VALIDO') or record.get('estado', 'VALIDO') or 'VALIDO',
                            'pdf_url': record.get('PDF_URL', '') or record.get('PDF URL', '') or record.get('pdf_url', '') or None,
                            # Campos adicionales para el PDF con plantilla
                            'mencion': record.get('MENCIÓN', '') or record.get('mencion', '') or '',
                            'f_inicio': record.get('F. INICIO', '') or record.get('f_inicio', '') or '',
                            'f_termino': record.get('F. TÉRMINO', '') or record.get('F. TERMINO', '') or record.get('f_termino', '') or '',
                            'p_certificado': record.get('P. CERTIFICADO', '') or record.get('p_certificado', '') or '',
                        }
                
                print(f"DEBUG get_certificate_by_code: Certificado no encontrado en CERTIFICADOS QR")
            except gspread.exceptions.WorksheetNotFound:
                print(f"DEBUG get_certificate_by_code: Hoja CERTIFICADOS QR no encontrada")
                pass
            
            # Fallback: buscar en la hoja principal (por compatibilidad)
            print(f"DEBUG get_certificate_by_code: Buscando en hoja principal como fallback")
            records = self.sheet.get_all_records()
            for record in records:
                if record.get("codigo", "").strip().lower() == codigo.strip().lower():
                    print(f"DEBUG get_certificate_by_code: Certificado encontrado en hoja principal")
                    return record
            
            print(f"DEBUG get_certificate_by_code: Certificado no encontrado en ninguna hoja")
            return None
        except Exception as e:
            print(f"DEBUG get_certificate_by_code: Error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error buscando certificado: {str(e)}")
    
    def create_certificate(self, data: Dict, mencion_data: Optional[Dict] = None) -> Dict:
        """Crea un nuevo certificado en el Sheet y en CERTIFICADOS QR"""
        try:
            # Validar que el código esté presente
            if not data.get("codigo"):
                raise ValueError("El código del certificado es requerido")
            
            # Verificar que el código no exista
            existing = self.get_certificate_by_code(data["codigo"])
            if existing:
                raise ValueError(f"El código {data['codigo']} ya existe")
            
            # 1. Guardar en la hoja original (certificados)
            try:
                headers = self.sheet.row_values(1)
                if not headers:
                    raise Exception("La hoja de certificados no tiene headers definidos")
                
                row = []
                for header in headers:
                    value = data.get(header, "")
                    row.append(str(value) if value else "")
                
                print(f"DEBUG: Guardando en hoja certificados - Headers: {headers}")
                print(f"DEBUG: Datos a guardar: {data}")
                print(f"DEBUG: Fila preparada: {row}")
                
                self.sheet.append_row(row)
                print(f"DEBUG: Certificado guardado exitosamente en hoja principal")
            except Exception as e_main:
                print(f"ERROR guardando en hoja principal: {str(e_main)}")
                import traceback
                traceback.print_exc()
                raise Exception(f"Error guardando en hoja de certificados: {str(e_main)}")
            
            # 2. Guardar también en CERTIFICADOS QR con datos del cliente
            try:
                print(f"DEBUG: Intentando obtener hoja 'CERTIFICADOS QR' del spreadsheet de certificados")
                print(f"DEBUG: Spreadsheet ID: {settings.SHEETS['certificados']['id']}")
                
                # Obtener el spreadsheet de certificados
                spreadsheet = self.spreadsheets.get('certificados')
                if not spreadsheet:
                    sheet_id = settings.SHEETS['certificados']['id']
                    spreadsheet = self.client.open_by_key(sheet_id)
                    self.spreadsheets['certificados'] = spreadsheet
                
                # Listar todas las hojas disponibles para debug
                available_sheets = [ws.title for ws in spreadsheet.worksheets()]
                print(f"DEBUG: Hojas disponibles en el spreadsheet: {available_sheets}")
                
                # Obtener la hoja CERTIFICADOS QR
                worksheet_qr = spreadsheet.worksheet('CERTIFICADOS QR')
                print(f"DEBUG: OK - Hoja 'CERTIFICADOS QR' obtenida exitosamente")
                
                # Obtener headers de la fila 1
                # Verificar si la hoja tiene datos
                all_values = worksheet_qr.get_all_values()
                print(f"DEBUG: Total de filas en la hoja: {len(all_values)}")
                
                # Obtener headers de la fila 1
                headers_qr = worksheet_qr.row_values(1) if len(all_values) > 0 else []
                print(f"DEBUG: Headers de CERTIFICADOS QR (fila 1): {headers_qr}")
                
                # Si no hay headers o la hoja está vacía, crear headers básicos en la fila 1
                if not headers_qr or all(not h.strip() for h in headers_qr if h):
                    print(f"DEBUG: La hoja no tiene headers validos, creando headers basicos en fila 1...")
                    headers_basicos = [
                        'CODIGO', 
                        'DNI DEL CLIENTE', 
                        'NOMBRE COMPLETO DEL CLIENTE', 
                        'CELULAR DEL CLIENTE',
                        'CORREO DEL CLIENTE',
                        'CURSO', 
                        'FECHA EMISION', 
                        'HORAS', 
                        'ESTADO', 
                        'PDF_URL',
                        'NRO',
                        'ESPECIALIDAD',
                        'P. CERTIFICADO',
                        'MENCIÓN',
                        'F. INICIO',
                        'F. TÉRMINO'
                    ]
                    
                    # Si la hoja está completamente vacía, usar append_row
                    # Si tiene algo pero no headers válidos, actualizar la fila 1
                    if len(all_values) == 0:
                        worksheet_qr.append_row(headers_basicos)
                        print(f"DEBUG: Headers creados con append_row (hoja vacia)")
                    else:
                        # Actualizar la fila 1 con los headers
                        for col_idx, header in enumerate(headers_basicos, start=1):
                            worksheet_qr.update_cell(1, col_idx, header)
                        print(f"DEBUG: Headers actualizados en fila 1")
                    
                    headers_qr = headers_basicos
                    print(f"DEBUG: Headers finales: {headers_qr}")
                
                # Obtener nombre completo: primero intentar desde 'nombre_completo' o 'NOMBRE COMPLETO DEL CLIENTE'
                # Si no está, combinar nombres + apellidos del formulario
                nombre_completo = (
                    data.get('nombre_completo', '') or 
                    data.get('NOMBRE COMPLETO DEL CLIENTE', '') or
                    data.get('nombreCompleto', '')
                )
                
                # Si no hay nombre completo directo, combinar nombres + apellidos
                if not nombre_completo:
                    nombres = data.get('nombres', '') or data.get('NOMBRES', '')
                    apellidos = data.get('apellidos', '') or data.get('APELLIDOS', '')
                    nombre_completo = f"{nombres} {apellidos}".strip()
                
                # Mapear los datos del certificado a los headers de CERTIFICADOS QR
                row_qr = []
                for header in headers_qr:
                    header_upper = header.upper().strip()
                    
                    # Mapear campos comunes
                    if header_upper in ['CODIGO', 'CÓDIGO', 'CODIGO CERTIFICADO']:
                        value = data.get('codigo', '') or data.get('CODIGO', '')
                    elif header_upper in ['DNI', 'DNI DEL CLIENTE', 'DNI CLIENTE']:
                        # Solo guardar DNI si está disponible
                        value = data.get('dni', '') or data.get('DNI', '') or ''
                    elif header_upper in ['NOMBRE COMPLETO', 'NOMBRE COMPLETO DEL CLIENTE', 'NOMBRE', 'CLIENTE', 'NOMBRES', 'APELLIDOS']:
                        # Para cualquier campo de nombre, usar nombre completo (un solo campo)
                        value = nombre_completo
                    elif header_upper in ['CELULAR DEL CLIENTE', 'CELULAR', 'TELEFONO', 'TELÉFONO', 'PHONE']:
                        value = (
                            data.get('CELULAR DEL CLIENTE', '')
                            or data.get('telefono', '')
                            or data.get('TELEFONO', '')
                            or data.get('CELULAR', '')
                        )
                    elif header_upper in ['CORREO DEL CLIENTE', 'CORREO', 'EMAIL', 'E-MAIL']:
                        value = (
                            data.get('CORREO DEL CLIENTE', '')
                            or data.get('email', '')
                            or data.get('EMAIL', '')
                            or data.get('CORREO', '')
                        )
                    elif header_upper in ['CURSO', 'NOMBRE DEL CURSO']:
                        value = data.get('curso', '') or data.get('CURSO', '')
                    elif header_upper in ['FECHA EMISION', 'FECHA DE EMISIÓN', 'FECHA EMISIÓN', 'FECHA']:
                        value = data.get('fecha_emision', '') or data.get('FECHA_EMISION', '') or data.get('FECHA EMISION', '')
                    elif header_upper in ['HORAS', 'HORAS TOTALES', 'TOTAL HORAS']:
                        # Priorizar horas de la mención si está disponible
                        value = data.get('mencion_horas', '') or data.get('horas', '') or data.get('HORAS', '') or (mencion_data.get('HORAS', '') if mencion_data else '')
                    elif header_upper in ['ESTADO', 'ESTADO CERTIFICADO']:
                        value = data.get('estado', 'VALIDO') or data.get('ESTADO', 'VALIDO')
                    elif header_upper in ['PDF_URL', 'PDF URL', 'URL PDF', 'URL']:
                        value = data.get('pdf_url', '') or data.get('PDF_URL', '')
                    elif header_upper in ['NRO', 'NRO MENCION', 'NUMERO MENCION', 'MENCIÓN NRO']:
                        # Número de la mención
                        value = data.get('mencion_nro', '') or (mencion_data.get('NRO', '') if mencion_data else '')
                    elif header_upper in ['ESPECIALIDAD', 'ESPECIALIDAD MENCION']:
                        # Especialidad de la mención
                        value = data.get('mencion_especialidad', '') or (mencion_data.get('ESPECIALIDAD', '') if mencion_data else '')
                    elif header_upper in ['P. CERTIFICADO', 'P CERTIFICADO', 'PROGRAMA CERTIFICADO', 'PROGRAMA']:
                        # Programa/Certificado de la mención
                        value = data.get('mencion_p_certificado', '') or (mencion_data.get('P. CERTIFICADO', '') if mencion_data else '')
                    elif header_upper in ['MENCIÓN', 'MENCION', 'TEXTO MENCION']:
                        # Texto completo de la mención
                        value = data.get('mencion_texto', '') or (mencion_data.get('MENCIÓN', '') if mencion_data else '')
                    elif header_upper in ['F. INICIO', 'FECHA INICIO', 'FECHA DE INICIO', 'F INICIO']:
                        # Fecha de inicio
                        value = data.get('fecha_inicio', '') or (mencion_data.get('F. INICIO', '') if mencion_data else '')
                    elif header_upper in ['F. TÉRMINO', 'F. TERMINO', 'FECHA TERMINO', 'FECHA DE TERMINO', 'F TERMINO']:
                        # Fecha de término
                        value = data.get('fecha_termino', '') or (mencion_data.get('F. TÉRMINO', '') if mencion_data else '')
                    # Nota: Se eliminó el campo "F. EMISIÓN" de la mención en CERTIFICADOS QR para evitar duplicidad con "FECHA EMISION".
                    else:
                        # Intentar buscar el valor directamente
                        value = data.get(header, '') or data.get(header.upper(), '') or data.get(header.lower(), '')
                    
                    row_qr.append(str(value) if value else "")
                
                # Agregar fila a CERTIFICADOS QR
                print(f"DEBUG: Preparando fila para CERTIFICADOS QR: {row_qr}")
                worksheet_qr.append_row(row_qr)
                print(f"DEBUG: OK - Certificado guardado exitosamente en CERTIFICADOS QR: codigo={data.get('codigo')}, nombre={nombre_completo}")
            except Exception as e_qr:
                # Si falla guardar en CERTIFICADOS QR, mostrar error detallado
                import traceback
                error_trace = traceback.format_exc()
                print(f"ERROR: No se pudo guardar en CERTIFICADOS QR: {str(e_qr)}")
                print(f"Traceback completo: {error_trace}")
                # NO fallar la creación del certificado principal, pero mostrar el error claramente
                # El certificado ya se guardó en la hoja principal, así que continuamos
            
            # Retornar el certificado creado
            try:
                certificado_creado = self.get_certificate_by_code(data["codigo"])
                if not certificado_creado:
                    # Si no se encuentra, retornar los datos que se enviaron
                    print(f"ADVERTENCIA: No se pudo recuperar el certificado recién creado, retornando datos enviados")
                    return data
                return certificado_creado
            except Exception as e_retrieve:
                print(f"ADVERTENCIA: Error recuperando certificado creado: {str(e_retrieve)}")
                # Retornar los datos que se enviaron como fallback
                return data
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            # Limpiar caracteres Unicode problemáticos del mensaje de error
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"ERROR completo en create_certificate: {error_msg}")
            print(f"Traceback completo: {error_trace.encode('ascii', 'ignore').decode('ascii')}")
            raise Exception(f"Error creando certificado: {error_msg}")
    
    def update_certificate(self, codigo: str, data: Dict) -> Dict:
        """Actualiza un certificado existente"""
        try:
            records = self.sheet.get_all_records()
            headers = self.sheet.row_values(1)
            
            # Encontrar la fila
            for idx, record in enumerate(records, start=2):  # start=2 porque row 1 es header
                if record.get("codigo", "").strip().lower() == codigo.strip().lower():
                    # Actualizar valores
                    for header in headers:
                        if header in data:
                            col_idx = headers.index(header) + 1
                            self.sheet.update_cell(idx, col_idx, str(data[header]))
                    return self.get_certificate_by_code(codigo)
            
            raise ValueError(f"Certificado con código {codigo} no encontrado")
        except Exception as e:
            raise Exception(f"Error actualizando certificado: {str(e)}")
    
    def anular_certificate(self, codigo: str, motivo: Optional[str] = None) -> Dict:
        """Anula un certificado cambiando su estado"""
        update_data = {"estado": "ANULADO"}
        if motivo:
            update_data["motivo_anulacion"] = motivo
        return self.update_certificate(codigo, update_data)
    
    def update_certificate_pdf_url(self, codigo: str, pdf_url: str) -> bool:
        """Actualiza la URL del PDF en CERTIFICADOS QR"""
        try:
            # Obtener el spreadsheet de certificados
            spreadsheet = self.spreadsheets.get('certificados')
            if not spreadsheet:
                sheet_id = settings.SHEETS['certificados']['id']
                spreadsheet = self.client.open_by_key(sheet_id)
                self.spreadsheets['certificados'] = spreadsheet
            
            # Obtener la hoja CERTIFICADOS QR
            worksheet_qr = spreadsheet.worksheet('CERTIFICADOS QR')
            records = worksheet_qr.get_all_records()
            headers = worksheet_qr.row_values(1)
            
            # Buscar el índice de la columna PDF_URL
            pdf_url_col_idx = None
            for idx, header in enumerate(headers):
                if header.upper().strip() in ['PDF_URL', 'PDF URL', 'URL PDF', 'URL']:
                    pdf_url_col_idx = idx + 1  # gspread usa índices base 1
                    break
            
            if not pdf_url_col_idx:
                print(f"ADVERTENCIA: No se encontró columna PDF_URL en CERTIFICADOS QR")
                return False
            
            # Buscar la fila con el código
            for row_idx, record in enumerate(records, start=2):  # start=2 porque row 1 es header
                codigo_record = (
                    record.get("CODIGO", "") or 
                    record.get("CÓDIGO", "") or 
                    record.get("codigo", "")
                )
                codigo_clean = str(codigo_record).strip() if codigo_record else ""
                
                if codigo_clean and codigo_clean.lower() == codigo.strip().lower():
                    # Actualizar la celda PDF_URL
                    worksheet_qr.update_cell(row_idx, pdf_url_col_idx, pdf_url)
                    print(f"DEBUG: PDF_URL actualizado para codigo={codigo}: {pdf_url}")
                    return True
            
            print(f"ADVERTENCIA: Certificado con codigo={codigo} no encontrado en CERTIFICADOS QR")
            return False
        except Exception as e:
            print(f"ERROR actualizando PDF_URL: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_certificate_fields(self, codigo: str, fields: Dict) -> bool:
        """Actualiza múltiples campos de un certificado en CERTIFICADOS QR"""
        try:
            # Obtener el spreadsheet de certificados
            spreadsheet = self.spreadsheets.get('certificados')
            if not spreadsheet:
                sheet_id = settings.SHEETS['certificados']['id']
                spreadsheet = self.client.open_by_key(sheet_id)
                self.spreadsheets['certificados'] = spreadsheet
            
            # Obtener la hoja CERTIFICADOS QR
            worksheet_qr = spreadsheet.worksheet('CERTIFICADOS QR')
            records = worksheet_qr.get_all_records()
            headers = worksheet_qr.row_values(1)
            
            # Asegurar que las columnas existan, si no, crearlas
            headers_upper = [h.upper().strip() for h in headers]
            new_headers = []
            
            # Mapeo de nombres de campos a posibles nombres de columnas en el Sheet
            field_to_column_map = {
                'CODIGO CERTIFICADO': ['CODIGO CERTIFICADO', 'CODIGO_CERTIFICADO', 'CÓDIGO CERTIFICADO'],
                'FECHA_GENERACION': ['FECHA GENERACION', 'FECHA_GENERACION', 'FECHA DE GENERACION', 'FECHA GENERACIÓN'],
                'PDF_URL': ['PDF_URL', 'PDF URL', 'URL PDF', 'URL']
            }
            
            for field_name in fields.keys():
                field_upper = field_name.upper().strip()
                # Buscar variaciones del nombre de la columna
                found = False
                possible_names = field_to_column_map.get(field_name, [field_name])
                
                for possible_name in possible_names:
                    for idx, header_upper in enumerate(headers_upper):
                        if possible_name.upper().strip() == header_upper or field_upper in header_upper or header_upper in field_upper:
                            found = True
                            break
                    if found:
                        break
                
                if not found:
                    # Agregar nueva columna solo si no es un campo mapeado
                    if field_name not in field_to_column_map:
                        new_headers.append(field_name)
                    else:
                        # Usar el primer nombre del mapeo como nombre de columna
                        new_headers.append(possible_names[0])
            
            # Agregar nuevas columnas si es necesario
            if new_headers:
                last_col = len(headers)
                for new_header in new_headers:
                    worksheet_qr.update_cell(1, last_col + 1, new_header)
                    headers.append(new_header)
                    headers_upper.append(new_header.upper().strip())
                    last_col += 1
                print(f"DEBUG: Nuevas columnas agregadas: {new_headers}")
            
            # Buscar la fila con el código (usando CODIGO, no CODIGO CERTIFICADO)
            for row_idx, record in enumerate(records, start=2):  # start=2 porque row 1 es header
                codigo_record = (
                    record.get("CODIGO", "") or 
                    record.get("CÓDIGO", "") or 
                    record.get("codigo", "")
                )
                codigo_clean = str(codigo_record).strip() if codigo_record else ""
                
                if codigo_clean and codigo_clean.lower() == codigo.strip().lower():
                    # Actualizar cada campo
                    for field_name, field_value in fields.items():
                        field_upper = field_name.upper().strip()
                        col_idx = None
                        
                        # Buscar la columna usando el mapeo
                        possible_names = field_to_column_map.get(field_name, [field_name])
                        for possible_name in possible_names:
                            for idx, header_upper in enumerate(headers_upper):
                                if possible_name.upper().strip() == header_upper:
                                    col_idx = idx + 1  # gspread usa índices base 1
                                    break
                            if col_idx:
                                break
                        
                        # Si no se encontró con el mapeo exacto, buscar por similitud
                        if not col_idx:
                            for idx, header_upper in enumerate(headers_upper):
                                if field_upper in header_upper or header_upper in field_upper:
                                    col_idx = idx + 1
                                    break
                        
                        if col_idx:
                            worksheet_qr.update_cell(row_idx, col_idx, str(field_value))
                            print(f"DEBUG: Campo {field_name} actualizado para codigo={codigo}: {field_value}")
                        else:
                            print(f"ADVERTENCIA: No se encontró columna para {field_name}")
                    
                    return True
            
            print(f"ADVERTENCIA: Certificado con codigo={codigo} no encontrado en CERTIFICADOS QR")
            return False
        except Exception as e:
            print(f"ERROR actualizando campos del certificado: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_worksheet(self, worksheet_name: str, sheet_type: str = 'certificados'):
        """
        Obtiene una hoja específica del spreadsheet
        
        Args:
            worksheet_name: Nombre de la hoja/worksheet
            sheet_type: Tipo de sheet ('certificados' o 'menciones')
        """
        try:
            if sheet_type == 'menciones':
                spreadsheet = self.spreadsheets.get('menciones')
                if not spreadsheet:
                    menciones_sheet_id = settings.SHEETS['menciones']['id']
                    spreadsheet = self.client.open_by_key(menciones_sheet_id)
                    self.spreadsheets['menciones'] = spreadsheet
            else:
                spreadsheet = self.spreadsheets.get('certificados')
                if not spreadsheet:
                    sheet_id = settings.SHEETS['certificados']['id']
                    spreadsheet = self.client.open_by_key(sheet_id)
                    self.spreadsheets['certificados'] = spreadsheet
            
            return spreadsheet.worksheet(worksheet_name)
        except Exception as e:
            raise Exception(f"Error obteniendo worksheet {worksheet_name} de {sheet_type}: {str(e)}")
    
    def get_compras_pendientes(self) -> List[Dict]:
        """Obtiene compras pendientes de procesar (sin código generado)"""
        try:
            worksheet = self.get_worksheet('compras', sheet_type='certificados')
            records = worksheet.get_all_records()
            
            # Filtrar compras sin código o con código vacío
            pendientes = []
            for record in records:
                codigo = record.get('codigo', '').strip() if record.get('codigo') else ''
                if not codigo or codigo == '':
                    pendientes.append(record)
            
            return pendientes
        except Exception as e:
            raise Exception(f"Error obteniendo compras pendientes: {str(e)}")
    
    def update_compra_codigo(self, row_index: int, codigo: str, **kwargs) -> bool:
        """Actualiza el código en una fila de compras y otros campos
        
        Args:
            row_index: Índice de la fila (1-based, incluyendo header)
            codigo: Código a actualizar
            **kwargs: Otros campos a actualizar
        """
        try:
            worksheet = self.get_worksheet('compras', sheet_type='certificados')
            headers = worksheet.row_values(1)
            
            # Encontrar índices de columnas
            updates = {}
            
            if 'codigo' in headers:
                codigo_col = headers.index('codigo') + 1
                updates[codigo_col] = codigo
            
            # Actualizar otros campos si se proporcionan
            for key, value in kwargs.items():
                if key in headers:
                    col_idx = headers.index(key) + 1
                    updates[col_idx] = str(value)
            
            # Actualizar todas las celdas de una vez (más eficiente)
            if updates:
                for col_idx, value in updates.items():
                    worksheet.update_cell(row_index, col_idx, value)
            
            return True
        except Exception as e:
            raise Exception(f"Error actualizando compra: {str(e)}")
    
    def get_menciones(self, force_refresh: bool = False) -> List[Dict]:
        """
        Obtiene todas las menciones desde Google Sheets con caché
        
        Args:
            force_refresh: Si es True, fuerza la actualización del caché
        """
        # Verificar si hay caché válido
        if not force_refresh and self._cache_menciones is not None:
            if self._cache_menciones_timestamp and (datetime.now() - self._cache_menciones_timestamp) < self._cache_ttl:
                print("DEBUG: Retornando menciones desde caché")
                return self._cache_menciones
        
        try:
            print("DEBUG: Obteniendo menciones desde Google Sheets (sin caché o caché expirado)")
            worksheet = self.get_worksheet('MENCIONES', sheet_type='menciones')
            records = worksheet.get_all_records()
            
            # Actualizar caché
            self._cache_menciones = records
            self._cache_menciones_timestamp = datetime.now()
            
            return records
        except Exception as e:
            raise Exception(f"Error obteniendo menciones: {str(e)}")
    
    def get_mencion_by_nro(self, nro: str) -> Optional[Dict]:
        """Busca una mención por NRO"""
        try:
            menciones = self.get_menciones()
            for mencion in menciones:
                nro_actual = str(mencion.get('NRO', '')).strip()
                if nro_actual == str(nro).strip():
                    return mencion
            return None
        except Exception as e:
            raise Exception(f"Error buscando mención por NRO: {str(e)}")
    
    def get_mencion_by_text(self, mencion_text: str) -> Optional[Dict]:
        """Busca una mención por texto de MENCIÓN"""
        try:
            menciones = self.get_menciones()
            mencion_text_lower = mencion_text.lower().strip()
            for mencion in menciones:
                mencion_actual = str(mencion.get('MENCIÓN', '')).lower().strip()
                if mencion_actual == mencion_text_lower:
                    return mencion
            return None
        except Exception as e:
            raise Exception(f"Error buscando mención por texto: {str(e)}")
    
    # ========== MÉTODOS PARA CLIENTES ==========
    
    def get_all_clientes(self, force_refresh: bool = False) -> List[Dict]:
        """
        Obtiene todos los clientes desde Google Sheets con caché
        
        Args:
            force_refresh: Si es True, fuerza la actualización del caché
        """
        # Verificar si hay caché válido
        if not force_refresh and self._cache_clientes is not None:
            if self._cache_clientes_timestamp and (datetime.now() - self._cache_clientes_timestamp) < self._cache_ttl:
                print("DEBUG: Retornando clientes desde caché")
                return self._cache_clientes
        
        try:
            print("DEBUG: Obteniendo clientes desde Google Sheets (sin caché o caché expirado)")
            # Obtener la hoja CLIENTES del spreadsheet de clientes
            worksheet = self.get_worksheet(settings.SHEETS['clientes']['worksheets']['clientes'], sheet_type='clientes')
            records = worksheet.get_all_records()
            
            # Actualizar caché
            self._cache_clientes = records
            self._cache_clientes_timestamp = datetime.now()
            
            return records
        except gspread.exceptions.WorksheetNotFound:
            # Si no encuentra la hoja, listar las hojas disponibles para debug
            spreadsheet = self.spreadsheets.get('clientes')
            if spreadsheet:
                available_sheets = [ws.title for ws in spreadsheet.worksheets()]
                raise Exception(f"Hoja 'CLIENTES' no encontrada. Hojas disponibles: {', '.join(available_sheets)}")
            raise Exception("No se pudo acceder al spreadsheet. Verifica la configuración.")
        except Exception as e:
            raise Exception(f"Error obteniendo clientes: {str(e)}")
    
    def get_cliente_by_dni(self, dni: str) -> Optional[Dict]:
        """Busca un cliente por DNI"""
        try:
            clientes = self.get_all_clientes()
            dni_clean = dni.replace('-', '').replace('.', '').replace(' ', '').strip()
            for cliente in clientes:
                # Buscar DNI en diferentes formatos de columnas
                cliente_dni = str(
                    cliente.get('DNI DEL CLIENTE', '') or 
                    cliente.get('DNI', '') or 
                    cliente.get('dni', '') or
                    cliente.get('DNI DEL CLIENTE', '')
                ).replace('-', '').replace('.', '').replace(' ', '').strip()
                if cliente_dni.lower() == dni_clean.lower():
                    return cliente
            return None
        except Exception as e:
            raise Exception(f"Error buscando cliente por DNI: {str(e)}")
    
    def create_cliente(self, data: Dict) -> Dict:
        """Crea un nuevo cliente en el Sheet y actualiza el caché"""
        try:
            worksheet = self.get_worksheet(settings.SHEETS['clientes']['worksheets']['clientes'], sheet_type='clientes')
            
            # Verificar que el DNI no exista
            dni = data.get('DNI DEL CLIENTE') or data.get('DNI') or data.get('dni')
            if dni:
                existing = self.get_cliente_by_dni(str(dni))
                if existing:
                    raise ValueError(f"El cliente con DNI {dni} ya existe")
            
            # Obtener headers
            headers = worksheet.row_values(1)
            
            # Mapear datos a los headers del Sheet
            # Si viene 'nombres' y 'apellidos' separados, combinarlos en 'NOMBRE COMPLETO DEL CLIENTE'
            mapped_data = {}
            for header in headers:
                # Buscar el valor en diferentes formatos
                if header == 'NOMBRE COMPLETO DEL CLIENTE':
                    nombres = data.get('nombres', '') or data.get('NOMBRES', '')
                    apellidos = data.get('apellidos', '') or data.get('APELLIDOS', '')
                    mapped_data[header] = f"{nombres} {apellidos}".strip()
                elif header == 'DNI DEL CLIENTE':
                    mapped_data[header] = data.get('DNI DEL CLIENTE') or data.get('DNI') or data.get('dni') or ''
                elif header == 'CELULAR DEL CLIENTE':
                    mapped_data[header] = data.get('CELULAR DEL CLIENTE') or data.get('telefono') or data.get('TELEFONO') or ''
                elif header == 'CORREO DEL CLIENTE':
                    mapped_data[header] = data.get('CORREO DEL CLIENTE') or data.get('email') or data.get('EMAIL') or ''
                else:
                    # Intentar encontrar el valor por cualquier variación
                    header_lower = header.lower()
                    for key, value in data.items():
                        if key.lower() == header_lower or key.lower().replace(' ', '_') == header_lower.replace(' ', '_'):
                            mapped_data[header] = value
                            break
                    if header not in mapped_data:
                        mapped_data[header] = ''
            
            # Preparar fila según los headers del Sheet
            row = []
            for header in headers:
                value = mapped_data.get(header, "")
                row.append(str(value) if value else "")
            
            # Agregar fila
            worksheet.append_row(row)
            
            # Invalidar caché de clientes
            self._cache_clientes = None
            self._cache_clientes_timestamp = None
            
            # Retornar el cliente creado
            if dni:
                return self.get_cliente_by_dni(str(dni))
            return mapped_data
        except Exception as e:
            raise Exception(f"Error creando cliente: {str(e)}")
    
    def update_cliente(self, dni: str, data: Dict) -> Dict:
        """Actualiza un cliente existente"""
        try:
            worksheet = self.get_worksheet(settings.SHEETS['clientes']['worksheets']['clientes'], sheet_type='clientes')
            records = worksheet.get_all_records()
            headers = worksheet.row_values(1)
            
            dni_clean = dni.replace('-', '').replace('.', '').replace(' ', '').strip()
            
            # Mapear datos a los headers del Sheet
            print(f"DEBUG google_sheets.update_cliente: data recibido: {data}")  # Debug
            print(f"DEBUG google_sheets.update_cliente: headers del sheet: {headers}")  # Debug
            mapped_data = {}
            for header in headers:
                if header == 'NOMBRE COMPLETO DEL CLIENTE':
                    # Buscar directamente 'NOMBRE COMPLETO DEL CLIENTE' o 'nombreCompleto'
                    nombre_completo = data.get('NOMBRE COMPLETO DEL CLIENTE') or data.get('nombreCompleto') or data.get('NOMBRE_COMPLETO')
                    if nombre_completo:
                        mapped_data[header] = str(nombre_completo).strip()
                        print(f"DEBUG: Mapeado NOMBRE COMPLETO DEL CLIENTE: {mapped_data[header]}")  # Debug
                elif header == 'CELULAR DEL CLIENTE':
                    telefono = data.get('CELULAR DEL CLIENTE') or data.get('telefono') or data.get('TELEFONO') or data.get('CELULAR')
                    if telefono:
                        mapped_data[header] = str(telefono).strip()
                        print(f"DEBUG: Mapeado CELULAR DEL CLIENTE: {mapped_data[header]}")  # Debug
                elif header == 'CORREO DEL CLIENTE':
                    email = data.get('CORREO DEL CLIENTE') or data.get('email') or data.get('EMAIL') or data.get('CORREO')
                    if email:
                        mapped_data[header] = str(email).strip()
                        print(f"DEBUG: Mapeado CORREO DEL CLIENTE: {mapped_data[header]}")  # Debug
                elif header in data and data[header]:
                    mapped_data[header] = str(data[header]).strip()
            
            print(f"DEBUG google_sheets.update_cliente: mapped_data final: {mapped_data}")  # Debug
            
            # Encontrar la fila
            for idx, record in enumerate(records, start=2):  # start=2 porque row 1 es header
                record_dni = str(
                    record.get('DNI DEL CLIENTE', '') or 
                    record.get('DNI', '') or 
                    record.get('dni', '')
                ).replace('-', '').replace('.', '').replace(' ', '').strip()
                if record_dni.lower() == dni_clean.lower():
                    # Actualizar valores
                    print(f"DEBUG: Cliente encontrado en fila {idx}, actualizando...")  # Debug
                    for header, value in mapped_data.items():
                        if header in headers:
                            col_idx = headers.index(header) + 1
                            print(f"DEBUG: Actualizando celda [{idx}, {col_idx}] ({header}) = '{value}'")  # Debug
                            worksheet.update_cell(idx, col_idx, str(value))
                    
                    # Invalidar caché de clientes
                    self._cache_clientes = None
                    self._cache_clientes_timestamp = None
                    
                    print(f"DEBUG: Actualización completada, obteniendo cliente actualizado...")  # Debug
                    return self.get_cliente_by_dni(dni)
            
            raise ValueError(f"Cliente con DNI {dni} no encontrado")
        except Exception as e:
            raise Exception(f"Error actualizando cliente: {str(e)}")
    
    def delete_cliente(self, dni: str) -> bool:
        """Elimina un cliente (marca como eliminado o elimina la fila)"""
        try:
            worksheet = self.get_worksheet(settings.SHEETS['clientes']['worksheets']['clientes'], sheet_type='clientes')
            records = worksheet.get_all_records()
            
            dni_clean = dni.replace('-', '').replace('.', '').replace(' ', '').strip()
            
            # Encontrar la fila
            for idx, record in enumerate(records, start=2):
                record_dni = str(
                    record.get('DNI DEL CLIENTE', '') or 
                    record.get('DNI', '') or 
                    record.get('dni', '')
                ).replace('-', '').replace('.', '').replace(' ', '').strip()
                if record_dni.lower() == dni_clean.lower():
                    # Eliminar fila
                    worksheet.delete_rows(idx)
                    
                    # Invalidar caché de clientes
                    self._cache_clientes = None
                    self._cache_clientes_timestamp = None
                    
                    return True
            
            return False
        except Exception as e:
            raise Exception(f"Error eliminando cliente: {str(e)}")


# Instancia global del servicio
sheets_service = GoogleSheetsService()
