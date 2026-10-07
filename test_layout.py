from pathlib import Path
from app.schemas import StoryPanel
from app.services.layout_builder import build_comic_layout

def test_build_comic_layout():
    story=[StoryPanel(
        panel_number=1,
        title="The Beginning",
        scene_description="A fox enters a forest.",
        image_prompt="A fox entering a forest.",
        caption="The forest was quiet.",
        narration="Finn stepped beneath the trees.",
        dialogue="What is that sound?",
    )]
    layout=build_comic_layout(story,[Path("static/panels/panel_01_test.png")])
    assert len(layout)==1
    assert layout[0]["panel_number"]==1
    assert layout[0]["image_url"].endswith(".png")
