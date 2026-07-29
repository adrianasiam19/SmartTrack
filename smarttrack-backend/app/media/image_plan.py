"""
Image Planner — LLM/rules decide WHAT image is needed, never fetch URLs.

Produces structured ImagePlan metadata consumed by ImageRetrievalService.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

DEFAULT_AVOID = [
    "book cover",
    "textbook cover",
    "textbook",
    "book page",
    "logo",
    "advertisement",
    "poster",
    "wallpaper",
    "clip art",
    "clipart",
    "decorative",
    "title page",
    "front cover",
    "isbn",
    "publisher",
    "stock photo model",
    "landscape",
    "mountain lake",
    "scenic",
    "tourism",
]

IMAGE_TYPES = (
    "labelled_diagram",
    "scientific_diagram",
    "photograph",
    "map",
    "graph",
    "illustration",
)


@dataclass
class ImagePlan:
    """Structured request for an educational visual — no URLs."""

    needed: bool = True
    concept: str = ""
    subject: str = ""
    image_type: str = "scientific_diagram"
    requires_labels: bool = False
    preferred_format: str = "png"  # svg | png | any
    search_keywords: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=lambda: list(DEFAULT_AVOID))
    reason: str = ""

    def primary_query(self) -> str:
        if self.search_keywords:
            return self.search_keywords[0]
        concept = (self.concept or "").strip()
        if not concept:
            return ""
        if self.requires_labels:
            return f"Labelled {concept} Diagram"
        if self.image_type == "photograph":
            return f"{concept} real-life photograph educational"
        if self.image_type == "map":
            return f"{concept} educational map"
        if self.image_type == "graph":
            return f"{concept} educational graph chart"
        return f"{concept} diagram"

    def query_variants(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for q in [self.primary_query(), *self.search_keywords]:
            q = re.sub(r"\s+", " ", (q or "").strip())
            key = q.lower()
            if q and key not in seen:
                seen.add(key)
                out.append(q)
        if self.requires_labels and self.concept:
            for extra in (
                f"Labelled {self.concept} Diagram",
                f"{self.concept} labelled diagram",
                f"{self.concept} labeled diagram SVG",
            ):
                key = extra.lower()
                if key not in seen:
                    seen.add(key)
                    out.append(extra)
        return out[:6]

    def cache_key(self) -> str:
        parts = [
            self.concept.lower().strip(),
            self.image_type,
            "labels" if self.requires_labels else "plain",
            self.primary_query().lower(),
        ]
        return "|".join(parts)[:200]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> ImagePlan:
        if not isinstance(data, dict):
            return cls(needed=False)
        return cls(
            needed=bool(data.get("needed", True)),
            concept=str(data.get("concept") or data.get("educational_concept") or ""),
            subject=str(data.get("subject") or ""),
            image_type=str(data.get("image_type") or "scientific_diagram"),
            requires_labels=bool(data.get("requires_labels") or data.get("requiresLabels")),
            preferred_format=str(data.get("preferred_format") or "png"),
            search_keywords=[
                str(x) for x in (data.get("search_keywords") or data.get("keywords") or []) if str(x).strip()
            ],
            avoid=[str(x) for x in (data.get("avoid") or DEFAULT_AVOID)],
            reason=str(data.get("reason") or ""),
        )


class ImagePlanner:
    """
    Builds ImagePlan from curriculum topics, challenge context, or LLM analysis.
    Never retrieves images.
    """

    @staticmethod
    def plan_from_curriculum_topic(
        topic: dict[str, str] | None,
        *,
        subject: str = "",
        requires_labels: bool = False,
        question_type: str = "",
    ) -> ImagePlan:
        if not topic:
            return ImagePlan(needed=False, subject=subject)
        concept = str(topic.get("topic") or "").strip()
        raw_query = str(topic.get("image_query") or concept).strip()
        qtype = (question_type or "").lower()
        needs_labels = requires_labels or qtype in ("diagram_label",)
        image_type = "labelled_diagram" if needs_labels else "scientific_diagram"
        # Heuristic type from query
        ql = raw_query.lower()
        if any(w in ql for w in ("map", "continent", "climate zone")):
            image_type = "map"
        elif any(w in ql for w in ("chart", "graph", "histogram", "pie")):
            image_type = "graph"
        elif any(w in ql for w in ("pollution", "photograph", "real-life", "mining", "urban")):
            image_type = "photograph" if not needs_labels else image_type

        keywords = []
        if needs_labels:
            keywords.append(f"Labelled {concept} Diagram" if concept else "Labelled scientific diagram")
            keywords.append(raw_query if "label" in raw_query.lower() else f"labelled {raw_query}")
        else:
            keywords.append(raw_query)
            if concept and concept.lower() not in raw_query.lower():
                keywords.append(f"{concept} diagram")

        avoid = list(DEFAULT_AVOID)
        # Ambiguous optics word "reflection" often returns scenic lake photos
        if any(w in ql for w in ("reflection", "mirror", "optics", "incident")):
            avoid.extend(["lake", "mountain", "landscape", "forest", "sunset", "nature photo"])
            if "ray" not in ql:
                keywords.insert(0, f"{raw_query} ray diagram plane mirror".strip())
            image_type = "labelled_diagram" if needs_labels else "scientific_diagram"

        return ImagePlan(
            needed=True,
            concept=concept or raw_query,
            subject=subject,
            image_type=image_type,
            requires_labels=needs_labels,
            preferred_format="svg" if needs_labels else "png",
            search_keywords=keywords,
            avoid=avoid,
            reason=str(topic.get("focus") or "curriculum visual aid"),
        )

    @staticmethod
    def plan_from_lesson(*, title: str, subject: str, introduction: str = "") -> ImagePlan:
        """Rule-based plan for Learning Center lessons."""
        blob = f"{title} {introduction}".lower()
        concept = title.strip() or subject
        requires_labels = any(
            k in blob
            for k in (
                "cell",
                "heart",
                "circuit",
                "neuron",
                "flower",
                "digestive",
                "eye",
                "leaf",
                "organelle",
                "anatomy",
            )
        )
        image_type = "labelled_diagram" if requires_labels else "scientific_diagram"
        if any(k in blob for k in ("map", "geography", "continent", "climate")):
            image_type = "map"
            requires_labels = False
        if any(k in blob for k in ("pollution", "environment", "settlement", "community")):
            image_type = "photograph"
            requires_labels = False

        keywords = (
            [f"Labelled {concept} Diagram", f"{concept} labelled diagram"]
            if requires_labels
            else [f"{concept} diagram", f"{concept} educational illustration"]
        )
        return ImagePlan(
            needed=True,
            concept=concept,
            subject=subject,
            image_type=image_type,
            requires_labels=requires_labels,
            preferred_format="svg" if requires_labels else "png",
            search_keywords=keywords,
            avoid=list(DEFAULT_AVOID),
            reason="learning center visual aid",
        )

    @staticmethod
    async def plan_with_llm(
        *,
        subject: str,
        context_text: str,
        question_type: str = "",
        prefer_labels: bool = False,
    ) -> ImagePlan:
        """
        LLM analyses context and returns ImagePlan JSON only — no URLs.
        Falls back to rule-based planning if the API is unavailable.
        """
        if not settings.DEEPSEEK_API_KEY:
            return ImagePlanner.plan_from_lesson(
                title=context_text[:80],
                subject=subject,
                introduction=context_text,
            )

        prompt = (
            "You are the Atlas Image Planner. Analyse the educational content and decide "
            "what visual would help a learner. Do NOT invent image URLs.\n"
            "Return ONLY JSON with keys:\n"
            "needed (bool), concept (string), subject (string), "
            "image_type (one of: labelled_diagram, scientific_diagram, photograph, map, graph, illustration), "
            "requires_labels (bool), preferred_format (svg|png|any), "
            "search_keywords (array of short concept-focused search phrases), "
            "avoid (array), reason (short string).\n"
            "Search keywords must name the CONCEPT (e.g. 'Labelled Osmosis Diagram'), "
            "never the full question wording or SHS labels.\n"
            f"Subject: {subject}\n"
            f"Question type: {question_type or 'n/a'}\n"
            f"Prefer labels: {prefer_labels}\n"
            f"Content:\n{context_text[:2000]}\n"
        )
        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                res = await client.post(
                    "https://api.deepseek.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}"},
                    json={
                        "model": settings.DEEPSEEK_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You plan educational images. JSON only. No URLs.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.2,
                    },
                )
                if res.status_code != 200:
                    raise RuntimeError(f"HTTP {res.status_code}")
                content = res.json()["choices"][0]["message"]["content"]
                parsed = _parse_json(content)
                if not parsed:
                    raise RuntimeError("no json")
                plan = ImagePlan.from_dict(parsed)
                if prefer_labels:
                    plan.requires_labels = True
                    plan.image_type = "labelled_diagram"
                    plan.preferred_format = "svg"
                if not plan.subject:
                    plan.subject = subject
                if not plan.avoid:
                    plan.avoid = list(DEFAULT_AVOID)
                if not plan.search_keywords and plan.concept:
                    plan.search_keywords = (
                        [f"Labelled {plan.concept} Diagram"]
                        if plan.requires_labels
                        else [f"{plan.concept} diagram"]
                    )
                return plan
        except Exception as exc:
            logger.info("ImagePlanner LLM fallback: %s", exc)
            return ImagePlanner.plan_from_lesson(
                title=context_text[:80],
                subject=subject,
                introduction=context_text,
            )


def _parse_json(content: str) -> dict[str, Any] | None:
    content = (content or "").strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", content, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                return None
    return None
