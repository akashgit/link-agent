import io
import logging

logger = logging.getLogger(__name__)


async def parse_file(content: bytes, content_type: str) -> str:
    """Extract text from uploaded files."""
    try:
        if content_type == "application/pdf":
            return _parse_pdf(content)
        elif content_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
            return _parse_pptx(content)
        elif content_type == "text/plain":
            return content.decode("utf-8", errors="replace")
        else:
            return ""
    except Exception as e:
        logger.error(f"File parsing failed: {e}")
        return ""


def _parse_pdf(content: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n\n".join(texts)


def _parse_pptx(content: bytes) -> str:
    from pptx import Presentation

    prs = Presentation(io.BytesIO(content))
    texts = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                texts.append(shape.text_frame.text)
    return "\n\n".join(texts)
