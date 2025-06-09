from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from social_media_models import *


class SocialMediaOperations:

    @staticmethod
    async def get_all_social_media(session: AsyncSession) -> List[SocialMedia]:
        """Obtiene todos los registros de redes sociales"""
        result = await session.execute(select(SocialMedia))
        return result.scalars().all()

    @staticmethod
    async def get_social_media_by_id(session: AsyncSession, entry_id: int) -> Optional[SocialMedia]:
        """Obtiene un registro por su ID"""
        result = await session.execute(
            select(SocialMedia).where(SocialMedia.id == entry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_social_media(session: AsyncSession, data: dict) -> SocialMedia:
        """Crea un nuevo registro de redes sociales"""
        new_entry = SocialMedia(**data)
        session.add(new_entry)
        await session.commit()
        await session.refresh(new_entry)
        return new_entry

    @staticmethod
    async def update_social_media(session: AsyncSession, entry_id: int, update_data: dict) -> Optional[SocialMedia]:
        """Modifica un registro existente, permitiendo cambios parciales o totales"""
        entry = await session.get(SocialMedia, entry_id)
        if not entry:
            return None

        for key, value in update_data.items():
            if hasattr(entry, key):
                # Solo actualiza si el valor no es None ni una cadena vacía
                if value not in (None, ""):
                    setattr(entry, key, value)

        await session.commit()
        await session.refresh(entry)
        return entry

    @staticmethod
    async def delete_social_media(session: AsyncSession, entry_id: int) -> Optional[SocialMedia]:
        """Elimina un registro por ID y lo guarda en deleted_social_media"""
        entry = await session.get(SocialMedia, entry_id)
        if not entry:
            return None

        try:
            deleted_entry = DeletedSocialMedia(**entry.dict())
        except ValueError as e:
            # Manejar errores de validación
            raise ValueError(f"Error al validar los datos para la tabla eliminada: {e}")

        await session.delete(entry)
        await session.commit()
        return entry

    @staticmethod
    async def get_deleted_social_media(session: AsyncSession) -> List[DeletedSocialMedia]:
        """Obtiene todos los registros eliminados de redes sociales"""
        result = await session.execute(select(DeletedSocialMedia))
        return result.scalars().all()

    @staticmethod
    async def search_social_media_by_gender(session: AsyncSession, gender: str) -> List[SocialMedia]:
        """Busca registros por género"""
        result = await session.execute(
            select(SocialMedia).where(SocialMedia.gender.ilike(gender))
        )
        return result.scalars().all()

    @staticmethod
    async def filter_social_media_by_age(session: AsyncSession) -> List[SocialMedia]:
        """Ordena los registros por edad"""
        result = await session.execute(
            select(SocialMedia).order_by(SocialMedia.age)
        )
        return result.scalars().all()

    @staticmethod
    async def search_social_media_by_field(session: AsyncSession, field: str, value: str) -> List[SocialMedia]:
        """Busca registros por cualquier campo especificado"""
        try:
            if not hasattr(SocialMedia, field):
                raise ValueError(f"Campo no válido: {field}")

            model_field = getattr(SocialMedia, field)

            # Determinar el tipo de campo y ajustar la búsqueda
            if field in ['age', 'usage_without_purpose', 'distraction_when_busy',
                         'restless_without_social_media', 'easily_distracted',
                         'compare_with_successful_people', 'seek_validation']:
                # Campos numéricos
                numeric_value = int(value)
                result = await session.execute(
                    select(SocialMedia).where(model_field == numeric_value)
                )
            else:
                # Campos de texto
                result = await session.execute(
                    select(SocialMedia).where(model_field.ilike(f"%{value}%"))
                )

            return result.scalars().all()
        except ValueError as e:
            raise ValueError(f"Error de validación: {str(e)}")
        except Exception as e:
            raise Exception(f"Error en la búsqueda: {str(e)}")

