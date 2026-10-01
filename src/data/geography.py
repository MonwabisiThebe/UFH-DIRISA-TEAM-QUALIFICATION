"""Eastern Cape municipal boundaries for the 33-unit analytical geography.

Source: Municipal Demarcation Board 2011 local-municipality boundaries, as
redistributed in TopoJSON form by github.com/datawizzards/zadmaps
(``geojson/za-local.topojson``). The 2011 layer has 39 Eastern Cape units.
We dissolve them into 33 units with the SAME crosswalk used for the election
data (``src.config.CODE_MAP``), so the map and the data share one geography.

Limitation: the 2016 re-determination also made small boundary realignments
that are not merger-driven. They are not represented here; the map is for
visual communication, not area calculations.
"""
from __future__ import annotations

import json

from src.config import CODE_MAP, GEOJSON, RAW_TOPOJSON, TARGET_CODES


def _decode_topojson(topo: dict, object_name: str = "layer1"):
    sx, sy = topo["transform"]["scale"]
    tx, ty = topo["transform"]["translate"]
    arcs = []
    for a in topo["arcs"]:  # arcs are delta-encoded integers
        x = y = 0
        pts = []
        for dx, dy in a:
            x += dx
            y += dy
            pts.append((x * sx + tx, y * sy + ty))
        arcs.append(pts)

    def arc(i):
        return arcs[i] if i >= 0 else arcs[~i][::-1]

    def ring(idx):
        pts = []
        for i in idx:
            a = arc(i)
            pts.extend(a if not pts else a[1:])
        return pts

    for g in topo["objects"][object_name]["geometries"]:
        if g["type"] == "Polygon":
            geom = {"type": "Polygon", "coordinates": [ring(r) for r in g["arcs"]]}
        elif g["type"] == "MultiPolygon":
            geom = {"type": "MultiPolygon", "coordinates": [[ring(r) for r in p] for p in g["arcs"]]}
        else:
            continue
        yield g["properties"], geom


def build_geojson(src=RAW_TOPOJSON, dst=GEOJSON, tolerance: float = 0.004) -> dict:
    """Dissolve MDB 2011 Eastern Cape units into the 33 analytical units."""
    from shapely.geometry import MultiPolygon, Polygon, mapping, shape
    from shapely.geometry.polygon import orient
    from shapely.ops import unary_union

    topo = json.loads(open(src, encoding="utf-8").read())
    parts: dict[str, list] = {}
    sources: dict[str, list] = {}
    for props, geom in _decode_topojson(topo):
        if props.get("PROVINCE") != "EC":
            continue
        code = CODE_MAP.get(props["CAT_B"], props["CAT_B"])
        parts.setdefault(code, []).append(shape(geom).buffer(0))
        sources.setdefault(code, []).append(props["CAT_B"])

    features = []
    for code in sorted(parts):
        merged = unary_union(parts[code]).simplify(tolerance, preserve_topology=True)
        # Plotly (d3-geo) needs CLOCKWISE exterior rings; otherwise a polygon is read as
        # "everything except this shape" and the map renders blank. Matplotlib ignores order.
        if isinstance(merged, Polygon):
            merged = orient(merged, sign=-1.0)
        else:
            merged = MultiPolygon([orient(g, sign=-1.0) for g in merged.geoms])
        features.append({"type": "Feature", "id": code,
                         "properties": {"MuniCode": code, "SourceUnits": ",".join(sorted(sources[code]))},
                         "geometry": mapping(merged)})
    fc = {"type": "FeatureCollection", "features": features}
    assert {f["id"] for f in features} == TARGET_CODES, "Map units must equal the 33 analytical codes"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(fc, separators=(",", ":")), encoding="utf-8")
    return fc


def load_geojson(path=GEOJSON) -> dict:
    """Load the 33-unit GeoJSON, building it from the raw TopoJSON if needed."""
    if not path.exists():
        return build_geojson(dst=path)
    return json.loads(path.read_text(encoding="utf-8"))
