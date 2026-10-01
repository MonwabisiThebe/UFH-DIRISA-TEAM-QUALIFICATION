"""Consistent figure style for notebooks and slides, plus a static map helper."""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from src.config import ALOE, FIGURES, GREY, INK, MIST, PARTY_COLORS, TEAL, TEAL_LIGHT

SEQ_CMAP = mpl.colors.LinearSegmentedColormap.from_list("ec_seq", ["#F1F5F3", TEAL_LIGHT, TEAL, "#08302E"])
DIV_CMAP = mpl.colors.LinearSegmentedColormap.from_list("ec_div", [ALOE, "#F3D9CC", "#F7F7F7", "#CFE3DF", TEAL])


def apply_style():
    """Matplotlib defaults: quiet frame, readable type, project colours."""
    mpl.rcParams.update({
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
        "font.family": "DejaVu Sans", "font.size": 10.5,
        "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
        "axes.labelsize": 10.5, "axes.labelcolor": INK, "axes.edgecolor": "#B8C4C2",
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#E3E9E8", "grid.linewidth": 0.8,
        "axes.prop_cycle": mpl.cycler(color=[TEAL, ALOE, "#4C6A92", "#A3B18A", "#6C4F9E", GREY]),
        "xtick.color": INK, "ytick.color": INK, "text.color": INK,
        "legend.frameon": False, "figure.facecolor": "white",
    })


def subtitle(ax, text, y=1.01):
    """Small explanatory line under the title (the 'so what' of the chart)."""
    ax.text(0, y, text, transform=ax.transAxes, fontsize=9.5, color="#4A5A5E", va="bottom")


def source_note(fig, text="Source: IEC LGE detailed results 2000-2021; team analysis."):
    fig.text(0.01, -0.02, text, fontsize=8, color="#6B7B7E", ha="left", va="top")


def save(fig, name: str, folder: str):
    out = FIGURES / folder
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png", facecolor="white")
    return out / f"{name}.png"


def choropleth(ax, geo: dict, values: dict, cmap=SEQ_CMAP, vmin=None, vmax=None,
               label_codes=(), edge="white", missing="#DDDDDD"):
    """Draw a filled map of the 33 municipalities from a GeoJSON dict."""
    from shapely.geometry import shape

    vals = np.array([v for v in values.values() if v is not None and np.isfinite(v)])
    vmin = vals.min() if vmin is None else vmin
    vmax = vals.max() if vmax is None else vmax
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    for f in geo["features"]:
        geom = shape(f["geometry"])
        v = values.get(f["id"])
        color = missing if v is None or not np.isfinite(v) else cmap(norm(v))
        polys = [geom] if geom.geom_type == "Polygon" else list(geom.geoms)
        for poly in polys:
            x, y = poly.exterior.xy
            ax.fill(x, y, color=color, ec=edge, lw=0.6)
        if f["id"] in label_codes:
            c = geom.representative_point()
            ax.annotate(f["id"], (c.x, c.y), fontsize=7, ha="center", va="center", color=INK,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.75))
    ax.set_aspect("equal")
    ax.axis("off")
    return mpl.cm.ScalarMappable(norm=norm, cmap=cmap)


def map_colorbar(fig, ax, mappable, label: str):
    """Compact horizontal colour bar under a map panel."""
    cb = fig.colorbar(mappable, ax=ax, orientation="horizontal", shrink=0.55, pad=0.01, aspect=30)
    cb.set_label(label, fontsize=9)
    cb.outline.set_visible(False)
    return cb


def party_color(p: str) -> str:
    return PARTY_COLORS.get(p, GREY)


__all__ = ["apply_style", "subtitle", "source_note", "save", "choropleth", "map_colorbar", "party_color",
           "SEQ_CMAP", "DIV_CMAP", "MIST"]
