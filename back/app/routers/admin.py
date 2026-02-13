from fastapi import APIRouter, Depends, HTTPException, Body, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Optional
from io import BytesIO
from app.models.schemas import (
    CertificateCreate, CertificateUpdate, CertificateResponse,
    CertificateAnular, UserResponse
)
from app.core.google_sheets import sheets_service
from app.core.security import get_operator_or_admin, get_admin_user, get_current_user
from app.core.config import settings
from app.core.qr_generator import generate_qr_code
from app.core.users import get_user, update_user_status
from datetime import datetime

router = APIRouter()


@router.post("/certificados", response_model=CertificateResponse)
async def create_certificate(
    certificado: CertificateCreate,
    mencion_nro: Optional[str] = None,
    current_user: dict = Depends(get_operator_or_admin)
):
    """
    Crea un nuevo certificado (Operador/Admin)
    
    Args:
        certificado: Datos del certificado
        mencion_nro: NRO de la mención desde Google Sheets (ej: "101")
    """
    try:
        # Obtener datos de la mención si se proporciona
        mencion_data = None
        mencion_text = ""
        
        if mencion_nro:
            mencion_data = sheets_service.get_mencion_by_nro(mencion_nro)
            if mencion_data:
                mencion_text = mencion_data.get('MENCIÓN', '')
                # Si no se proporcionaron horas o curso, usar los de la mención
                if not certificado.horas and mencion_data.get('HORAS'):
                    certificado.horas = mencion_data.get('HORAS')
                if not certificado.curso and mencion_data.get('P. CERTIFICADO'):
                    certificado.curso = mencion_data.get('P. CERTIFICADO')
                if not certificado.fecha_emision and mencion_data.get('F. EMISIÓN'):
                    certificado.fecha_emision = mencion_data.get('F. EMISIÓN', '')
        
        # Usar directamente Google Sheets
        certificado_dict = certificado.model_dump()
        certificado_dict["created_at"] = datetime.now().isoformat()
        certificado_dict["updated_at"] = datetime.now().isoformat()
        
        # nombre_completo ya está incluido en certificado_dict si viene del frontend
        
        # Incluir datos de la mención si está disponible
        if mencion_data:
            certificado_dict["mencion_nro"] = mencion_data.get('NRO', '')
            certificado_dict["mencion_especialidad"] = mencion_data.get('ESPECIALIDAD', '')
            certificado_dict["mencion_p_certificado"] = mencion_data.get('P. CERTIFICADO', '')
            certificado_dict["mencion_texto"] = mencion_data.get('MENCIÓN', '')
            certificado_dict["mencion_horas"] = mencion_data.get('HORAS', '')
            certificado_dict["fecha_inicio"] = mencion_data.get('F. INICIO', '')
            certificado_dict["fecha_termino"] = mencion_data.get('F. TÉRMINO', '')
            certificado_dict["fecha_emision_mencio"] = mencion_data.get('F. EMISIÓN', '')
        
        # Generar código si no se proporcionó
        if not certificado_dict.get("codigo"):
            from app.core.code_generator import generate_certificate_code
            certificado_dict["codigo"] = generate_certificate_code(
                dni=certificado.dni,
                mencion_nro=mencion_nro
            )

        # Enriquecer datos del cliente desde la hoja CLIENTES (si hay DNI)
        try:
            dni_value = certificado_dict.get("dni") or certificado_dict.get("DNI")
            if dni_value:
                cliente = sheets_service.get_cliente_by_dni(str(dni_value))
                if cliente:
                    # Nombre completo del cliente
                    nombre_cliente = (
                        cliente.get("NOMBRE COMPLETO DEL CLIENTE")
                        or cliente.get("NOMBRES")
                        or cliente.get("nombres")
                        or ""
                    )
                    if nombre_cliente and not certificado_dict.get("nombre_completo"):
                        certificado_dict["nombre_completo"] = str(nombre_cliente).strip()

                    # Teléfono y correo
                    telefono_cliente = (
                        cliente.get("CELULAR DEL CLIENTE")
                        or cliente.get("TELEFONO")
                        or cliente.get("telefono")
                        or ""
                    )
                    correo_cliente = (
                        cliente.get("CORREO DEL CLIENTE")
                        or cliente.get("EMAIL")
                        or cliente.get("email")
                        or ""
                    )
                    if telefono_cliente:
                        certificado_dict["telefono"] = str(telefono_cliente).strip()
                    if correo_cliente:
                        certificado_dict["email"] = str(correo_cliente).strip()
        except Exception as e:
            # No bloquear la creación si falla el enriquecimiento
            print(f"ADVERTENCIA: No se pudo enriquecer datos del cliente desde CLIENTES: {str(e)}")
        
        try:
            nuevo_certificado = sheets_service.create_certificate(certificado_dict, mencion_data=mencion_data)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            # Limpiar caracteres Unicode problemáticos del mensaje de error
            error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
            print(f"ERROR en create_certificate: {error_msg}")
            print(f"Traceback: {error_trace.encode('ascii', 'ignore').decode('ascii')}")
            raise HTTPException(status_code=500, detail=f"Error creando certificado en Google Sheets: {error_msg}")
        
        verify_url = f"{settings.BASE_URL}/consulta/{nuevo_certificado.get('codigo')}"
        
        # Actualizar PDF_URL en Google Sheets con la URL de verificación (la misma que usa el QR)
        try:
            sheets_service.update_certificate_pdf_url(nuevo_certificado.get('codigo'), verify_url)
            print(f"DEBUG: PDF_URL actualizado con URL de verificación: {verify_url}")
        except Exception as e_update:
            print(f"ADVERTENCIA: No se pudo actualizar PDF_URL en Sheets: {str(e_update)}")
        
        # Asegurar que nombres y apellidos tengan valores válidos
        nombres = nuevo_certificado.get("nombres") or ""
        apellidos = nuevo_certificado.get("apellidos") or ""
        
        # Si no hay nombres/apellidos separados, intentar separar desde nombre_completo
        if not nombres and not apellidos:
            nombre_completo = nuevo_certificado.get("nombre_completo") or nuevo_certificado.get("NOMBRE COMPLETO DEL CLIENTE") or ""
            if nombre_completo:
                partes = str(nombre_completo).strip().split(' ', 1)
                if len(partes) >= 2:
                    nombres = partes[0]
                    apellidos = ' '.join(partes[1:])
                else:
                    nombres = nombre_completo
        
        print(f"DEBUG create_certificate response: codigo={nuevo_certificado.get('codigo')}, nombres={nombres}, apellidos={apellidos}")
        
        # Convertir horas a string si es número
        horas_value = nuevo_certificado.get("horas")
        if horas_value is not None:
            horas_value = str(horas_value) if not isinstance(horas_value, str) else horas_value
        
        try:
            response = CertificateResponse(
                found=True,
                codigo=nuevo_certificado.get("codigo") or "",
                nombres=nombres,
                apellidos=apellidos,
                curso=nuevo_certificado.get("curso") or "",
                fecha_emision=nuevo_certificado.get("fecha_emision") or "",
                horas=horas_value,
                estado=nuevo_certificado.get("estado", "VALIDO") or "VALIDO",
                pdf_url=nuevo_certificado.get("pdf_url") or None,
                verify_url=verify_url
            )
            print(f"DEBUG: CertificateResponse creado exitosamente")
            return response
        except Exception as e_response:
            # No exponer detalles del error al usuario
            raise HTTPException(status_code=500, detail="Error procesando certificado")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        # No exponer detalles del error al usuario
        raise HTTPException(status_code=500, detail="Error creando certificado")


# CRÍTICO: Esta ruta DEBE estar ANTES de cualquier otra ruta que use /certificados/{codigo}
# FastAPI resuelve rutas en orden de definición, y las rutas más específicas deben ir primero
# Debe estar justo después de create_certificate para asegurar que se registre antes que otras rutas
@router.get("/certificados/{codigo}/qr", name="download_qr")
async def download_qr(
    codigo: str,
    current_user: dict = Depends(get_operator_or_admin)
):
    """Descarga el código QR de un certificado (Operador/Admin)"""
    print(f"DEBUG: download_qr llamado con codigo={codigo}")
    try:
        certificado = sheets_service.get_certificate_by_code(codigo)
        if not certificado:
            print(f"DEBUG: Certificado no encontrado para codigo={codigo}")
            raise HTTPException(status_code=404, detail="Certificado no encontrado")
        
        print(f"DEBUG: Generando QR para codigo={codigo}")
        qr_buffer = generate_qr_code(codigo, size=512)
        
        return StreamingResponse(
            qr_buffer,
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=qr_{codigo}.png"}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Error generando QR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generando QR: {str(e)}")


@router.post("/certificados/{codigo}/anular", response_model=CertificateResponse)
async def anular_certificate(
    codigo: str,
    data: CertificateAnular,
    current_user: dict = Depends(get_operator_or_admin)
):
    """Anula un certificado (Operador/Admin)"""
    try:
        certificado_anulado = sheets_service.anular_certificate(codigo, data.motivo)
        
        verify_url = f"{settings.BASE_URL}/consulta/{codigo}"
        
        return CertificateResponse(
            found=True,
            codigo=certificado_anulado.get("codigo"),
            nombres=certificado_anulado.get("nombres"),
            apellidos=certificado_anulado.get("apellidos"),
            curso=certificado_anulado.get("curso"),
            fecha_emision=certificado_anulado.get("fecha_emision"),
            horas=certificado_anulado.get("horas"),
            estado=certificado_anulado.get("estado"),
            pdf_url=certificado_anulado.get("pdf_url"),
            verify_url=verify_url
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error anulando certificado: {str(e)}")


@router.post("/certificados/{codigo}/unir-pdf")
async def unir_pdfs(
    codigo: str,
    pdf_file: UploadFile = File(...),
    current_user: dict = Depends(get_operator_or_admin)
):
    """
    Une un PDF adicional al certificado generado.
    El PDF subido se agregará después del PDF del certificado.
    """
    try:
        # Validar tipo de archivo
        if not pdf_file.content_type == 'application/pdf':
            raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
        
        # Validar tamaño del archivo (máximo 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await pdf_file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="El archivo PDF no puede exceder 10MB")
        
        # Validar que realmente sea un PDF leyendo el header
        if not file_content.startswith(b'%PDF'):
            raise HTTPException(status_code=400, detail="El archivo no es un PDF válido")
        
        # Resetear el archivo para leerlo de nuevo
        pdf_file.file.seek(0)
        
        # Obtener certificado
        certificado = sheets_service.get_certificate_by_code(codigo)
        if not certificado:
            raise HTTPException(status_code=404, detail="Certificado no encontrado")
        
        # Generar PDF del certificado si no existe
        from app.core.pdf_generator import generate_certificate_pdf
        pdf_certificado_buffer = generate_certificate_pdf(certificado)
        pdf_certificado_buffer.seek(0)
        
        # Leer PDF subido (ya validado arriba)
        pdf_subido_content = file_content
        nombre_pdf_subido = pdf_file.filename or f"pdf_subido_{codigo}.pdf"
        # Validar y limpiar el nombre del archivo (prevenir path traversal)
        import re
        nombre_pdf_subido = re.sub(r'[^a-zA-Z0-9._-]', '_', nombre_pdf_subido)
        # Quitar la extensión .pdf del nombre
        if nombre_pdf_subido.lower().endswith('.pdf'):
            nombre_pdf_subido = nombre_pdf_subido[:-4]
        
        # Unir PDFs usando pypdf
        from pypdf import PdfWriter, PdfReader
        
        # Crear writer para el PDF final
        writer = PdfWriter()
        
        # Agregar primero las páginas del PDF subido
        pdf_subido_buffer = BytesIO(pdf_subido_content)
        reader_subido = PdfReader(pdf_subido_buffer)
        for page in reader_subido.pages:
            writer.add_page(page)
        
        # Agregar después las páginas del certificado generado
        reader_certificado = PdfReader(pdf_certificado_buffer)
        for page in reader_certificado.pages:
            writer.add_page(page)
        
        # Generar PDF unido en memoria
        pdf_unido_buffer = BytesIO()
        writer.write(pdf_unido_buffer)
        pdf_unido_content = pdf_unido_buffer.getvalue()
        
        # Guardar PDF unido
        from app.core.storage import StorageService
        storage_service = StorageService()
        
        filename = f"certificado_{codigo}_unido.pdf"
        storage_info = storage_service.save_pdf(
            file_content=pdf_unido_content,
            filename=filename,
            codigo=codigo
        )
        
        # Obtener timestamp actual
        from datetime import datetime
        timestamp_generacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Generar URL de verificación (la misma que usa el QR)
        from app.core.config import settings
        verify_url = f"{settings.BASE_URL}/consulta/{codigo}"
        
        # Actualizar certificado en Google Sheets con múltiples campos
        try:
            fields_to_update = {
                'PDF_URL': verify_url,  # URL de verificación, no la URL del archivo físico
                'CODIGO CERTIFICADO': nombre_pdf_subido,
                'FECHA_GENERACION': timestamp_generacion
            }
            sheets_service.update_certificate_fields(codigo, fields_to_update)
            print(f"DEBUG: PDF unido guardado y campos actualizados en Sheets: PDF_URL={verify_url}, CODIGO CERTIFICADO: {nombre_pdf_subido}, Fecha: {timestamp_generacion}")
        except Exception as e_update:
            print(f"ADVERTENCIA: No se pudo actualizar campos en Sheets: {str(e_update)}")
            # Intentar actualizar solo la URL como fallback
            try:
                sheets_service.update_certificate_pdf_url(codigo, verify_url)
            except:
                pass
        
        return {
            "message": "PDFs unidos exitosamente",
            "codigo": codigo,
            "pdf_url": verify_url,
            "total_paginas": len(reader_certificado.pages) + len(reader_subido.pages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error uniendo PDFs: {str(e)}")


@router.get("/certificados", response_model=List[dict])
async def list_certificates(
    current_user: dict = Depends(get_operator_or_admin)
):
    """Lista todos los certificados desde CERTIFICADOS QR (Operador/Admin)"""
    try:
        # Usar CERTIFICADOS QR (hoja donde se guardan todos los certificados con datos completos)
        certificados = sheets_service.get_all_certificates_qr()
        return certificados
    except Exception as e:
        clean_error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        raise HTTPException(status_code=500, detail=f"Error listando certificados: {clean_error_msg}")


@router.put("/certificados/{codigo}", response_model=CertificateResponse)
async def update_certificate(
    codigo: str,
    certificado: CertificateUpdate,
    current_user: dict = Depends(get_operator_or_admin)
):
    """Actualiza un certificado existente (Operador/Admin)"""
    try:
        update_data = certificado.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now().isoformat()
        
        certificado_actualizado = sheets_service.update_certificate(codigo, update_data)
        
        verify_url = f"{settings.BASE_URL}/consulta/{codigo}"
        
        return CertificateResponse(
            found=True,
            codigo=certificado_actualizado.get("codigo"),
            nombres=certificado_actualizado.get("nombres"),
            apellidos=certificado_actualizado.get("apellidos"),
            curso=certificado_actualizado.get("curso"),
            fecha_emision=certificado_actualizado.get("fecha_emision"),
            horas=certificado_actualizado.get("horas"),
            estado=certificado_actualizado.get("estado", "VALIDO"),
            pdf_url=certificado_actualizado.get("pdf_url"),
            verify_url=verify_url
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando certificado: {str(e)}")


@router.get("/users", response_model=List[UserResponse])
async def list_users(current_user: dict = Depends(get_admin_user)):
    """Lista todos los usuarios (solo Admin)"""
    # En producción, esto debería venir de una base de datos
    from app.core.users import users_db
    users = []
    for email, user_data in users_db.items():
        users.append(UserResponse(
            email=user_data["email"],
            role=user_data["role"],
            active=user_data.get("active", True)
        ))
    return users


@router.put("/users/{email}/activate")
async def activate_user(email: str, current_user: dict = Depends(get_admin_user)):
    """Activa un usuario (solo Admin)"""
    try:
        update_user_status(email, True)
        return {"message": f"Usuario {email} activado"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/users/{email}/deactivate")
async def deactivate_user(email: str, current_user: dict = Depends(get_admin_user)):
    """Desactiva un usuario (solo Admin)"""
    try:
        update_user_status(email, False)
        return {"message": f"Usuario {email} desactivado"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
