"""Multi-taxpayer family bundle segregation engine (Phase 1.3).

The problem: in ITR season a client emails ONE PDF containing the husband's
Form 16, the wife's LIC receipt, and the father's pension statement. The OCR
pipeline sees a single document, but it actually bundles several taxpayers'
papers that must be linked to different individual client-member profiles.

This module splits multi-page OCR output into logical document segments by
detecting changing identity signals — PANs, employer TANs, and taxpayer
names — across pages, and optionally assigns each segment to a family member
profile (matched by PAN first, then by name similarity).

It is fully deterministic (regex + heuristics, no LLM), so it is cheap to run
on every ingest and easy to unit-test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# PAN: 5 letters, 4 digits, 1 letter (4th char encodes holder type).
PAN_REGEX = re.compile(r"\b([A-Z]{3}[ABCFGHJLPT][A-Z][0-9]{4}[A-Z])\b")
# TAN: 4 letters, 5 digits, 1 letter (employer/deductor identity).
TAN_REGEX = re.compile(r"\b([A-Z]{4}[0-9]{5}[A-Z])\b")

# Lines that typically introduce the taxpayer's name on Indian tax documents.
_NAME_LABELS = (
    "name of deductee",
    "name of employee",
    "name of assessee",
    "name of taxpayer",
    "deductee name",
    "employee name",
    "assessee name",
    "taxpayer name",
    "account holder",
    "policyholder",
    "insured name",
    "proposer name",
)

_STOP_TOKENS = {
    "mr", "mrs", "ms", "shri", "smt", "the", "ltd", "limited", "pvt", "private",
    "co", "company", "india", "bank", "insurance", "life",
}


@dataclass(frozen=True)
class PageInput:
    """One OCR page reduced to plain text."""

    page_index: int
    text: str


@dataclass
class IdentitySignals:
    """Identity evidence found on one page."""

    pans: set[str] = field(default_factory=set)
    tans: set[str] = field(default_factory=set)
    names: list[str] = field(default_factory=list)


@dataclass
class DocumentSegment:
    """A logical sub-document: consecutive pages sharing one taxpayer identity."""

    page_indices: list[int] = field(default_factory=list)
    pan: str | None = None
    tan: str | None = None
    taxpayer_names: list[str] = field(default_factory=list)
    text: str = ""

    @property
    def start_page(self) -> int | None:
        return self.page_indices[0] if self.page_indices else None


@dataclass(frozen=True)
class MemberProfile:
    """Minimal client-member info needed for assignment."""

    member_id: str
    name: str
    pan: str | None = None


@dataclass
class MemberAssignment:
    """A segment assigned to a client member profile."""

    member_id: str
    segment: DocumentSegment
    matched_by: str  # "pan" | "name"


def detect_identity_signals(text: str) -> IdentitySignals:
    """Extract PANs, TANs, and candidate taxpayer names from raw page text."""
    upper = text.upper()
    signals = IdentitySignals(
        pans=set(PAN_REGEX.findall(upper)),
        tans=set(TAN_REGEX.findall(upper)),
    )
    for line in upper.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        for label in _NAME_LABELS:
            idx = stripped.find(label.upper())
            if idx == -1:
                continue
            candidate = stripped[idx + len(label):].strip(" :.-\t")
            candidate = re.split(r"\s{2,}|\t", candidate)[0].strip()
            # Keep plausible person/company names only (>= 2 chars, letters).
            if len(candidate) >= 2 and re.match(r"^[A-Z][A-Za-z .&'-]+$", candidate):
                signals.names.append(candidate.strip())
            break
    return signals


def _segment_key(signals: IdentitySignals) -> frozenset[str]:
    """Identity fingerprint used to compare pages. PAN beats TAN."""
    if signals.pans:
        return frozenset(signals.pans)
    if signals.tans:
        return frozenset(signals.tans)
    return frozenset()


def segregate_pages(pages: list[PageInput]) -> list[DocumentSegment]:
    """Group consecutive OCR pages into per-taxpayer document segments.

    A page starts a new segment when its identity fingerprint differs from
    the open segment's. Pages without any signal (blank separators, annexure
    tables, stamp pages) continue the current segment.
    """
    segments: list[DocumentSegment] = []
    open_segment: DocumentSegment | None = None
    open_key: frozenset[str] = frozenset()

    for page in pages:
        signals = detect_identity_signals(page.text)
        key = _segment_key(signals)

        if open_segment is not None and (not key or key == open_key):
            target = open_segment
        elif open_segment is not None:
            open_segment = None  # close; fall through to open a new one
            target = None
        else:
            target = None

        if target is None:
            open_segment = DocumentSegment(page_indices=[], text="")
            segments.append(open_segment)
            open_key = key
            target = open_segment

        target.page_indices.append(page.page_index)
        target.text += ("\n\n" if target.text else "") + page.text
        # Within a segment the fingerprint is constant, so first wins.
        if signals.pans and not target.pan:
            target.pan = sorted(signals.pans)[0]
        if signals.tans and not target.tan:
            target.tan = sorted(signals.tans)[0]
        target.taxpayer_names.extend(n for n in signals.names if n not in target.taxpayer_names)

    return segments


def _normalize_name(name: str) -> set[str]:
    tokens = re.split(r"[^a-z]+", name.lower())
    return {t for t in tokens if len(t) > 1} - _STOP_TOKENS


def _name_similarity(a: str, b: str) -> float:
    ta, tb = _normalize_name(a), _normalize_name(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / min(len(ta), len(tb))


def assign_segments_to_members(
    segments: list[DocumentSegment],
    members: list[MemberProfile],
    *,
    name_threshold: float = 0.75,
) -> list[MemberAssignment]:
    """Match each segment to a family member by PAN, then by name similarity.

    Unmatched segments are simply omitted from the result (they stay attached
    to the parent client until a reviewer assigns them manually).
    """
    assignments: list[MemberAssignment] = []
    used_members: set[str] = set()

    # Pass 1: PAN match (authoritative).
    for segment in segments:
        if not segment.pan:
            continue
        for member in members:
            if member.member_id in used_members or not member.pan:
                continue
            if member.pan.upper() == segment.pan:
                assignments.append(
                    MemberAssignment(member.member_id, segment, matched_by="pan")
                )
                used_members.add(member.member_id)
                break

    # Pass 2: fuzzy name match for segments still unassigned.
    for segment in segments:
        if any(a.segment is segment for a in assignments):
            continue
        best_member, best_score = None, 0.0
        for member in members:
            if member.member_id in used_members:
                continue
            for name in segment.taxpayer_names:
                score = _name_similarity(name, member.name)
                if score > best_score:
                    best_member, best_score = member, score
        if best_member is not None and best_score >= name_threshold:
            assignments.append(
                MemberAssignment(best_member.member_id, segment, matched_by="name")
            )
            used_members.add(best_member.member_id)

    return assignments


def pages_from_ocr_result(result: dict) -> list[PageInput]:
    """Build PageInput list from a stored OCR result.json structure."""
    pages: list[PageInput] = []
    for index, page in enumerate(result.get("pages", [])):
        text = page.get("text") or ""
        if not text:
            text = "\n".join(block.get("text", "") for block in page.get("blocks", []))
        pages.append(PageInput(page_index=page.get("page_index", index), text=text))
    return pages
