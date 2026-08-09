"""
Stage 2 — Intelligent Image Planning.

The LLM (or rule-based fallback) decides WHAT image to search for.
It NEVER retrieves images and NEVER invents image URLs.

Produces structured ImagePlan metadata for ImageRetrievalService (Stage 3).
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from typing import Any
from urllib.parse import urlparse

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
    "cartoon",
    "cartoons",
    "meme",
    "memes",
    "watermark",
    "watermarks",
    "unrelated artwork",
    "decorative",
    "decorative graphics",
    "low-quality",
    "blurry",
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
    "illustration",
    "photograph",
    "chart",
    "graph",
    "svg",
    "map",
)

_IMAGE_TYPE_ALIASES = {
    "labeled_diagram": "labelled_diagram",
    "labelled": "labelled_diagram",
    "diagram": "scientific_diagram",
    "scientific": "scientific_diagram",
    "photo": "photograph",
    "picture": "photograph",
    "charts": "chart",
    "graphs": "graph",
    "maps": "map",
}


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
    planner_source: str = "rules"  # rules | llm

    def primary_query(self) -> str:
        if self.search_keywords:
            return self.search_keywords[0]
        concept = (self.concept or "").strip()
        if not concept:
            return ""
        if self.requires_labels or self.image_type in ("labelled_diagram", "svg"):
            return f"labelled {concept} diagram"
        if self.image_type == "photograph":
            return f"{concept} educational photograph"
        if self.image_type == "map":
            return f"{concept} educational map"
        if self.image_type in ("graph", "chart"):
            return f"{concept} educational {self.image_type}"
        if self.image_type == "illustration":
            return f"{concept} educational illustration"
        return f"{concept} educational diagram"

    def query_variants(self) -> list[str]:
        """Ranked educational search phrases (primary first)."""
        seen: set[str] = set()
        out: list[str] = []
        for q in [*self.search_keywords, self.primary_query()]:
            q = _clean_phrase(q)
            key = q.lower()
            if q and key not in seen and not _looks_like_url(q):
                seen.add(key)
                out.append(q)
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
        image_type = _normalize_image_type(
            str(data.get("image_type") or data.get("preferred_image_type") or "scientific_diagram")
        )
        preferred_format = str(data.get("preferred_format") or "png").lower().strip()
        if image_type == "svg":
            preferred_format = "svg"
            image_type = "labelled_diagram"
        if preferred_format not in ("svg", "png", "any"):
            preferred_format = "png"
        keywords = [
            _clean_phrase(str(x))
            for x in (
                data.get("search_keywords")
                or data.get("search_phrases")
                or data.get("keywords")
                or []
            )
            if str(x).strip() and not _looks_like_url(str(x))
        ]
        avoid = [
            str(x).strip()
            for x in (data.get("avoid") or data.get("images_to_avoid") or DEFAULT_AVOID)
            if str(x).strip()
        ]
        return cls(
            needed=bool(data.get("needed", True)),
            concept=_clean_phrase(
                str(data.get("concept") or data.get("educational_concept") or "")
            ),
            subject=str(data.get("subject") or ""),
            image_type=image_type,
            requires_labels=bool(
                data.get("requires_labels")
                or data.get("requiresLabels")
                or image_type == "labelled_diagram"
            ),
            preferred_format=preferred_format,
            search_keywords=keywords,
            avoid=avoid or list(DEFAULT_AVOID),
            reason=str(data.get("reason") or "")[:240],
            planner_source=str(data.get("planner_source") or "llm"),
        )


def _looks_like_url(value: str) -> bool:
    text = (value or "").strip().lower()
    if not text:
        return False
    if "http://" in text or "https://" in text or "www." in text:
        return True
    try:
        parsed = urlparse(text)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def _clean_phrase(value: str) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip())
    text = re.sub(r"(?i)\b(shs\s*[123]|wassce|waec)\b", "", text)
    text = re.sub(r"\s+", " ", text).strip(" -,:;")
    return text[:120]


def _normalize_image_type(raw: str) -> str:
    key = re.sub(r"[\s\-]+", "_", (raw or "").strip().lower())
    key = _IMAGE_TYPE_ALIASES.get(key, key)
    if key in IMAGE_TYPES:
        return key
    return "scientific_diagram"


def _merge_avoid(extra: list[str] | None = None) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in [*(extra or []), *DEFAULT_AVOID]:
        key = item.lower().strip()
        if key and key not in seen:
            seen.add(key)
            out.append(item.strip())
    return out


def _ensure_ranked_phrases(plan: ImagePlan) -> ImagePlan:
    """Guarantee 2–3 educational search phrases ranked by relevance."""
    phrases = [_clean_phrase(p) for p in plan.search_keywords if _clean_phrase(p)]
    phrases = [p for p in phrases if not _looks_like_url(p)]
    concept = plan.concept or "educational concept"

    if plan.requires_labels or plan.image_type in ("labelled_diagram", "svg"):
        defaults = [
            f"labelled {concept} diagram",
            f"{concept} labelled diagram for students",
            f"{concept} labeled scientific diagram SVG",
        ]
    elif plan.image_type == "map":
        defaults = [
            f"{concept} educational map",
            f"{concept} labelled map diagram",
            f"{concept} geography map for students",
        ]
    elif plan.image_type in ("graph", "chart"):
        defaults = [
            f"{concept} educational {plan.image_type}",
            f"{concept} student {plan.image_type} diagram",
            f"{concept} classroom {plan.image_type}",
        ]
    elif plan.image_type == "photograph":
        defaults = [
            f"{concept} educational photograph",
            f"{concept} real life educational photo",
            f"{concept} classroom photograph",
        ]
    elif plan.image_type == "illustration":
        defaults = [
            f"{concept} educational illustration",
            f"{concept} scientific illustration",
            f"{concept} textbook-style illustration",
        ]
    else:
        defaults = [
            f"{concept} educational diagram",
            f"{concept} scientific diagram for students",
            f"{concept} classroom illustration",
        ]

    seen: set[str] = set()
    merged: list[str] = []
    for phrase in [*phrases, *defaults]:
        key = phrase.lower()
        if key and key not in seen:
            seen.add(key)
            merged.append(phrase)
        if len(merged) >= 3:
            break

    plan.search_keywords = merged[:3]
    plan.avoid = _merge_avoid(plan.avoid)
    if plan.requires_labels and plan.preferred_format == "png":
        plan.preferred_format = "svg"
    if plan.image_type == "svg":
        plan.image_type = "labelled_diagram"
        plan.requires_labels = True
        plan.preferred_format = "svg"
    return plan


class ImagePlanner:
    """
    Stage 2 Image Planner — builds search metadata only.
    Never retrieves images or invents URLs.
    """

    @staticmethod
    def plan_from_curriculum_topic(
        topic: dict[str, str] | None,
        *,
        subject: str = "",
        requires_labels: bool = False,
        question_type: str = "",
    ) -> ImagePlan:
        """Rule-based fallback planner for challenge curriculum topics."""
        if not topic:
            return ImagePlan(needed=False, subject=subject, planner_source="rules")
        concept = _clean_phrase(str(topic.get("topic") or "").strip())
        raw_query = _clean_phrase(str(topic.get("image_query") or concept).strip())
        qtype = (question_type or "").lower()
        needs_labels = requires_labels or qtype in ("diagram_label",)
        image_type = "labelled_diagram" if needs_labels else "scientific_diagram"
        ql = raw_query.lower()
        if any(w in ql for w in ("map", "continent", "climate zone")):
            image_type = "map"
        elif any(w in ql for w in ("chart", "graph", "histogram", "pie")):
            image_type = "graph"
        elif any(w in ql for w in ("pollution", "photograph", "real-life", "mining", "urban")):
            image_type = "photograph" if not needs_labels else image_type

        keywords: list[str] = []
        if needs_labels:
            keywords.extend(
                [
                    f"labelled {concept} diagram" if concept else "labelled scientific diagram",
                    f"{raw_query} labelled diagram" if raw_query else f"labelled {concept} diagram",
                    f"{concept} labeled diagram SVG" if concept else "labeled diagram SVG",
                ]
            )
        else:
            keywords.append(raw_query or f"{concept} educational diagram")
            if concept and concept.lower() not in (raw_query or "").lower():
                keywords.append(f"{concept} educational diagram")
            keywords.append(f"{concept or raw_query} scientific illustration")

        avoid = list(DEFAULT_AVOID)
        if any(w in ql for w in ("reflection", "mirror", "optics", "incident")):
            avoid.extend(["lake", "mountain", "landscape", "forest", "sunset", "nature photo"])
            keywords.insert(0, f"{raw_query} ray diagram plane mirror".strip())
            image_type = "labelled_diagram" if needs_labels else "scientific_diagram"

        plan = ImagePlan(
            needed=True,
            concept=concept or raw_query,
            subject=subject,
            image_type=image_type,
            requires_labels=needs_labels,
            preferred_format="svg" if needs_labels else "png",
            search_keywords=keywords,
            avoid=avoid,
            reason=str(topic.get("focus") or "curriculum visual aid"),
            planner_source="rules",
        )
        return _ensure_ranked_phrases(plan)

    @staticmethod
    def plan_from_lesson(*, title: str, subject: str, introduction: str = "") -> ImagePlan:
        """Rule-based fallback planner for Learning Center lessons."""
        blob = f"{title} {introduction}".lower()
        concept = _clean_phrase(title.strip() or subject)
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
                "osmosis",
            )
        )
        image_type = "labelled_diagram" if requires_labels else "scientific_diagram"
        if any(k in blob for k in ("map", "geography", "continent", "climate")):
            image_type = "map"
            requires_labels = False
        if any(k in blob for k in ("pollution", "environment", "settlement", "community")):
            image_type = "photograph"
            requires_labels = False
        if any(k in blob for k in ("graph", "chart", "histogram")):
            image_type = "chart"

        if requires_labels:
            keywords = [
                f"labelled {concept} diagram",
                f"{concept} labelled diagram for students",
                f"{concept} labeled scientific diagram",
            ]
        elif image_type == "map":
            keywords = [
                f"{concept} educational map",
                f"{concept} geography map diagram",
                f"{concept} labelled map for students",
            ]
        elif image_type == "photograph":
            keywords = [
                f"{concept} educational photograph",
                f"{concept} real life educational photo",
                f"{concept} classroom photograph",
            ]
        else:
            keywords = [
                f"{concept} educational diagram",
                f"{concept} scientific illustration",
                f"{concept} educational illustration for students",
            ]

        plan = ImagePlan(
            needed=True,
            concept=concept,
            subject=subject,
            image_type=image_type,
            requires_labels=requires_labels,
            preferred_format="svg" if requires_labels else "png",
            search_keywords=keywords,
            avoid=list(DEFAULT_AVOID),
            reason="learning center visual aid",
            planner_source="rules",
        )
        return _ensure_ranked_phrases(plan)

    @staticmethod
    async def plan_with_llm(
        *,
        subject: str,
        context_text: str,
        question_type: str = "",
        prefer_labels: bool = False,
        topic_hint: str = "",
        title: str = "",
    ) -> ImagePlan:
        """
        LLM Image Planner — returns structured search metadata only (no URLs).
        Falls back to rule-based planning if the API is unavailable.
        """
        fallback = ImagePlanner.plan_from_lesson(
            title=(title or topic_hint or context_text[:80]),
            subject=subject,
            introduction=context_text,
        )
        if prefer_labels:
            fallback.requires_labels = True
            fallback.image_type = "labelled_diagram"
            fallback.preferred_format = "svg"
            fallback = _ensure_ranked_phrases(fallback)

        if not (getattr(settings, "DEEPSEEK_API_KEY", "") or "").strip():
            return fallback

        prompt = (
            "You are the Atlas Image Planner for Ghana SHS education.\n"
            "A visual aid IS needed for this topic. Plan HOW to search for it.\n"
            "CRITICAL RULES:\n"
            "- Do NOT invent, guess, or return image URLs.\n"
            "- Do NOT return http/https links of any kind.\n"
            "- Produce 2–3 educational search phrases ranked by relevance "
            "(best first). Prefer specific phrases like "
            "'plant cell osmosis labelled diagram' over vague ones like 'osmosis'.\n"
            "- Choose a preferred image type.\n"
            "- Say whether lettered labels are required.\n"
            "- List images to avoid (cartoons, memes, logos, watermarks, "
            "unrelated artwork, decorative graphics, low-quality images, book covers).\n\n"
            "Return ONLY JSON with keys:\n"
            "needed (true),\n"
            "concept (short educational concept),\n"
            "subject (string),\n"
            "image_type (one of: labelled_diagram, scientific_diagram, illustration, "
            "photograph, chart, graph, svg, map),\n"
            "requires_labels (bool),\n"
            "preferred_format (svg|png|any),\n"
            "search_keywords (array of 2–3 ranked search phrases),\n"
            "avoid (array of strings),\n"
            "reason (short string).\n\n"
            f"Subject: {subject}\n"
            f"Title: {title or '(none)'}\n"
            f"Topic hint: {topic_hint or '(none)'}\n"
            f"Question type: {question_type or 'n/a'}\n"
            f"Prefer labels: {prefer_labels}\n"
            f"Content:\n{(context_text or '')[:2000]}\n"
        )
        try:
            from app.llm.deepseek_client import deepseek_message_content, llm_circuit_open

            if llm_circuit_open():
                return fallback

            content = await deepseek_message_content(
                [
                    {
                        "role": "system",
                        "content": (
                            "You are an educational Image Planner. "
                            "Return JSON search metadata only. Never URLs."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                read_timeout=15.0,
                purpose="image_plan",
            )
            if not content:
                raise RuntimeError("no content")
            parsed = _parse_json(content)
            if not parsed:
                raise RuntimeError("no json")
            # Reject any plan that smuggled URLs into keyword fields
            raw_keywords = parsed.get("search_keywords") or parsed.get("search_phrases") or []
            if any(_looks_like_url(str(x)) for x in raw_keywords):
                raise RuntimeError("planner returned URL-like keywords")

            plan = ImagePlan.from_dict(parsed)
            plan.needed = True
            plan.planner_source = "llm"
            if prefer_labels:
                plan.requires_labels = True
                plan.image_type = "labelled_diagram"
                plan.preferred_format = "svg"
            if not plan.subject:
                plan.subject = subject
            if not plan.concept:
                plan.concept = topic_hint or title or fallback.concept
            plan = _ensure_ranked_phrases(plan)
            logger.info(
                "Image plan (llm): concept=%r type=%s labels=%s queries=%s",
                plan.concept,
                plan.image_type,
                plan.requires_labels,
                plan.search_keywords,
            )
            return plan
        except Exception as exc:
            logger.info("ImagePlanner LLM fallback: %s", exc)
            return fallback

    @staticmethod
    async def plan_for_learning(
        *,
        subject: str,
        title: str,
        introduction: str = "",
        topic_hint: str = "",
    ) -> ImagePlan:
        """Stage 2 entry for Learning Center (LLM planner + rules fallback)."""
        context = f"{title}\n{introduction}".strip()
        return await ImagePlanner.plan_with_llm(
            subject=subject,
            context_text=context,
            title=title,
            topic_hint=topic_hint or title,
        )

    @staticmethod
    async def plan_for_challenge(
        *,
        subject: str,
        topic: dict[str, str] | None,
        question_type: str = "",
        prefer_labels: bool = False,
        topic_hint: str = "",
    ) -> ImagePlan:
        """Stage 2 entry for Challenge questions (LLM planner + rules fallback)."""
        topic = topic or {}
        title = str(topic.get("topic") or topic_hint or subject)
        context = (
            f"{topic.get('topic') or ''}\n"
            f"{topic.get('focus') or ''}\n"
            f"{topic.get('image_query') or ''}"
        ).strip()
        plan = await ImagePlanner.plan_with_llm(
            subject=subject,
            context_text=context or title,
            question_type=question_type,
            prefer_labels=prefer_labels,
            topic_hint=topic_hint or title,
            title=title,
        )
        # If LLM unavailable path already returned rules via plan_from_lesson,
        # enrich with curriculum-topic rules when topic metadata is richer.
        if plan.planner_source == "rules" and topic:
            ruled = ImagePlanner.plan_from_curriculum_topic(
                topic,
                subject=subject,
                requires_labels=prefer_labels or plan.requires_labels,
                question_type=question_type,
            )
            return ruled
        return plan


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
