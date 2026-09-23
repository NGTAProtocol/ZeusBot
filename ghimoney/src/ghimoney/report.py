"""JSON and Markdown report rendering. Both are pure functions of the report dict."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ghimoney.canonical import canonical_json


def _fmt(value: Any, digits: int = 1) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def _pct(value: float | None) -> str:
    return "—" if value is None else f"{value * 100:.0f}%"


def render_json(report: dict[str, Any]) -> str:
    return canonical_json(report, indent=2) + "\n"


def render_markdown(r: dict[str, Any]) -> str:
    p, meth, src = r["project"], r["methodology"], r["source"]
    imp, cov, conf, risk = r["impact"], r["coverage"], r["confidence"], r["risk"]
    out: list[str] = []
    w = out.append

    w(f"# GHIMONEY Impact Report: {p['full_name']}")
    w("")
    if src["synthetic"]:
        w("> **SYNTHETIC DATA.** This report was computed from a synthetic test snapshot, "
          "not from a real repository.")
        w("")
    w("> Provisional result of methodology "
      f"`{meth['methodology_version']}`. Weights and anchors are hypotheses. "
      "No human review was performed and this result is not used for funding.")
    w("")
    w("## Summary")
    w("")
    w("| Output | Value |")
    w("|---|---|")
    if imp["status"] == "SCORED":
        impact_text = f"**{_fmt(imp['score'])} / 100**"
        if imp["weights_renormalized"]:
            impact_text += " (weights recalculated, see below)"
    else:
        impact_text = "**INSUFFICIENT_EVIDENCE**: no final Impact Score"
    w(f"| Impact | {impact_text} |")
    w(f"| Evidence Coverage | {_pct(cov['value'])} |")
    w(f"| Confidence | {_pct(conf['adjusted'])} (base {_pct(conf['base'])}, "
      f"risk factor {conf['risk_adjustment_factor']:.2f}) |")
    w(f"| Risk | {risk['level']} ({len(risk['signals'])} signal(s)) |")
    w("")
    w("Impact, Coverage, Confidence and Risk are independent outputs: Coverage, Confidence "
      "and Risk never change the Impact Score.")
    w("")

    if imp["reasons"]:
        w("### Why there is no Impact Score")
        w("")
        for reason in imp["reasons"]:
            w(f"- {reason}")
        w("")

    w("## Dimensions")
    w("")
    w("| Dimension | Weight | Effective weight | Status | Score | Metric coverage | Confidence |")
    w("|---|---|---|---|---|---|---|")
    for d in r["dimensions"]:
        eff = imp["effective_weights"].get(d["dimension"])
        w(f"| {d['dimension']} | {_pct(d['weight'])} | {_pct(eff)} | {d['availability']} | "
          f"{_fmt(d['score'])} | {_pct(d['metric_coverage'])} | {_pct(d['confidence'])} |")
    w("")
    if imp["missing_dimensions"]:
        w(f"Missing dimensions: {', '.join(imp['missing_dimensions'])}. "
          "Missing dimensions are not counted as zero.")
        w("")

    w("## Risk")
    w("")
    if risk["signals"]:
        for s in risk["signals"]:
            observed = ", ".join(f"{k}={v}" for k, v in sorted(s["observed"].items()))
            w(f"- **{s['level']}**, `{s['signal_id']}`: {s['description']} ({observed})")
    else:
        w("No risk signal triggered.")
    w("")
    w("A risk signal is an anomaly to be reviewed, not evidence of fraud.")
    if risk["checks_not_evaluated"]:
        w(f"Checks not evaluated for lack of data: {', '.join(risk['checks_not_evaluated'])}.")
    w("")

    w("## Evidence")
    w("")
    w("| Metric | Availability | Raw value | Normalized | Method | Confidence | Note |")
    w("|---|---|---|---|---|---|---|")
    for e in r["evidence"]:
        w(f"| {e['metric']} | {e['availability']} | {_fmt(e['raw_value'], 2)} | "
          f"{_fmt(e['normalized_value'])} | {e['method']} | {_pct(e['confidence'])} | "
          f"{e['note'] or ''} |")
    w("")

    w("## Reproducibility")
    w("")
    w(f"- Project ID: `{p['project_id']}` (GitHub repository id {p['forge_repo_id']})")
    w(f"- Methodology: `{meth['methodology_version']}`, config `{meth['config_version']}`, "
      f"hash `{meth['config_hash']}`")
    w(f"- Snapshot: `{src['snapshot_id']}` as of {src['as_of']}, hash `{src['snapshot_hash']}`")
    w(f"- Sources: {', '.join(f'{k} ({v})' for k, v in src['source_versions'].items())}")
    w(f"- Report hash: `{r['report_hash']}`")
    w("")
    w("Same snapshot + same methodology + same configuration produce the same report.")
    w("")
    return "\n".join(out)


def write_reports(report: dict[str, Any], out_dir: Path | str) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path, md_path = out / "report.json", out / "report.md"
    json_path.write_text(render_json(report), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path
