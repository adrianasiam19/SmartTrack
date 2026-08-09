"""Educational media: content analysis, images, videos, and learning resources."""

from app.media.content_analysis import (
    VisualNeedDecision,
    analyze_visual_need,
    analyze_visual_need_rules,
)
from app.media.image_plan import ImagePlan, ImagePlanner
from app.media.image_retrieval import (
    ImageRetrievalService,
    retrieve_for_plan,
    retrieve_for_plan_local_only,
    score_image_candidate,
)
from app.media.learning_resources import learning_resource
from app.media.video_retrieval import build_video_queries, retrieve_educational_videos

__all__ = [
    "VisualNeedDecision",
    "analyze_visual_need",
    "analyze_visual_need_rules",
    "ImagePlan",
    "ImagePlanner",
    "ImageRetrievalService",
    "retrieve_for_plan",
    "retrieve_for_plan_local_only",
    "learning_resource",
    "build_video_queries",
    "retrieve_educational_videos",
]
