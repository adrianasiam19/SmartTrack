"""
Atlas-authored labelled educational diagrams (SVG data URIs).

Stock photos cannot show reliable A/B/C labels. When a challenge asks about
labelled parts, we serve these diagrams with arrows + letter markers so the
question and figure always match.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import quote


def _data_uri(svg: str) -> str:
    return "data:image/svg+xml;charset=utf-8," + quote(svg)


def _label_marker(x: float, y: float, letter: str, tip_x: float, tip_y: float) -> str:
    """Arrow from label badge to target point."""
    return f"""
    <line x1="{x}" y1="{y}" x2="{tip_x}" y2="{tip_y}" stroke="#1E3A8A" stroke-width="2" marker-end="url(#arrow)" />
    <circle cx="{x}" cy="{y}" r="14" fill="#2563EB" stroke="#1E3A8A" stroke-width="1.5"/>
    <text x="{x}" y="{y + 5}" text-anchor="middle" font-size="14" font-family="Arial,sans-serif" font-weight="700" fill="#fff">{letter}</text>
    """


_DEFS = """
<defs>
  <marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
    <path d="M0,0 L6,3 L0,6 Z" fill="#1E3A8A"/>
  </marker>
</defs>
"""


def plant_cell_labelled() -> dict[str, Any]:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
  <rect width="640" height="420" fill="#F8FAFC"/>
  {_DEFS}
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Plant cell (labelled)</text>
  <!-- cell wall -->
  <rect x="120" y="70" width="320" height="300" rx="8" fill="#DCFCE7" stroke="#166534" stroke-width="6"/>
  <!-- membrane -->
  <rect x="135" y="85" width="290" height="270" rx="6" fill="#ECFDF5" stroke="#059669" stroke-width="3"/>
  <!-- nucleus -->
  <circle cx="280" cy="220" r="42" fill="#C7D2FE" stroke="#3730A3" stroke-width="3"/>
  <circle cx="280" cy="220" r="12" fill="#4F46E5"/>
  <!-- vacuole -->
  <ellipse cx="220" cy="150" rx="55" ry="40" fill="#A5F3FC" stroke="#0891B2" stroke-width="2"/>
  <!-- chloroplast -->
  <ellipse cx="360" cy="160" rx="40" ry="22" fill="#86EFAC" stroke="#15803D" stroke-width="2"/>
  <ellipse cx="350" cy="280" rx="36" ry="20" fill="#86EFAC" stroke="#15803D" stroke-width="2"/>
  {_label_marker(70, 120, "A", 120, 140)}
  {_label_marker(520, 150, "B", 390, 160)}
  {_label_marker(520, 230, "C", 320, 220)}
  {_label_marker(70, 300, "D", 180, 160)}
  <text x="40" y="380" font-size="12" font-family="Arial" fill="#334155">A = cell wall · B = chloroplast · C = nucleus · D = vacuole</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Labelled plant cell diagram",
        "attribution": "Atlas labelled diagram",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": {
            "A": "cell wall",
            "B": "chloroplast",
            "C": "nucleus",
            "D": "vacuole",
        },
        "key": "plant_cell",
    }


def animal_cell_labelled() -> dict[str, Any]:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
  <rect width="640" height="420" fill="#F8FAFC"/>
  {_DEFS}
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Animal cell (labelled)</text>
  <ellipse cx="300" cy="220" rx="160" ry="130" fill="#DBEAFE" stroke="#1D4ED8" stroke-width="4"/>
  <circle cx="300" cy="210" r="45" fill="#C7D2FE" stroke="#3730A3" stroke-width="3"/>
  <circle cx="300" cy="210" r="14" fill="#4F46E5"/>
  <ellipse cx="220" cy="160" rx="28" ry="18" fill="#FCA5A5" stroke="#B91C1C" stroke-width="2"/>
  <ellipse cx="380" cy="280" rx="30" ry="18" fill="#FCA5A5" stroke="#B91C1C" stroke-width="2"/>
  {_label_marker(80, 140, "A", 160, 160)}
  {_label_marker(520, 200, "B", 340, 210)}
  {_label_marker(80, 280, "C", 200, 250)}
  {_label_marker(520, 300, "D", 400, 280)}
  <text x="40" y="380" font-size="12" font-family="Arial" fill="#334155">A = cell membrane · B = nucleus · C = cytoplasm · D = mitochondrion</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Labelled animal cell diagram",
        "attribution": "Atlas labelled diagram",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": {
            "A": "cell membrane",
            "B": "nucleus",
            "C": "cytoplasm",
            "D": "mitochondrion",
        },
        "key": "animal_cell",
    }


def heart_labelled() -> dict[str, Any]:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
  <rect width="640" height="420" fill="#F8FAFC"/>
  {_DEFS}
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Human heart (labelled)</text>
  <path d="M320 120 C260 80 180 110 180 190 C180 260 260 320 320 360 C380 320 460 260 460 190 C460 110 380 80 320 120 Z" fill="#FECACA" stroke="#B91C1C" stroke-width="4"/>
  <line x1="320" y1="150" x2="320" y2="340" stroke="#7F1D1D" stroke-width="2"/>
  <line x1="200" y1="230" x2="440" y2="230" stroke="#7F1D1D" stroke-width="2"/>
  {_label_marker(90, 160, "A", 230, 170)}
  {_label_marker(540, 160, "B", 410, 170)}
  {_label_marker(90, 300, "C", 240, 300)}
  {_label_marker(540, 300, "D", 400, 300)}
  <text x="40" y="390" font-size="12" font-family="Arial" fill="#334155">A = right atrium · B = left atrium · C = right ventricle · D = left ventricle</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Labelled human heart diagram",
        "attribution": "Atlas labelled diagram",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": {
            "A": "right atrium",
            "B": "left atrium",
            "C": "right ventricle",
            "D": "left ventricle",
        },
        "key": "heart",
    }


def circuit_labelled() -> dict[str, Any]:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <rect width="640" height="360" fill="#F8FAFC"/>
  {_DEFS}
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Series circuit (labelled)</text>
  <rect x="120" y="120" width="400" height="140" fill="none" stroke="#0F172A" stroke-width="4"/>
  <!-- battery -->
  <line x1="160" y1="140" x2="160" y2="240" stroke="#0F172A" stroke-width="3"/>
  <line x1="175" y1="155" x2="175" y2="225" stroke="#0F172A" stroke-width="6"/>
  <!-- bulb -->
  <circle cx="320" cy="120" r="22" fill="#FEF08A" stroke="#CA8A04" stroke-width="3"/>
  <!-- switch -->
  <line x1="450" y1="120" x2="490" y2="95" stroke="#0F172A" stroke-width="3"/>
  <circle cx="450" cy="120" r="5" fill="#0F172A"/>
  <circle cx="500" cy="120" r="5" fill="#0F172A"/>
  {_label_marker(90, 180, "A", 160, 180)}
  {_label_marker(320, 60, "B", 320, 100)}
  {_label_marker(540, 80, "C", 480, 110)}
  {_label_marker(320, 300, "D", 320, 260)}
  <text x="40" y="340" font-size="12" font-family="Arial" fill="#334155">A = cell/battery · B = lamp/bulb · C = switch · D = connecting wire</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Labelled series circuit diagram",
        "attribution": "Atlas labelled diagram",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": {
            "A": "cell/battery",
            "B": "lamp/bulb",
            "C": "switch",
            "D": "connecting wire",
        },
        "key": "circuit",
    }


def flower_labelled() -> dict[str, Any]:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
  <rect width="640" height="420" fill="#F8FAFC"/>
  {_DEFS}
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Flower structure (labelled)</text>
  <ellipse cx="320" cy="160" rx="90" ry="50" fill="#FBCFE8" stroke="#BE185D" stroke-width="2"/>
  <ellipse cx="280" cy="140" rx="40" ry="55" fill="#F9A8D4" stroke="#BE185D" stroke-width="2"/>
  <ellipse cx="360" cy="140" rx="40" ry="55" fill="#F9A8D4" stroke="#BE185D" stroke-width="2"/>
  <circle cx="320" cy="150" r="14" fill="#FDE68A" stroke="#CA8A04" stroke-width="2"/>
  <line x1="320" y1="164" x2="320" y2="280" stroke="#166534" stroke-width="6"/>
  <ellipse cx="320" cy="300" rx="28" ry="22" fill="#86EFAC" stroke="#166534" stroke-width="2"/>
  {_label_marker(120, 120, "A", 250, 130)}
  {_label_marker(500, 140, "B", 330, 150)}
  {_label_marker(120, 300, "C", 300, 300)}
  {_label_marker(500, 260, "D", 320, 220)}
  <text x="40" y="380" font-size="12" font-family="Arial" fill="#334155">A = petal · B = anther/stamen · C = ovary · D = style/filament region</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Labelled flower structure diagram",
        "attribution": "Atlas labelled diagram",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": {
            "A": "petal",
            "B": "anther/stamen",
            "C": "ovary",
            "D": "style",
        },
        "key": "flower",
    }


def neuron_labelled() -> dict[str, Any]:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">
  <rect width="640" height="360" fill="#F8FAFC"/>
  {_DEFS}
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Neuron (labelled)</text>
  <circle cx="160" cy="180" r="40" fill="#C7D2FE" stroke="#3730A3" stroke-width="3"/>
  <line x1="200" y1="180" x2="420" y2="180" stroke="#1E3A8A" stroke-width="8"/>
  <line x1="120" y1="150" x2="80" y2="110" stroke="#1E3A8A" stroke-width="4"/>
  <line x1="120" y1="180" x2="70" y2="180" stroke="#1E3A8A" stroke-width="4"/>
  <line x1="120" y1="210" x2="80" y2="250" stroke="#1E3A8A" stroke-width="4"/>
  <line x1="420" y1="180" x2="460" y2="150" stroke="#1E3A8A" stroke-width="4"/>
  <line x1="420" y1="180" x2="470" y2="180" stroke="#1E3A8A" stroke-width="4"/>
  <line x1="420" y1="180" x2="460" y2="210" stroke="#1E3A8A" stroke-width="4"/>
  {_label_marker(60, 100, "A", 100, 130)}
  {_label_marker(160, 80, "B", 160, 145)}
  {_label_marker(320, 120, "C", 320, 175)}
  {_label_marker(520, 180, "D", 450, 180)}
  <text x="40" y="330" font-size="12" font-family="Arial" fill="#334155">A = dendrite · B = cell body · C = axon · D = axon terminal</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Labelled neuron diagram",
        "attribution": "Atlas labelled diagram",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": {
            "A": "dendrite",
            "B": "cell body",
            "C": "axon",
            "D": "axon terminal",
        },
        "key": "neuron",
    }


def plane_mirror_reflection() -> dict[str, Any]:
    """Plane mirror ray diagram — incident ray, normal, reflected ray."""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
  <rect width="640" height="420" fill="#F8FAFC"/>
  {_DEFS}
  <text x="320" y="30" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Reflection at a plane mirror</text>
  <line x1="320" y1="70" x2="320" y2="340" stroke="#64748B" stroke-width="10"/>
  <line x1="328" y1="70" x2="328" y2="340" stroke="#94A3B8" stroke-width="2" stroke-dasharray="4 4"/>
  <text x="360" y="60" font-size="13" font-family="Arial" fill="#475569">Plane mirror</text>
  <line x1="320" y1="200" x2="200" y2="200" stroke="#0F172A" stroke-width="2" stroke-dasharray="6 4"/>
  <line x1="80" y1="110" x2="320" y2="200" stroke="#DC2626" stroke-width="3" marker-end="url(#arrow)"/>
  <line x1="320" y1="200" x2="80" y2="290" stroke="#2563EB" stroke-width="3" marker-end="url(#arrow)"/>
  <path d="M280 200 A40 40 0 0 0 295 170" fill="none" stroke="#166534" stroke-width="2"/>
  <path d="M280 200 A40 40 0 0 1 295 230" fill="none" stroke="#166534" stroke-width="2"/>
  <text x="250" y="175" font-size="12" font-family="Arial" fill="#166534">i</text>
  <text x="250" y="235" font-size="12" font-family="Arial" fill="#166534">r</text>
  {_label_marker(100, 90, "A", 160, 130)}
  {_label_marker(140, 200, "B", 240, 200)}
  {_label_marker(100, 310, "C", 160, 270)}
  {_label_marker(400, 200, "D", 330, 200)}
  <text x="40" y="390" font-size="12" font-family="Arial" fill="#334155">A = incident ray · B = normal · C = reflected ray · D = plane mirror</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Labelled plane mirror reflection ray diagram showing incident ray, normal and reflected ray",
        "attribution": "Atlas labelled diagram",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": {
            "A": "incident ray",
            "B": "normal",
            "C": "reflected ray",
            "D": "plane mirror",
        },
        "key": "plane_mirror",
    }


def bar_chart_simple() -> dict[str, Any]:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400">
  <rect width="640" height="400" fill="#F8FAFC"/>
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Bar chart — pupils in clubs</text>
  <line x1="80" y1="340" x2="580" y2="340" stroke="#334155" stroke-width="2"/>
  <line x1="80" y1="340" x2="80" y2="60" stroke="#334155" stroke-width="2"/>
  <rect x="120" y="220" width="70" height="120" fill="#3B82F6"/>
  <rect x="230" y="140" width="70" height="200" fill="#10B981"/>
  <rect x="340" y="180" width="70" height="160" fill="#F59E0B"/>
  <rect x="450" y="100" width="70" height="240" fill="#EF4444"/>
  <text x="155" y="360" text-anchor="middle" font-size="13" font-family="Arial" fill="#334155">Drama</text>
  <text x="265" y="360" text-anchor="middle" font-size="13" font-family="Arial" fill="#334155">Science</text>
  <text x="375" y="360" text-anchor="middle" font-size="13" font-family="Arial" fill="#334155">Music</text>
  <text x="485" y="360" text-anchor="middle" font-size="13" font-family="Arial" fill="#334155">Sport</text>
  <text x="155" y="210" text-anchor="middle" font-size="12" font-family="Arial" fill="#0F172A">12</text>
  <text x="265" y="130" text-anchor="middle" font-size="12" font-family="Arial" fill="#0F172A">20</text>
  <text x="375" y="170" text-anchor="middle" font-size="12" font-family="Arial" fill="#0F172A">16</text>
  <text x="485" y="90" text-anchor="middle" font-size="12" font-family="Arial" fill="#0F172A">24</text>
  <text x="40" y="200" font-size="12" font-family="Arial" fill="#64748B" transform="rotate(-90 40 200)">Number of pupils</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Bar chart of pupils in Drama Science Music and Sport clubs",
        "attribution": "Atlas educational chart",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": None,
        "key": "bar_chart",
        "chart_data": {"Drama": 12, "Science": 20, "Music": 16, "Sport": 24},
    }


def pie_chart_simple() -> dict[str, Any]:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400">
  <rect width="640" height="400" fill="#F8FAFC"/>
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Pie chart — favourite subjects</text>
  <circle cx="280" cy="210" r="120" fill="#3B82F6"/>
  <path d="M280 210 L280 90 A120 120 0 0 1 383 265 Z" fill="#10B981"/>
  <path d="M280 210 L383 265 A120 120 0 0 1 200 310 Z" fill="#F59E0B"/>
  <path d="M280 210 L200 310 A120 120 0 0 1 280 90 Z" fill="#EF4444"/>
  <rect x="440" y="120" width="18" height="18" fill="#3B82F6"/><text x="468" y="134" font-size="13" font-family="Arial" fill="#334155">Maths 25%</text>
  <rect x="440" y="155" width="18" height="18" fill="#10B981"/><text x="468" y="169" font-size="13" font-family="Arial" fill="#334155">Science 35%</text>
  <rect x="440" y="190" width="18" height="18" fill="#F59E0B"/><text x="468" y="204" font-size="13" font-family="Arial" fill="#334155">English 20%</text>
  <rect x="440" y="225" width="18" height="18" fill="#EF4444"/><text x="468" y="239" font-size="13" font-family="Arial" fill="#334155">History 20%</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Pie chart of favourite subjects Maths Science English History",
        "attribution": "Atlas educational chart",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": None,
        "key": "pie_chart",
        "chart_data": {"Maths": 25, "Science": 35, "English": 20, "History": 20},
    }


def number_line_simple() -> dict[str, Any]:
    ticks = "".join(
        f'<line x1="{x}" y1="108" x2="{x}" y2="132" stroke="#1E3A8A" stroke-width="2"/>'
        f'<text x="{x}" y="160" text-anchor="middle" font-size="14" font-family="Arial" fill="#0F172A">{n}</text>'
        for n, x in zip(range(-3, 5), range(100, 540, 60))
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="640" height="220" viewBox="0 0 640 220">
  <rect width="640" height="220" fill="#F8FAFC"/>
  <text x="320" y="36" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Number line</text>
  <line x1="60" y1="120" x2="580" y2="120" stroke="#1E3A8A" stroke-width="3"/>
  <polygon points="580,120 560,110 560,130" fill="#1E3A8A"/>
  <polygon points="60,120 80,110 80,130" fill="#1E3A8A"/>
  {ticks}
  <circle cx="280" cy="120" r="8" fill="#DC2626"/>
  <text x="280" y="95" text-anchor="middle" font-size="13" font-family="Arial" fill="#DC2626">P</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Number line from -3 to 4 with point P at 0",
        "attribution": "Atlas educational chart",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": None,
        "key": "number_line",
    }


def linear_graph_simple() -> dict[str, Any]:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="640" height="400" viewBox="0 0 640 400">
  <rect width="640" height="400" fill="#F8FAFC"/>
  <text x="320" y="28" text-anchor="middle" font-size="18" font-family="Arial" font-weight="700" fill="#0F172A">Straight-line graph y = x + 1</text>
  <line x1="80" y1="320" x2="560" y2="320" stroke="#334155" stroke-width="2"/>
  <line x1="200" y1="60" x2="200" y2="340" stroke="#334155" stroke-width="2"/>
  <text x="550" y="345" font-size="13" font-family="Arial" fill="#334155">x</text>
  <text x="210" y="70" font-size="13" font-family="Arial" fill="#334155">y</text>
  <line x1="120" y1="280" x2="480" y2="100" stroke="#2563EB" stroke-width="3"/>
  <circle cx="200" cy="240" r="5" fill="#DC2626"/>
  <circle cx="280" cy="200" r="5" fill="#DC2626"/>
  <circle cx="360" cy="160" r="5" fill="#DC2626"/>
  <text x="40" y="380" font-size="12" font-family="Arial" fill="#475569">Points shown on the line: (0,1), (2,3), (4,5)</text>
</svg>"""
    return {
        "url": _data_uri(svg),
        "alt": "Linear graph of y equals x plus 1 on a coordinate plane",
        "attribution": "Atlas educational chart",
        "source": "atlas_svg",
        "license": "Atlas",
        "labels": None,
        "key": "linear_graph",
    }


_CATALOG = {
    "plant_cell": plant_cell_labelled,
    "animal_cell": animal_cell_labelled,
    "heart": heart_labelled,
    "circuit": circuit_labelled,
    "flower": flower_labelled,
    "neuron": neuron_labelled,
    "plane_mirror": plane_mirror_reflection,
    "bar_chart": bar_chart_simple,
    "pie_chart": pie_chart_simple,
    "number_line": number_line_simple,
    "linear_graph": linear_graph_simple,
}


_TOPIC_HINTS = [
    (("plant cell", "cell wall", "chloroplast", "vacuole"), "plant_cell"),
    (("animal cell", "mitochondrion", "cytoplasm"), "animal_cell"),
    (("heart", "atrium", "ventricle", "circulatory"), "heart"),
    (("circuit", "resistor", "battery", "bulb", "switch", "lamp"), "circuit"),
    (("flower", "petal", "ovary", "anther", "stamen", "pollination"), "flower"),
    (("neuron", "axon", "dendrite", "nervous"), "neuron"),
    (
        (
            "plane mirror",
            "reflection of light",
            "incident ray",
            "reflected ray",
            "angle of incidence",
            "ray diagram",
            "mirror ray",
        ),
        "plane_mirror",
    ),
    (("bar chart", "bar graph", "simple bar"), "bar_chart"),
    (("pie chart", "pie graph"), "pie_chart"),
    (("number line",), "number_line"),
    (("linear graph", "straight-line graph", "coordinate plane", "y = x"), "linear_graph"),
]


def pick_labelled_diagram(topic_text: str = "", subject: str = "") -> dict[str, Any] | None:
    """Return a matching Atlas diagram when topic text strongly matches a known figure."""
    blob = f"{subject} {topic_text}".lower()
    for keys, name in _TOPIC_HINTS:
        if any(k in blob for k in keys):
            return _CATALOG[name]()
    return None


def labelled_diagram_by_key(key: str) -> dict[str, Any] | None:
    fn = _CATALOG.get(key)
    return fn() if fn else None


def labels_legend_text(image: dict[str, Any]) -> str:
    labels = image.get("labels") or {}
    if not isinstance(labels, dict) or not labels:
        return ""
    parts = [f"{k} = {v}" for k, v in labels.items()]
    return "Labels on the diagram: " + " · ".join(parts)
