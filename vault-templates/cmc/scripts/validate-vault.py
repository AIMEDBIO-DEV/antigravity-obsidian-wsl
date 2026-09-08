#!/usr/bin/env python3
"""Validate OKF v0.2 hard conformance and AIMEDBIO vault rules."""

from __future__ import annotations

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print(
        "ERROR: PyYAML is required. Install it with "
        "'python3 -m pip install -r scripts/requirements.txt'.",
        file=sys.stderr,
    )
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "config" / "vault-schema.yaml"
FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ACTOR_RE = re.compile(r"^(?:human:[^\s]+|process:[^\s]+|[^/\s]+/[^/\s]+)$")
WIKILINK_RE = re.compile(r"\[\[([^\]|#\n]+)")
NESTED_WIKILINK_RE = re.compile(r"\[\[[^\]\n]*\[\[[^\n]*")


def load_yaml_mapping(raw: str, label: str, errors: list[str]) -> dict[str, Any] | None:
    try:
        value = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        summary = str(exc).splitlines()[0]
        errors.append(f"{label}: YAML 파싱 실패 — {summary}")
        return None
    if not isinstance(value, dict):
        errors.append(f"{label}: frontmatter는 YAML mapping이어야 함")
        return None
    return value


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_iso_date(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if isinstance(value, date):
        return True
    if not isinstance(value, str) or not DATE_RE.fullmatch(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def is_iso_datetime(value: Any) -> bool:
    if isinstance(value, datetime):
        return True
    if not isinstance(value, str) or "T" not in value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def validate_actor(value: Any, field: str, label: str, errors: list[str]) -> None:
    if not is_nonempty_string(value) or not ACTOR_RE.fullmatch(value):
        errors.append(
            f"{label}: {field} actor 형식 오류 — human:<id>, process:<id>, "
            "또는 <producer>/<version> 사용"
        )


def validate_usage_window(value: Any, field: str, label: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{label}: {field}는 from/to YAML mapping이어야 함")
        return
    for key in ("from", "to"):
        if key not in value or not is_iso_date(value[key]):
            errors.append(f"{label}: {field}.{key}는 YYYY-MM-DD 날짜여야 함")


def validate_okf_v02_fields(
    data: dict[str, Any], body: str, label: str, errors: list[str], warnings: list[str]
) -> None:
    if "timestamp" in data:
        warnings.append(f"{label}: legacy timestamp 사용 — generated.at으로 이전 권장")
    if re.search(r"(?m)^# Citations\s*$", body):
        warnings.append(f"{label}: legacy # Citations 사용 — sources로 이전 권장")

    if "generated" in data:
        generated = data["generated"]
        if not isinstance(generated, dict):
            errors.append(f"{label}: generated는 by/at YAML mapping이어야 함")
        else:
            validate_actor(generated.get("by"), "generated.by", label, errors)
            if "at" in generated and not is_iso_datetime(generated["at"]):
                errors.append(f"{label}: generated.at은 ISO 8601 datetime이어야 함")

    if "verified" in data:
        verified = data["verified"]
        events = verified if isinstance(verified, list) else [verified]
        if not events:
            errors.append(f"{label}: verified는 비어 있지 않은 mapping 또는 list여야 함")
        for index, event in enumerate(events):
            field = f"verified[{index}]"
            if not isinstance(event, dict):
                errors.append(f"{label}: {field}는 by/at YAML mapping이어야 함")
                continue
            validate_actor(event.get("by"), f"{field}.by", label, errors)
            if "at" not in event or not is_iso_datetime(event["at"]):
                errors.append(f"{label}: {field}.at은 ISO 8601 datetime이어야 함")

    if "sources" in data:
        sources = data["sources"]
        if not isinstance(sources, list):
            errors.append(f"{label}: sources는 YAML list여야 함")
        else:
            seen_ids: set[str] = set()
            for index, source in enumerate(sources):
                field = f"sources[{index}]"
                if not isinstance(source, dict):
                    errors.append(f"{label}: {field}는 YAML mapping이어야 함")
                    continue
                if not is_nonempty_string(source.get("resource")):
                    errors.append(f"{label}: {field}.resource 누락 또는 빈 값")
                source_id = source.get("id")
                if source_id is not None:
                    if not is_nonempty_string(source_id):
                        errors.append(f"{label}: {field}.id는 비어 있지 않은 문자열이어야 함")
                    elif source_id in seen_ids:
                        errors.append(f"{label}: 중복 source id — {source_id}")
                    else:
                        seen_ids.add(source_id)
                if "usage_count" in source and (
                    not isinstance(source["usage_count"], int)
                    or isinstance(source["usage_count"], bool)
                    or source["usage_count"] < 0
                ):
                    errors.append(f"{label}: {field}.usage_count는 0 이상의 정수여야 함")
                if "last_modified" in source and not is_iso_date(source["last_modified"]):
                    errors.append(f"{label}: {field}.last_modified는 YYYY-MM-DD여야 함")
                if "usage_window" in source:
                    validate_usage_window(
                        source["usage_window"], f"{field}.usage_window", label, errors
                    )

    if "usage_window" in data:
        validate_usage_window(data["usage_window"], "usage_window", label, errors)
    if "stale_after" in data and not is_iso_date(data["stale_after"]):
        errors.append(f"{label}: stale_after는 YYYY-MM-DD여야 함")

    if data.get("type") == "Attested Computation":
        if not is_nonempty_string(data.get("runtime")):
            errors.append(f"{label}: Attested Computation에는 runtime이 필수")
        if "parameters" in data:
            parameters = data["parameters"]
            if not isinstance(parameters, list):
                errors.append(f"{label}: parameters는 YAML list여야 함")
            else:
                for index, parameter in enumerate(parameters):
                    field = f"parameters[{index}]"
                    if not isinstance(parameter, dict):
                        errors.append(f"{label}: {field}는 YAML mapping이어야 함")
                        continue
                    if not is_nonempty_string(parameter.get("name")):
                        errors.append(f"{label}: {field}.name 누락 또는 빈 값")
                    if not is_nonempty_string(parameter.get("type")):
                        errors.append(f"{label}: {field}.type 누락 또는 빈 값")
                    if not isinstance(parameter.get("required"), bool):
                        errors.append(f"{label}: {field}.required는 boolean이어야 함")
        has_external_computation = is_nonempty_string(data.get("computation"))
        has_inline_computation = bool(re.search(r"(?m)^# Computation\s*$", body))
        if has_external_computation == has_inline_computation:
            errors.append(
                f"{label}: computation 경로 또는 # Computation 본문 중 정확히 하나를 사용"
            )


def validate_index(
    path: Path,
    relative: Path,
    text: str,
    schema: dict[str, Any],
    errors: list[str],
) -> None:
    label = relative.as_posix()
    match = FRONTMATTER_RE.match(text)
    body = text
    if match:
        if len(relative.parts) != 1:
            errors.append(f"{label}: 하위 index.md에는 frontmatter 사용 금지")
        data = load_yaml_mapping(match.group(1), label, errors)
        body = text[match.end() :]
        if data is not None:
            extra = set(data) - {"okf_version"}
            if extra:
                errors.append(
                    f"{label}: root index frontmatter에는 okf_version만 허용 — "
                    + ", ".join(sorted(extra))
                )
            if data.get("okf_version") != schema["okf_version"]:
                errors.append(
                    f"{label}: okf_version은 문자열 '{schema['okf_version']}'이어야 함"
                )
    elif len(relative.parts) == 1:
        errors.append(f"{label}: root index.md에 okf_version 선언 누락")

    if not re.search(r"(?m)^#\s+\S", body):
        errors.append(f"{label}: index.md에 section heading이 필요")
    if not re.search(r"(?m)^\s*[*+-]\s+\[[^\]]+\]\([^)]+\)", body):
        errors.append(f"{label}: index.md에 표준 Markdown listing link가 필요")


def validate_log(relative: Path, text: str, errors: list[str]) -> None:
    label = relative.as_posix()
    if FRONTMATTER_RE.match(text):
        errors.append(f"{label}: log.md에는 frontmatter 사용 금지")
    if not re.search(r"(?m)^#\s+\S", text):
        errors.append(f"{label}: log.md에 title heading이 필요")
    headings = re.findall(r"(?m)^##\s+(.+?)\s*$", text)
    if not headings:
        errors.append(f"{label}: log.md에 YYYY-MM-DD date heading이 필요")
        return
    parsed_dates: list[date] = []
    for heading in headings:
        if not is_iso_date(heading):
            errors.append(f"{label}: log date heading은 YYYY-MM-DD 형식이어야 함 — {heading}")
        else:
            parsed_dates.append(date.fromisoformat(str(heading)))
    if parsed_dates != sorted(parsed_dates, reverse=True):
        errors.append(f"{label}: log date heading은 최신순이어야 함")


def validate_templater_setup(schema: dict[str, Any], errors: list[str]) -> None:
    config_dir = ROOT / ".obsidian"
    plugin_dir = config_dir / "plugins" / "templater-obsidian"
    try:
        community = json.loads((config_dir / "community-plugins.json").read_text())
        core = json.loads((config_dir / "core-plugins.json").read_text())
        manifest = json.loads((plugin_dir / "manifest.json").read_text())
        settings = json.loads((plugin_dir / "data.json").read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Templater 설정 또는 설치 파일을 읽을 수 없음 — {exc}")
        return

    if "templater-obsidian" not in community:
        errors.append(".obsidian/community-plugins.json: Templater가 활성화되지 않음")
    if core.get("templates") is not False:
        errors.append(".obsidian/core-plugins.json: 중복 방지를 위해 core Templates를 꺼야 함")
    if manifest.get("id") != "templater-obsidian" or not manifest.get("version"):
        errors.append("Templater manifest id/version 오류")
    for asset in ("main.js", "manifest.json", "styles.css"):
        if not (plugin_dir / asset).is_file():
            errors.append(f"Templater release asset 누락 — {asset}")
    if settings.get("templates_folder") != "Templates":
        errors.append("Templater templates_folder는 Templates여야 함")
    if settings.get("trigger_on_file_creation_mode") != "folder":
        errors.append("Templater trigger mode는 folder mapping이어야 함")
    if settings.get("shell_path") or settings.get("user_scripts_folder"):
        errors.append("Templater system command/user script 경로는 비워 두어야 함")
    if settings.get("startup_templates"):
        errors.append("Templater startup templates는 사용하지 않음")

    pairs = settings.get("folder_templates")
    if not isinstance(pairs, list):
        errors.append("Templater folder_templates는 list여야 함")
        return
    mapped_folders = {
        pair.get("folder") for pair in pairs if isinstance(pair, dict)
    }
    expected_folders = set(schema.get("note_folders", {}))
    if mapped_folders != expected_folders:
        errors.append(
            "Templater folder mapping과 schema note_folders 불일치 — "
            f"missing={sorted(expected_folders - mapped_folders)}, "
            f"extra={sorted(mapped_folders - expected_folders)}"
        )
    for pair in pairs:
        if not isinstance(pair, dict):
            errors.append("Templater folder template entry는 mapping이어야 함")
            continue
        folder = pair.get("folder")
        template = pair.get("template")
        if not is_nonempty_string(folder) or not (ROOT / str(folder)).is_dir():
            errors.append(f"Templater folder mapping 대상 누락 — {folder}")
        template_path = ROOT / str(template)
        if not is_nonempty_string(template) or not template_path.is_file():
            errors.append(f"Templater template file 누락 — {template}")
            continue
        text = template_path.read_text(encoding="utf-8-sig")
        match = FRONTMATTER_RE.match(text)
        if not match:
            errors.append(f"{template}: template frontmatter 누락")
            continue
        data = load_yaml_mapping(match.group(1), str(template), errors)
        if data is not None and not is_nonempty_string(data.get("type")):
            errors.append(f"{template}: non-empty type 누락")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        print(f"ERROR: schema를 읽을 수 없음 — {exc}", file=sys.stderr)
        return 2
    if not isinstance(schema, dict) or schema.get("okf_version") != "0.2":
        print("ERROR: config/vault-schema.yaml의 okf_version은 문자열 '0.2'여야 함", file=sys.stderr)
        return 2

    validate_templater_setup(schema, errors)

    excluded = set(schema.get("excluded_top_level", []))
    agent_documents = set(schema.get("agent_documents", []))
    root_allowed = set(schema.get("root_allowed", []))
    folder_rules = schema.get("note_folders", {})
    known_tags = set(schema.get("known_tags", []))
    accepted_tags = known_tags | set(schema.get("legacy_tags", []))
    status_by_type = {
        key: set(values) for key, values in schema.get("status_by_type", {}).items()
    }

    canonical = ROOT / "AGENTS.md"
    if not canonical.is_file() or canonical.is_symlink():
        errors.append("AGENTS.md: 정본은 실제 파일이어야 함")
    for name in ("CLAUDE.md", "GEMINI.md"):
        path = ROOT / name
        if not path.is_symlink() or path.readlink() != Path("AGENTS.md"):
            errors.append(f"{name}: AGENTS.md를 가리키는 symlink여야 함")
    shared_skills = ROOT / ".agents" / "skills"
    if not shared_skills.is_symlink() or shared_skills.readlink() != Path(
        "../.claude/skills"
    ):
        errors.append(".agents/skills: ../.claude/skills를 가리키는 symlink여야 함")

    for directory in ROOT.iterdir():
        if not directory.is_dir() or directory.is_symlink():
            continue
        normalized = re.sub(r"[ _-]", "", directory.name.lower())
        if directory.name != "Daily" and normalized in {"daily", "dailynotes"}:
            errors.append(
                f"{directory.name}/: 비표준 daily directory — Daily/만 사용"
            )

    markdown_files: list[tuple[Path, Path]] = []
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        if relative.parts[0] in excluded:
            continue
        markdown_files.append((path, relative))

    note_stems = {path.stem for path, _ in markdown_files}

    for path, relative in markdown_files:
        label = relative.as_posix()
        if len(relative.parts) == 1 and relative.name in agent_documents:
            continue
        if len(relative.parts) == 1 and relative.name not in root_allowed:
            errors.append(
                f"{label}: vault root에 허용되지 않은 노트 — 지정 note folder로 이동"
            )

        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if not text.strip():
            errors.append(f"{label}: 빈 파일")
            continue
        if relative.name == "index.md":
            validate_index(path, relative, text, schema, errors)
            continue
        if relative.name == "log.md":
            validate_log(relative, text, errors)
            continue

        match = FRONTMATTER_RE.match(text)
        if not match:
            errors.append(f"{label}: parseable YAML frontmatter 누락")
            data: dict[str, Any] | None = None
            body = text
        else:
            data = load_yaml_mapping(match.group(1), label, errors)
            body = text[match.end() :]

        if data is not None:
            concept_type = data.get("type")
            if not is_nonempty_string(concept_type):
                errors.append(f"{label}: non-empty type 필드 누락")
            tags = data.get("tags")
            if tags is not None:
                if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
                    errors.append(f"{label}: tags는 문자열 YAML list여야 함")
                else:
                    unknown = sorted(set(tags) - accepted_tags)
                    if unknown:
                        errors.append(f"{label}: 미등록 tag — {', '.join(unknown)}")

            folder = relative.parts[0] if len(relative.parts) > 1 else None
            rule = folder_rules.get(folder, {}) if folder else {}
            allowed_types = set(rule.get("types", []))
            if allowed_types and concept_type not in allowed_types:
                errors.append(
                    f"{label}: {folder}/에서 허용되지 않은 type '{concept_type}' — "
                    + ", ".join(sorted(allowed_types))
                )
            filename_regex = rule.get("filename_regex")
            if filename_regex and not re.fullmatch(filename_regex, relative.name):
                errors.append(f"{label}: folder filename 규칙 위반")
            for field in rule.get("required_fields", []):
                if field not in data or data[field] in (None, ""):
                    errors.append(f"{label}: 필수 frontmatter field 누락 — {field}")
            if isinstance(tags, list):
                for required_tag in rule.get("required_tags", []):
                    if required_tag not in tags:
                        errors.append(f"{label}: 필수 tag 누락 — {required_tag}")
            if rule.get("english_filename") and re.search(r"[가-힣]", path.stem):
                errors.append(f"{label}: 파일명은 영문, 한글 이름은 aliases로 관리")

            if "status" in data and concept_type in status_by_type:
                if data["status"] not in status_by_type[concept_type]:
                    errors.append(
                        f"{label}: type '{concept_type}'의 미등록 status — {data['status']}"
                    )

            for field in ("subject", "role", "title"):
                if isinstance(data.get(field), str) and "[[" in data[field]:
                    errors.append(f"{label}: {field}에는 wikilink 사용 금지")

            validate_okf_v02_fields(data, body, label, errors, warnings)

        if not body.strip():
            warnings.append(f"{label}: 본문이 비어 있음")
        if "<%" in text or "%>" in text:
            errors.append(f"{label}: 해석되지 않은 Templater token 존재")
        for bad in NESTED_WIKILINK_RE.findall(text):
            errors.append(f"{label}: 중첩 wikilink — {bad[:70]}")
        for link in WIKILINK_RE.findall(text):
            target = link.split("/")[-1].strip()
            if not target or "." in target:
                continue
            if target not in note_stems:
                errors.append(f"{label}: 깨진 wikilink [[{link}]]")

    if warnings:
        print(f"WARN: {len(warnings)}건")
        for warning in warnings:
            print("  -", warning)
    if errors:
        print(f"FAIL: {len(errors)}건")
        for error in errors:
            print("  -", error)
        return 1

    print(
        f"OK: OKF v{schema['okf_version']} hard conformance + vault rules 통과 "
        f"({len(markdown_files)} markdown files)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
