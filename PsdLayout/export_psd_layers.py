# -*- coding: utf-8 -*-
import argparse
import json
import os
from typing import List, Dict

from psd_tools import PSDImage
try:
    # Optional import: available in psd-tools >= 1.9
    from psd_tools.api.layers import TextLayer  # type: ignore
except Exception:  # pragma: no cover - optional import fallback
    TextLayer = None


def is_locked(layer) -> bool:
    """Return True if the layer is locked (any protection bit)."""
    try:
        blocks = getattr(layer, "tagged_blocks", None)
        if blocks:
            protected = blocks.get_data(b"lspf")  # PROTECTED_SETTING
            if protected is not None:
                value = getattr(protected, "value", 0)
                if bool(value):
                    return True
        record = getattr(layer, "_record", None)
        flags = getattr(record, "flags", None)
        if flags and getattr(flags, "transparency_protected", False):
            return True
    except Exception:
        pass
    return False


def compute_bbox_dict(bbox, use_center: bool = False) -> Dict[str, int]:
    # psd-tools may return a BBox object or a 4-tuple (left, top, right, bottom)
    if hasattr(bbox, "left") and hasattr(bbox, "top") and hasattr(bbox, "right") and hasattr(bbox, "bottom"):
        left = int(bbox.left)
        top = int(bbox.top)
        right = int(bbox.right)
        bottom = int(bbox.bottom)
    else:
        left, top, right, bottom = [int(v) for v in bbox]
    width = max(0, int(right - left))
    height = max(0, int(bottom - top))
    if use_center:
        center_x = int(round(left + width / 2.0))
        center_y = int(round(top + height / 2.0))
        x_value, y_value = center_x, center_y
    else:
        x_value, y_value = left, top
    return {
        "x": x_value,
        "y": y_value,
        "width": width,
        "height": height,
    }


def collect_layers(layers, include_hidden: bool, use_center: bool, parent_path: List[str], results: List[Dict]):
    for layer in layers:
        # Group layers contain children
        if getattr(layer, "is_group", None) and layer.is_group():
            child_parent_path = parent_path + [layer.name or ""]
            collect_layers(layer, include_hidden, use_center, child_parent_path, results)
            continue

        # Skip hidden layers unless requested
        if not include_hidden and not layer.is_visible():
            continue

        # Skip locked layers (any protection)
        if is_locked(layer):
            continue

        # Skip text (font) layers; only export image layers
        try:
            if TextLayer is not None and isinstance(layer, TextLayer):
                continue
            kind = getattr(layer, "kind", None)
            if kind == "type":
                continue
            blocks = getattr(layer, "tagged_blocks", None)
            if blocks and getattr(blocks, "get_data", None):
                if blocks.get_data(b"TySh") is not None:
                    continue
        except Exception:
            continue

        bbox = getattr(layer, "bbox", None)
        if bbox is None:
            continue

        bbox_dict = compute_bbox_dict(bbox, use_center=use_center)
        if bbox_dict["width"] == 0 or bbox_dict["height"] == 0:
            # Skip empty layers with no area
            continue

        # Name in JSON remains exactly the layer name (no suffix/extension)
        layer_name = layer.name or ""
        full_path = "/".join(parent_path + [layer_name]) if parent_path or layer_name else layer_name

        results.append(
            {
                "name": layer_name,
                "path": full_path,
                **bbox_dict,
            }
        )


def export_layers(psd_path: str, out_path: str, include_hidden: bool = False, use_center: bool = False) -> List[Dict]:
    psd = PSDImage.open(psd_path)
    results: List[Dict] = []
    collect_layers(psd, include_hidden, use_center, [], results)
    # Write JSON
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Export PSD layer names and coordinates to JSON"
    )
    parser.add_argument("psd", help="Path to the PSD file, e.g. continue.psd")
    parser.add_argument(
        "--out",
        dest="out",
        help="Output JSON file path. Defaults to <psd_basename>_layers.json",
    )
    parser.add_argument(
        "--include-hidden",
        dest="include_hidden",
        action="store_true",
        help="Include hidden layers in the output",
    )
    parser.add_argument(
        "--center",
        dest="center",
        action="store_true",
        help="Output x,y as the center of the layer instead of top-left",
    )

    args = parser.parse_args()
    psd_path = args.psd
    if not os.path.isfile(psd_path):
        raise SystemExit(f"PSD file not found: {psd_path}")

    base_name = os.path.splitext(os.path.basename(psd_path))[0]
    default_dir = os.path.join("layout")
    os.makedirs(default_dir, exist_ok=True)
    out_path = args.out or os.path.join(default_dir, f"{base_name}_layers.json")

    results = export_layers(psd_path, out_path, include_hidden=args.include_hidden, use_center=args.center)
    print(f"Exported {len(results)} layers to {out_path}")


if __name__ == "__main__":
    main()


