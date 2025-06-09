from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from mental_health_models import *


class MentalHealthOperations:

    @staticmethod
    async def get_all_mental_health(session: AsyncSession) -> List[MentalHealth]:
        """Obtiene todos los registros de salud mental"""
        result = await session.execute(select(MentalHealth))
        return result.scalars().all()

    @staticmethod
    async def get_mental_health_by_id(session: AsyncSession, entry_id: int) -> Optional[MentalHealth]:
        """Obtiene un registro por su ID"""
        result = await session.execute(
            select(MentalHealth).where(MentalHealth.id == entry_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_mental_health(session: AsyncSession, data: dict) -> MentalHealth:
        """Crea un nuevo registro de salud mental"""
        new_entry = MentalHealth(**data)
        session.add(new_entry)
        await session.commit()
        await session.refresh(new_entry)
        return new_entry

    @staticmethod
    async def update_mental_health(session: AsyncSession, entry_id: int, update_data: dict) -> Optional[MentalHealth]:
        """Modifica un registro existente, permitiendo cambios parciales o totales"""
        entry = await session.get(MentalHealth, entry_id)
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
    async def delete_mental_health(session: AsyncSession, entry_id: int) -> Optional[MentalHealth]:
        """Elimina un registro por ID y lo guarda en deleted_mental_health"""
        entry = await session.get(MentalHealth, entry_id)
        if not entry:
            return None

        try:
            deleted_entry = DeletedMentalHealth(**entry.dict())
        except ValueError as e:
            # Manejar errores de validación
            raise ValueError(f"Error al validar los datos para la tabla de eliminados: {e}")

        await session.delete(entry)
        await session.commit()
        return entry

    @staticmethod
    async def get_deleted_mental_health(session: AsyncSession) -> List[DeletedMentalHealth]:
        """Obtiene todos los registros eliminados de salud mental"""
        result = await session.execute(select(DeletedMentalHealth))
        return result.scalars().all()

    @staticmethod
    async def search_mental_health_by_age(session: AsyncSession, age: int) -> List[MentalHealth]:
        """Busca registros por edad"""
        result = await session.execute(
            select(MentalHealth).where(MentalHealth.age == age)
        )
        return result.scalars().all()

    @staticmethod
    async def filter_mental_health_by_sleep_issues(session: AsyncSession) -> List[MentalHealth]:
        """Filtra y ordena por problemas de sueño (sleep_issues)"""
        result = await session.execute(
            select(MentalHealth).order_by(MentalHealth.sleep_issues)
        )
        return result.scalars().all()

    @staticmethod
    async def search_mental_health_by_field(session: AsyncSession, field: str, value: str) -> List[MentalHealth]:
        """Busca registros por cualquier campo especificado"""
        if not hasattr(MentalHealth, field):
            return []

        model_field = getattr(MentalHealth, field)

        # Determinar el tipo de campo y ajustar la búsqueda
        try:
            if field in ['age', 'bothered_by_worries', 'difficulty_concentrating',
                         'comparison_feelings', 'feel_depressed', 'fluctuation_interest', 'sleep_issues']:
                # Campos numéricos
                numeric_value = int(value)
                result = await session.execute(
                    select(MentalHealth).where(model_field == numeric_value)
                )
            else:
                # Campos de texto
                result = await session.execute(
                    select(MentalHealth).where(model_field.ilike(f"%{value}%"))
                )
            return result.scalars().all()
        except ValueError:
            return []
