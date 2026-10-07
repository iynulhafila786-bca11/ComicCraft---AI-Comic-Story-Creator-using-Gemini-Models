from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout

router = APIRouter()
settings = get_settings()
templates = Jinja2Templates(directory=str(settings.templates_dir))

def _generate_comic(data: PromptRequest):
    outline = generate_outline(data)
    story = generate_story(data, outline)
    images = [
        generate_image(
            panel.image_prompt,
            panel.panel_number,
            settings.panels_dir,
            settings.image_provider,
            settings.hf_token,
            settings.hf_image_model,
            settings.local_image_model,
        )
        for panel in story
    ]
    layout = build_comic_layout(story, images)
    pdf = save_pdf(layout, settings.exports_dir)
    return layout, pdf

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})

@router.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    data = PromptRequest(
        story_prompt=story_prompt.strip(),
        character_name=character_name.strip(),
        setting=setting.strip(),
        tone=tone.strip(),
        art_style=art_style.strip(),
    )
    try:
        layout, pdf = _generate_comic(data)
        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={"request": request, "layout": layout, "pdf_url": f"/download/{pdf.name}"},
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"request": request, "error": str(exc), "form_data": data.model_dump()},
            status_code=500,
        )

@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    try:
        layout, pdf = _generate_comic(payload)
        return {"success": True, "layout": layout, "pdf_url": f"/download/{pdf.name}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.get("/download/{filename}")
async def download_pdf(filename: str):
    safe_name = Path(filename).name
    path = settings.exports_dir / safe_name
    if not path.exists() or path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="PDF not found.")
    return FileResponse(path, media_type="application/pdf", filename=safe_name)

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse(request=request, name="export_success.html", context={"request": request})

@router.get("/test-image")
async def test_image(prompt: str = "A brave fox in an enchanted forest, comic book style"):
    try:
        path = generate_image(
            prompt, 0, settings.panels_dir, settings.image_provider,
            settings.hf_token, settings.hf_image_model, settings.local_image_model
        )
        return {"success": True, "image_url": f"/static/panels/{path.name}"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
