from fastapi import FastAPI, HTTPException, Depends, Request, Form, UploadFile
from fastapi.responses import HTMLResponse
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from database.connection_db import get_session
from fastapi.templating import Jinja2Templates
import os

from images.upload_images import save_file
from mental_health_models import *
from social_media_models import *
from mental_health_operations import MentalHealthOperations
from social_media_operations import SocialMediaOperations

app = FastAPI(
    title="Impacto De Las Redes Sociales En La Salud Mental",
    description="API para gestionar registros entre salud mental y redes sociales.",
    version="La última versión"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "..", "templates"))

# Página de inicio
@app.get("/", response_class=HTMLResponse, tags=["Página Principal"])
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# --------------- ELIMINADOS -----------
@app.get("/mental_health/deleted", response_model=List[DeletedMentalHealth], tags=["Eliminados"])
async def get_deleted_mental_health(session: AsyncSession = Depends(get_session)):
    """Obtiene todos los registros de salud mental eliminados"""
    return await MentalHealthOperations.get_deleted_mental_health(session)


@app.get("/social_media/deleted", response_model=List[DeletedSocialMedia], tags=["Eliminados"])
async def get_deleted_videogames(session: AsyncSession = Depends(get_session)):
    """Obtiene todos los registros de redes sociales eliminados"""
    return await SocialMediaOperations.get_deleted_social_media(session)


@app.get("/deleted", response_class=HTMLResponse, tags=["Eliminados"])
async def view_deleted(request: Request, session: AsyncSession = Depends(get_session)):
    deleted_mental_health = await MentalHealthOperations.get_deleted_mental_health(session)
    deleted_social_media = await SocialMediaOperations.get_deleted_social_media(session)

    return templates.TemplateResponse(
        "deleted.html",
        {
            "request": request,
            "deleted_mental_health": deleted_mental_health,
            "deleted_social_media": deleted_social_media
        }
    )

@app.get("/delete", response_class=HTMLResponse, tags=["Eliminación"])
async def delete_page(request: Request):
    """Página para eliminar registros"""
    return templates.TemplateResponse("delete.html", {"request": request})

# -------------------- MENTAL HEALTH --------------------

@app.get("/mental_health", response_class=HTMLResponse, tags=["Salud Mental"])
async def get_mental_health(request: Request, session: AsyncSession = Depends(get_session)):
    records = await MentalHealthOperations.get_all_mental_health(session)
    return templates.TemplateResponse(
        "records.html",
        {
            "request": request,
            "records": records,
            "tipo": "mental_health"
        }
    )

@app.get("/mental_health/search_mental_health_by_age", response_model=List[MentalHealthResponse], tags=["Salud Mental"])
async def search_by_age(age: int, session: AsyncSession = Depends(get_session)):
    results = await MentalHealthOperations.search_mental_health_by_age(session, age)
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron registros con ese edad")
    return results

@app.get("/mental_health/search_mental_health_by_field", response_model=List[MentalHealthResponse], tags=["Salud Mental"])
async def search_cosmetic_by_field(
    field: str,
    value: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca registros de salud mental por cualquier campo especificado.
    Campos disponibles: id,date,age,gender,relationship_status,bothered_by_worries,difficulty_concentrating,comparison_feelings,feel_depressed,fluctuation_interest,sleep_issues,image_url.
    """
    results = await MentalHealthOperations.search_mental_health_by_field(session, field, value)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron registros con {field} que contenga '{value}'"
        )
    return results

@app.get("/mental_health/by_sleep_issues", response_model=List[MentalHealthResponse], tags=["Salud Mental"])
async def filter_mental_health_by_sleep_issues(session: AsyncSession = Depends(get_session)):
    return await MentalHealthOperations.filter_mental_health_by_sleep_issues(session)

@app.get("/mental_health/{mental_health_id}", response_model=MentalHealthResponse, tags=["Salud Mental"])
async def get_mental_health(mental_health_id: int, session: AsyncSession = Depends(get_session)):
    mental_health = await MentalHealthOperations.get_mental_health_by_id(session, mental_health_id)
    if not mental_health:
        raise HTTPException(status_code=404, detail="Registro de salud mental no encontrado")
    return mental_health

@app.post("/mental_health", response_model=MentalHealthResponse, tags=["Salud Mental"])
async def create_mental_health_endpoint(mental_health: MentalHealth, session: AsyncSession = Depends(get_session)):
    return await MentalHealthOperations.create_mental_health(session, mental_health.model_dump())


@app.put("/mental_health/{mental_health_id}", response_model=MentalHealthResponse, tags=["Salud Mental"])
async def update_mental_health_endpoint(
        mental_health_id: int,
        date: str = Form(None),
        age: str = Form(None),
        gender: str = Form(None),
        relationship_status: str = Form(None),
        bothered_by_worries: str = Form(None),
        difficulty_concentrating: str = Form(None),
        comparison_feelings: str = Form(None),
        feel_depressed: str = Form(None),
        fluctuation_interest: str = Form(None),
        sleep_issues: str = Form(None),
        image_file: UploadFile = None,
        session: AsyncSession = Depends(get_session)
):
    """
    Actualiza un registro de colaboración de maquillaje.
    Solo los campos enviados en la solicitud serán actualizados.
    """
    update_data = {}

    # Recopilar campos no nulos
    if date: update_data["date"] = date
    if age: update_data["age"] = age
    if gender: update_data["gender"] = gender
    if relationship_status: update_data["relationship_status"] = relationship_status
    if bothered_by_worries: update_data["bothered_by_worries"] = bothered_by_worries
    if difficulty_concentrating: update_data["difficulty_concentrating"] = difficulty_concentrating
    if comparison_feelings: update_data["comparison_feelings"] = comparison_feelings
    if feel_depressed: update_data["feel_depressed"] = feel_depressed
    if fluctuation_interest: update_data["fluctuation_interest"] = fluctuation_interest
    if sleep_issues: update_data["sleep_issues"] = sleep_issues

    # Si hay una nueva imagen, procesarla
    if image_file and image_file.filename:
        image_url = await save_file(image_file)
        if isinstance(image_url, dict) and "error" in image_url:
            raise HTTPException(status_code=400, detail=image_url["error"])
        update_data["image_url"] = image_url

    updated = await MentalHealthOperations.update_mental_health(session, mental_health_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="La colaboración no fue actualizada")
    return updated


@app.post("/mental_health/upload", tags=["Salud Mental"])
async def create_mental_health_with_image(
    date: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    relationship_status: str = Form(...),
    bothered_by_worries: int = Form(...),
    difficulty_concentrating: int = Form(...),
    comparison_feelings: int = Form(...),
    feel_depressed: int = Form(...),
    fluctuation_interest: int = Form(...),
    sleep_issues: int = Form(...),
    image_file: UploadFile = Form(...),
    session: AsyncSession = Depends(get_session)
):
    image_url = await save_file(image_file)

    if isinstance(image_url, dict) and "error" in image_url:
        raise HTTPException(status_code=400, detail=image_url["error"])

    new_data = MentalHealthCreate(
        date=date,
        age=age,
        gender=gender,
        relationship_status=relationship_status,
        bothered_by_worries=bothered_by_worries,
        difficulty_concentrating=difficulty_concentrating,
        comparison_feelings=comparison_feelings,
        feel_depressed=feel_depressed,
        fluctuation_interest=fluctuation_interest,
        sleep_issues=sleep_issues,
        image_url=image_url
    )

    new_entry = MentalHealth.from_orm(new_data)
    session.add(new_entry)
    await session.commit()
    await session.refresh(new_entry)

    return {"id": new_entry.id}

@app.post("/mental_health/delete", tags=["Salud Mental"])
async def delete_mental_health_by_id(
    request: Request,
    id: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    deleted = await MentalHealthOperations.delete_mental_health(session, id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="El registro de salud mental no fue encontrado"
        )
    return {"message": "Registro de salud mental eliminado con éxito"}


# -------------------- SOCIAL MEDIA --------------------

@app.get("/social_media", response_class=HTMLResponse, tags=["Redes Sociales"])
async def get_social_media(request: Request, session: AsyncSession = Depends(get_session)):
    records = await SocialMediaOperations.get_all_social_media(session)
    return templates.TemplateResponse(
        "records.html",
        {
            "request": request,
            "records": records,
            "tipo": "social_media"
        }
    )

@app.get("/social_media/search_by_gender", response_model=List[SocialMediaResponse], tags=["Redes Sociales"])
async def search_by_gender(gender: str, session: AsyncSession = Depends(get_session)):
    results = await SocialMediaOperations.search_social_media_by_gender(session, gender)
    if not results:
        raise HTTPException(status_code=404, detail="No se encontraron registros de redes sociales con ese género")
    return results

@app.get("/social_media/search_by_field", response_model=List[SocialMediaResponse], tags=["Redes Sociales"])
async def search_social_media_by_field(
    field: str,
    value: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Busca registros de redes sociales por cualquier campo especificado.
    Campos disponibles: id,date,age,gender,occupation_status,organization_affiliation,uses_social_media,platforms_used,daily_use_average,usage_without_purpose,distraction_when_busy,restless_without_social_media,easily_distracted,compare_with_successful_people,seek_validation,image_url
    """
    results = await SocialMediaOperations.search_social_media_by_field(session, field, value)
    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron registros de redes sociales con {field} que contenga '{value}'"
        )
    return results

@app.get("/social_media/by_age", response_model=List[SocialMediaResponse], tags=["Redes Sociales"])
async def filter_social_media_by_age(session: AsyncSession = Depends(get_session)):
    return await SocialMediaOperations.filter_social_media_by_age(session)

@app.get("/social_media/{social_media_id}", response_model=SocialMediaResponse, tags=["Redes Sociales"])
async def get_social_media(social_media_id: int, session: AsyncSession = Depends(get_session)):
    social_media = await SocialMediaOperations.get_social_media_by_id(session, social_media_id)
    if not social_media:
        raise HTTPException(status_code=404, detail="Registro de redes sociales no encontrado")
    return social_media

@app.post("/social_media", response_model=SocialMediaResponse, tags=["Redes Sociales"])
async def create_social_media_endpoint(social_media: SocialMediaCreate, session: AsyncSession = Depends(get_session)):
    return await SocialMediaOperations.create_social_media(session, social_media.model_dump())

@app.put("/social_media/{social_media_id}", response_model=SocialMediaResponse, tags=["Redes Sociales"])
async def update_social_media_endpoint(
        social_media_id: int,
        date: str = Form(None),
        age: int = Form(None),
        gender: str = Form(None),
        occupation_status: str = Form(None),
        organization_affiliation: str = Form(None),
        uses_social_media: str = Form(None),
        platforms_used: str = Form(None),
        daily_use_average: str = Form(None),
        usage_without_purpose: int = Form(None),
        distraction_when_busy: int = Form(None),
        restless_without_social_media: int = Form(None),
        easily_distracted: int = Form(None),
        compare_with_successful_people: int = Form(None),
        seek_validation: int = Form(None),
        image_file: UploadFile = None,
        session: AsyncSession = Depends(get_session)
):
    """
    Actualiza un registro de redes sociales.
    Solo los campos enviados en la solicitud serán actualizados.
    """
    update_data = {}

    # Recopilar campos no nulos
    if date: update_data["date"] = date
    if age is not None: update_data["age"] = age
    if gender: update_data["gender"] = gender
    if occupation_status: update_data["occupation_status"] = occupation_status
    if organization_affiliation is not None: update_data["organization_affiliation"] = organization_affiliation
    if uses_social_media: update_data["uses_social_media"] = uses_social_media
    if platforms_used: update_data["platforms_used"] = platforms_used
    if daily_use_average: update_data["daily_use_average"] = daily_use_average
    if usage_without_purpose is not None: update_data["usage_without_purpose"] = usage_without_purpose
    if distraction_when_busy is not None: update_data["distraction_when_busy"] = distraction_when_busy
    if restless_without_social_media is not None: update_data[
        "restless_without_social_media"] = restless_without_social_media
    if easily_distracted is not None: update_data["easily_distracted"] = easily_distracted
    if compare_with_successful_people is not None: update_data[
        "compare_with_successful_people"] = compare_with_successful_people
    if seek_validation is not None: update_data["seek_validation"] = seek_validation

    # Si hay una nueva imagen, procesarla
    if image_file and image_file.filename:
        image_url = await save_file(image_file)
        if isinstance(image_url, dict) and "error" in image_url:
            raise HTTPException(status_code=400, detail=image_url["error"])
        update_data["image_url"] = image_url

    updated = await SocialMediaOperations.update_social_media(session, social_media_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="El registro de redes sociales no fue actualizado")
    return updated


@app.post("/social_media/upload", tags=["Redes Sociales"])
async def create_social_media_with_image(
    date: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    occupation_status: str = Form(...),
    organization_affiliation: str = Form(...),
    uses_social_media: str = Form(...),
    platforms_used:  List[str] = Form(...),
    daily_use_average: str = Form(...),
    usage_without_purpose: int = Form(...),
    distraction_when_busy: int = Form(...),
    restless_without_social_media: int = Form(...),
    easily_distracted: int = Form(...),
    compare_with_successful_people: int = Form(...),
    seek_validation: int = Form(...),
    image_file: UploadFile = Form(...),
    session: AsyncSession = Depends(get_session)
):
    platforms_str = ", ".join(platforms_used)
    image_url = await save_file(image_file)
    if isinstance(image_url, dict) and "error" in image_url:
        raise HTTPException(status_code=400, detail=image_url["error"])

    new_data = SocialMediaCreate(
        date=date,
        age=age,
        gender=gender,
        occupation_status=occupation_status,
        organization_affiliation=organization_affiliation,
        uses_social_media=uses_social_media,
        platforms_used=platforms_str,
        daily_use_average=daily_use_average,
        usage_without_purpose=usage_without_purpose,
        distraction_when_busy=distraction_when_busy,
        restless_without_social_media=restless_without_social_media,
        easily_distracted=easily_distracted,
        compare_with_successful_people=compare_with_successful_people,
        seek_validation=seek_validation,
        image_url=image_url
    )

    new_colab = SocialMedia.from_orm(new_data)
    session.add(new_colab)
    await session.commit()
    await session.refresh(new_colab)

    return {"id": new_colab.id}


@app.post("/social_media/delete", tags=["Redes Sociales"])
async def delete_social_media_by_id(
    request: Request,
    id: int = Form(...),
    session: AsyncSession = Depends(get_session)
):
    deleted = await SocialMediaOperations.delete_social_media(session, id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="El registro de redes sociales no fue encontrado"
        )
    return {"message": "Registro de redes sociales eliminado con éxito"}

# -------------- MOSTRAR REGISTROS ----------------
@app.get("/show", response_class=HTMLResponse, tags=["Registros"])
async def show_records(
        request: Request,
        session: AsyncSession = Depends(get_session)
):
    mental_health = await MentalHealthOperations.get_all_mental_health(session)
    social_media = await SocialMediaOperations.get_all_social_media(session)

    return templates.TemplateResponse(
        "show.html",
        {
            "request": request,
            "mental_health": mental_health,
            "social_media": social_media
        }
    )

# -------------------- CREACIÓN --------------------
@app.get("/create", response_class=HTMLResponse, tags=["Creación"])
async def create_page(request: Request):
    """Página para crear nuevos registros"""
    return templates.TemplateResponse("create.html", {"request": request})

# --------------- ACTUALIZACIÓN -----------
@app.get("/update", response_class=HTMLResponse, tags=["Actualización"])
async def update_page(request: Request):
    return templates.TemplateResponse("update.html", {"request": request})

# --------------- CONSULTAS -----------
@app.get("/query", response_class=HTMLResponse, tags=["Consultas"])
async def query_page(request: Request):
    return templates.TemplateResponse("query.html", {"request": request})

# --------------- DESARROLLADOR -----------
@app.get("/developer", response_class=HTMLResponse, tags=["Desarrollador"])
async def developer_info(request: Request):
    return templates.TemplateResponse("developer.html", {"request": request})

# --------------- PROYECTO ----------------
@app.get("/goal", response_class=HTMLResponse, tags=["Objetivo Proyecto"])
async def objetivo_proyecto(request: Request):
    return templates.TemplateResponse("goal.html", {"request": request})

# --------------- PLANEACIÓN ----------------
@app.get("/planning", response_class=HTMLResponse, tags=["Planeación"])
async def planeacion_proyecto(request: Request):
    return templates.TemplateResponse("planning.html", {"request":request})

# --------------- DISEÑO ----------------
@app.get("/design", response_class=HTMLResponse, tags=["Diseño"])
async def diseno_proyecto(request: Request):
    return templates.TemplateResponse("design.html", {"request":request})
