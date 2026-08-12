"""Rebuild the tracked UF × EW panel from a local SINAN extract."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from arboviruses_series_forecasting.data.epidemiological.pipeline import (
    build_dengue_uf_ew_series,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def load_config(config_path: Path) -> dict:
    with config_path.open() as f:
        return yaml.safe_load(f)


def build_panel_from_config(
    *,
    config_path: Path | None = None,
    sinan_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    root = repo_root()
    config_path = config_path or (root / "config.yml")
    config = load_config(config_path)

    sinan_path = sinan_path or (root / config["data"]["sinan"]["path"])
    output_path = output_path or (
        root / config["paths"]["processed"] / "dengue_uf_ew.parquet"
    )
    if not sinan_path.is_file():
        raise FileNotFoundError(
            f"SINAN extract not found at {sinan_path}. "
            "Place the snapshot there (gitignored) or pass --sinan."
        )

    aggregation = config["aggregation"]
    panel = build_dengue_uf_ew_series(
        sinan_path,
        window_start=aggregation["window"]["start"],
        right_censor_weeks=int(aggregation["right_censor_weeks"]),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    return output_path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build data/processed/dengue_uf_ew.parquet from the SINAN extract."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to config.yml (default: repo root)",
    )
    parser.add_argument(
        "--sinan",
        type=Path,
        default=None,
        help="Override path to SINAN parquet extract",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Override output parquet path",
    )
    args = parser.parse_args(argv)
    path = build_panel_from_config(
        config_path=args.config,
        sinan_path=args.sinan,
        output_path=args.output,
    )
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
