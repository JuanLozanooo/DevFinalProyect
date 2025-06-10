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

    async def delete_social_media(session: AsyncSession, id: int) -> bool:
        try:
            stmt = select(SocialMedia).where(SocialMedia.id == id)
            result = await session.execute(stmt)
            social_media = result.scalar_one_or_none()

            if not social_media:
                return False

            # Normalizar valores de uses_social_media
            uses_value = social_media.uses_social_media
            if uses_value.lower() in ['sí', 'si', 'sí', 'yes']:
                uses_value = "Yes"
            elif uses_value.lower() in ['no']:
                uses_value = "No"

            deleted_record = DeletedSocialMedia(
                id=social_media.id,
                date=social_media.date,
                age=social_media.age,
                gender=social_media.gender,
                occupation_status=social_media.occupation_status,
                organization_affiliation=social_media.organization_affiliation,
                uses_social_media=uses_value,  # Usar valor normalizado
                platforms_used=social_media.platforms_used.strip('"').strip("'"),
                daily_use_average=social_media.daily_use_average,
                usage_without_purpose=social_media.usage_without_purpose,
                distraction_when_busy=social_media.distraction_when_busy,
                restless_without_social_media=social_media.restless_without_social_media,
                easily_distracted=social_media.easily_distracted,
                compare_with_successful_people=social_media.compare_with_successful_people,
                seek_validation=social_media.seek_validation,
                image_url=social_media.image_url
            )

            session.add(deleted_record)
            await session.delete(social_media)
            await session.commit()
            return True

        except Exception as e:
            await session.rollback()
            print(f"Error details: {str(e)}")
            raise Exception(f"Error al procesar la eliminación: {e}")
        
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

