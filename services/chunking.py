from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple


DEFAULT_MAX_TOKENS = 800
DEFAULT_OVERLAP = 100


@dataclass
class Chunk:
    content: str
    section: str
    heading: Optional[str]
    position: int
    token_count: int


def _approx_token_count(text: str) -> int:
    # Simple approximation: ~4 chars per token
    return max(1, int(len(text) / 4))


def _split_by_lines(text: str) -> List[str]:
    return [line for line in text.splitlines()]


def _detect_sections(lines: List[str]) -> List[Tuple[str, Optional[str], List[str]]]:
    sections: List[Tuple[str, Optional[str], List[str]]] = []

    current_section = "other"
    current_heading: Optional[str] = None
    buffer: List[str] = []

    def push():
        nonlocal buffer, current_section, current_heading
        if buffer:
            sections.append((current_section, current_heading, buffer))
            buffer = []

    for line in lines:
        lower = line.strip().lower()
        if lower.startswith("experience") or lower.startswith("work experience"):
            push(); current_section = "experience"; current_heading = "Experience"; continue
        if lower.startswith("skills"):
            push(); current_section = "skills"; current_heading = "Skills"; continue
        if lower.startswith("projects"):
            push(); current_section = "projects"; current_heading = "Projects"; continue
        if lower.startswith("education"):
            push(); current_section = "education"; current_heading = "Education"; continue
        if lower.startswith("certifications") or lower.startswith("certs"):
            push(); current_section = "certs"; current_heading = "Certifications"; continue
        buffer.append(line)

    push()
    if not sections:
        sections.append(("other", None, lines))
    return sections


def chunk_text(text: str, max_tokens: int = DEFAULT_MAX_TOKENS, overlap: int = DEFAULT_OVERLAP) -> List[Chunk]:
    lines = _split_by_lines(text)
    sections = _detect_sections(lines)

    chunks: List[Chunk] = []
    position = 0
    for section, heading, content_lines in sections:
        content = "\n".join(content_lines).strip()
        if not content:
            continue

        # Sliding window by characters approximating tokens
        start = 0
        while start < len(content):
            end = min(len(content), start + max_tokens * 4)
            piece = content[start:end]
            token_count = _approx_token_count(piece)
            chunks.append(Chunk(content=piece, section=section, heading=heading, position=position, token_count=token_count))
            position += 1
            if end == len(content):
                break
            start = max(0, end - overlap * 4)

    return chunks

