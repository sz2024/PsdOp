# -*- coding: utf-8 -*-
import argparse
import os
import re
from typing import Iterable

from psd_tools import PSDImage
try:
    # Helpful for reliably detecting text layers
    from psd_tools.api.layers import TextLayer  # type: ignore
except Exception:  # pragma: no cover - optional import fallback
    TextLayer = None


def sanitize_filename(name: str) -> str:
    name = name.strip() or "layer"
    # Replace invalid filename chars on Windows
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    # Collapse spaces
    name = re.sub(r"\s+", " ", name)
    return name[:128]


def is_locked(layer) -> bool:
    # Consider both Tagged Block PROTECTED_SETTING (lspf) and layer flags
    # Any protection (transparency/composite/position) treated as locked
    try:
        # 1) Tagged block lspf
        blocks = getattr(layer, "tagged_blocks", None)
        if blocks:
            protected = blocks.get_data(b"lspf")  # Tag.PROTECTED_SETTING
            if protected is not None:
                value = getattr(protected, "value", 0)
                if bool(value):
                    return True
        # 2) Layer flags: transparency_protected
        record = getattr(layer, "_record", None)
        flags = getattr(record, "flags", None)
        if flags and getattr(flags, "transparency_protected", False):
            return True
    except Exception:
        pass
    return False


def is_text_layer(layer) -> bool:
    """Return True if the layer is a text (font) layer."""
    try:
        if TextLayer is not None and isinstance(layer, TextLayer):
            return True
        kind = getattr(layer, "kind", None)
        if kind == "type":
            return True
        # Fallback: presence of TySh tagged block indicates text engine data
        blocks = getattr(layer, "tagged_blocks", None)
        if blocks and getattr(blocks, "get_data", None):
            if blocks.get_data(b"TySh") is not None:
                return True
    except Exception:
        pass
    return False


def iter_layers(root) -> Iterable:
    for layer in root:
        yield layer
        if getattr(layer, "is_group", None) and layer.is_group():
            for child in iter_layers(layer):
                yield child


def export_layer_png(layer, out_dir: str, include_invisible: bool) -> bool:
    if not include_invisible and not layer.is_visible():
        return False
    if layer.is_group():
        return False
    if is_locked(layer):
        return False
    if is_text_layer(layer):
        return False
    # Render layer to PIL; skip if no pixels
    image = layer.composite()
    if image is None:
        return False
    if image.width == 0 or image.height == 0:
        return False

    # Filename: keep exactly the layer name (sanitized), no extra suffix
    base = sanitize_filename(layer.name or "layer")
    filename = f"{base}.png"
    path = os.path.join(out_dir, filename)
    # Ensure directory exists
    os.makedirs(out_dir, exist_ok=True)
    image.save(path, format="PNG")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Export all non-locked layers in a PSD as PNG files"
    )
    parser.add_argument("psd", help="Path to the PSD file, e.g. continue.psd")
    parser.add_argument(
        "--out-dir",
        dest="out_dir",
        default=os.path.join("layout", "png"),
        help="Output directory (will be created if missing). Default: ./layout/png",
    )
    parser.add_argument(
        "--include-hidden",
        dest="include_hidden",
        action="store_true",
        help="Include hidden layers",
    )

    args = parser.parse_args()
    psd_path = args.psd
    out_dir = args.out_dir

    if not os.path.isfile(psd_path):
        raise SystemExit(f"PSD file not found: {psd_path}")

    psd = PSDImage.open(psd_path)
    total = 0
    exported = 0
    for layer in iter_layers(psd):
        total += 1
        if export_layer_png(layer, out_dir, include_invisible=args.include_hidden):
            exported += 1

    print(f"Exported {exported} PNGs out of {total} layers to {out_dir}")


if __name__ == "__main__":
    main()


