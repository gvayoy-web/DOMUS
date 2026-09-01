from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa_docx"

font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)

for stem in ("tecnico_actualizado", "guia_actualizada"):
    pdf_path = QA / f"{stem}.pdf"
    page_dir = QA / stem
    page_dir.mkdir(exist_ok=True)
    pdf = pdfium.PdfDocument(pdf_path)
    thumbs = []
    for index in range(len(pdf)):
        page = pdf[index]
        full = page.render(scale=1.45).to_pil().convert("RGB")
        out = page_dir / f"page-{index + 1:02d}.png"
        full.save(out)
        thumb = full.copy()
        thumb.thumbnail((420, 560))
        card = Image.new("RGB", (450, 610), "#DCE4EE")
        card.paste(thumb, ((450 - thumb.width) // 2, 35))
        d = ImageDraw.Draw(card)
        d.text((16, 6), f"Página {index + 1}", font=font, fill="#172033")
        thumbs.append(card)
    cols = 3
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 450, rows * 610), "#AAB6C5")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % cols) * 450, (i // cols) * 610))
    sheet.save(QA / f"{stem}_contact_sheet.png")
    print(stem, len(pdf), "pages")
