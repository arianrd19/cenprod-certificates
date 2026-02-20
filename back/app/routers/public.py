from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.models.schemas import CertificateResponse, CertificateSearch
from app.core.google_sheets import sheets_service
from app.core.config import settings
from app.core.pdf_generator import generate_certificate_pdf

router = APIRouter()


@router.get("/certificados/{codigo}", response_model=CertificateResponse)
async def get_certificate(codigo: str, request: Request):
    """Obtiene un certificado por código (público)"""
    try:
        # Obtener desde Google Sheets
        try:
            certificado = sheets_service.get_certificate_by_code(codigo)
        except Exception as e_sheets:
            import traceback
            error_trace = traceback.format_exc()
            raise HTTPException(status_code=500, detail=f"Error buscando certificado en Google Sheets: {str(e_sheets)}")
        
        if not certificado:
            return CertificateResponse(found=False)
        
        
        # Asegurar que todos los campos tengan valores válidos
        codigo_value = certificado.get("codigo") or ""
        nombres_value = certificado.get("nombres") or ""
        apellidos_value = certificado.get("apellidos") or ""
        curso_value = certificado.get("curso") or ""
        fecha_emision_value = certificado.get("fecha_emision") or ""
        horas_value = certificado.get("horas")
        if horas_value is not None:
            horas_value = str(horas_value) if not isinstance(horas_value, str) else horas_value
        estado_value = certificado.get("estado", "VALIDO") or "VALIDO"
        pdf_url_value = certificado.get("pdf_url") or None
        
        verify_url = f"{settings.BASE_URL}/consulta/{codigo_value}"
        
        try:
            response = CertificateResponse(
                found=True,
                codigo=codigo_value,
                nombres=nombres_value,
                apellidos=apellidos_value,
                curso=curso_value,
                fecha_emision=fecha_emision_value,
                horas=horas_value,
                estado=estado_value,
                pdf_url=pdf_url_value,
                verify_url=verify_url
            )
            return response
        except Exception as e_response:
            pass
            # No exponer detalles del error al usuario
            raise HTTPException(status_code=500, detail="Error procesando certificado")
    except HTTPException:
        raise
    except Exception as e:
        pass
        # No exponer detalles del error al usuario
        raise HTTPException(status_code=500, detail="Error obteniendo certificado")


@router.post("/buscar", response_model=CertificateResponse)
async def search_certificate(search: CertificateSearch, request: Request):
    """Busca un certificado por código (público)"""
    try:
        certificado = sheets_service.get_certificate_by_code(search.codigo)
        
        if not certificado:
            return CertificateResponse(found=False)
        
        verify_url = f"{settings.BASE_URL}/consulta/{search.codigo}"
        
        return CertificateResponse(
            found=True,
            codigo=certificado.get("codigo"),
            nombres=certificado.get("nombres"),
            apellidos=certificado.get("apellidos"),
            curso=certificado.get("curso"),
            fecha_emision=certificado.get("fecha_emision"),
            horas=certificado.get("horas"),
            estado=certificado.get("estado", "VALIDO"),
            pdf_url=certificado.get("pdf_url"),
            verify_url=verify_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error buscando certificado: {str(e)}")


@router.get("/certificados/{codigo}/pdf")
async def download_certificate_pdf(
    codigo: str, 
    request: Request, 
    force_regenerate: bool = False,
    download: bool = False
):
    """Descarga el PDF del certificado (público). Si no existe, lo genera y guarda."""
    try:
        certificado = sheets_service.get_certificate_by_code(codigo)
        
        if not certificado:
            raise HTTPException(status_code=404, detail="Certificado no encontrado")
        
        # Determinar disposición (ver o descargar)
        disposition_type = "attachment" if download else "inline"
        
        # Si hay pdf_url y el archivo existe, y no se fuerza regeneración, redirigir a ese
        pdf_url = certificado.get("pdf_url")
        if pdf_url and not force_regenerate:
            # Verificar si el archivo existe localmente
            try:
                from app.core.storage import StorageService
                storage_service = StorageService()
                if storage_service.storage_type == 'local':
                    # Verificar si el archivo existe
                    import os
                    from pathlib import Path
                    from app.core.config import ROOT
                    # Extraer ruta relativa de la URL
                    if '/uploads/certificados/' in pdf_url:
                        relative_path = pdf_url.split('/uploads/certificados/')[-1]
                        file_path = ROOT / 'uploads' / 'certificados' / relative_path
                        if file_path.exists():
                            from fastapi.responses import FileResponse
                            nombre_completo = f"{certificado.get('nombres', '')}_{certificado.get('apellidos', '')}"
                            filename = f"certificado_{nombre_completo.replace(' ', '_')}.pdf"
                            return FileResponse(
                                str(file_path),
                                media_type="application/pdf",
                                headers={
                                    "Content-Disposition": f"{disposition_type}; filename={filename}",
                                    "X-Content-Type-Options": "nosniff"
                                }
                            )
            except Exception as e:
                pass
                # Continuar para generar nuevo PDF
                pass
        
        # Generar PDF dinámico
        pdf_buffer = generate_certificate_pdf(certificado)
        pdf_content = pdf_buffer.read()
        
        # Guardar PDF en el backend
        try:
            from app.core.storage import StorageService
            storage_service = StorageService()
            
            nombre_completo = certificado.get('nombre_completo') or f"{certificado.get('nombres', '')} {certificado.get('apellidos', '')}"
            filename = f"certificado_{codigo}.pdf"
            
            # Guardar PDF
            storage_info = storage_service.save_pdf(
                file_content=pdf_content,
                filename=filename,
                codigo=codigo
            )
            
            
            # Actualizar certificado en Google Sheets con la URL real del PDF guardado
            try:
                sheets_service.update_certificate_pdf_url(codigo, storage_info['url'])
            except Exception as e_update:
                pass
                # Continuar aunque no se actualice la URL
                pass
            
            # Devolver el PDF guardado (no el buffer en memoria)
            # Esto asegura que siempre se devuelva el mismo PDF que se guardó
            if storage_service.storage_type == 'local':
                relative_path = storage_info['relative_path']
                file_path = storage_service.storage_path / relative_path
                if file_path.exists():
                    from fastapi.responses import FileResponse
                    nombre_completo = f"{certificado.get('nombres', '')}_{certificado.get('apellidos', '')}"
                    filename = f"certificado_{nombre_completo.replace(' ', '_')}.pdf"
                    return FileResponse(
                        str(file_path),
                        media_type="application/pdf",
                        headers={
                            "Content-Disposition": f"{disposition_type}; filename={filename}",
                            "X-Content-Type-Options": "nosniff"
                        }
                    )
            
        except Exception as e_storage:
            pass
            # Continuar para devolver el PDF aunque no se guarde
            pass
        
        # Fallback: devolver el PDF generado desde el buffer
        pdf_buffer.seek(0)  # Resetear buffer para lectura
        nombre_completo = f"{certificado.get('nombres', '')}_{certificado.get('apellidos', '')}"
        filename = f"certificado_{nombre_completo.replace(' ', '_')}.pdf"
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"{disposition_type}; filename={filename}",
                "Content-Type": "application/pdf",
                "X-Content-Type-Options": "nosniff"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {str(e)}")

