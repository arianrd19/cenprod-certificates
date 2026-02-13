from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CertificateBase(BaseModel):
    codigo: str
    nombres: str
    apellidos: str
    dni: Optional[str] = None
    curso: str
    fecha_emision: str
    horas: Optional[str] = None
    estado: str = "VALIDO"
    pdf_url: Optional[str] = None
    firma_url: Optional[str] = None
    logo_url: Optional[str] = None
    nombre_completo: Optional[str] = None  # Campo adicional para CERTIFICADOS QR


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    dni: Optional[str] = None
    curso: Optional[str] = None
    fecha_emision: Optional[str] = None
    horas: Optional[str] = None
    estado: Optional[str] = None
    pdf_url: Optional[str] = None
    firma_url: Optional[str] = None
    logo_url: Optional[str] = None


class CertificateResponse(BaseModel):
    found: bool
    codigo: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    curso: Optional[str] = None
    fecha_emision: Optional[str] = None
    horas: Optional[str] = None
    estado: Optional[str] = None
    pdf_url: Optional[str] = None
    verify_url: Optional[str] = None


class CertificateSearch(BaseModel):
    codigo: str


class CertificateAnular(BaseModel):
    motivo: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):
    email: str
    role: str
    active: bool
