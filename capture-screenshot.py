import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import subprocess
import jinja2
import shutil
import pathlib

QUARTO_PROJECT_FOLDER = pathlib.Path("quarto-project")
QUARTO_CONFIG_PATH = QUARTO_PROJECT_FOLDER / "_quarto.yml"
QUARTO_INDEX_PATH = QUARTO_PROJECT_FOLDER / "index.qmd"
FLAVORS = ["latte", "frappe", "macchiato", "mocha"]


def create_quarto_website_project(flavor: str):
    subprocess.run(
        [
            "quarto",
            "create",
            "project",
            "website",
            str(QUARTO_PROJECT_FOLDER),
            "--no-prompt",
            "--no-open",
        ],
        check=True,
    )

    QUARTO_INDEX_PATH.unlink()
    QUARTO_CONFIG_PATH.unlink()

    jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    quarto_configuration_template = jinja_environment.get_template("_quarto.yml")

    with open(QUARTO_CONFIG_PATH, "w") as configuration_file:
        configuration_file.write(quarto_configuration_template.render(flavor=flavor))

    shutil.copy("index.qmd", QUARTO_INDEX_PATH)

    style = f"catppuccin-{flavor}.scss"
    shutil.copy(f"themes/{style}", QUARTO_PROJECT_FOLDER / style)


def render_quarto_project(flavor: str):
    subprocess.run(
        [
            "quarto",
            "render",
            QUARTO_PROJECT_FOLDER,
            "--to",
            "html",
        ],
        check=True,
    )


async def capture_screenshot(flavor: str):
    async with async_playwright() as playwright_manager:
        browser_instance = await playwright_manager.chromium.launch()
        browser_page = await browser_instance.new_page()

        absolute_file_path = Path(f"{QUARTO_PROJECT_FOLDER}/_site/index.html").resolve()

        await browser_page.goto(f"file://{absolute_file_path}")
        await browser_page.screenshot(path=f"assets/{flavor}.png")
        await browser_instance.close()


if __name__ == "__main__":
    for flavor in FLAVORS:
        create_quarto_website_project(flavor)
        render_quarto_project(flavor)
        asyncio.run(capture_screenshot(flavor))
        shutil.rmtree(QUARTO_PROJECT_FOLDER)
