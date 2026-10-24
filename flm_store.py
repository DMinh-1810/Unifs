"""Đọc syllabus đã lưu từ FLM (data/flm_data.json -> 'syllabi') để chatbot trả lời về đánh giá, tín chỉ, CLO...
File này do tiện ích Chrome (flm_content.js) + server.py ghi; ở đây chỉ ĐỌC, tự nạp lại khi file đổi."""
import json
import re
from config import DATA_DIR

FLM_FILE = DATA_DIR / "flm_data.json"
_cache = {"mtime": None, "data": {}}

SECTIONS = ("overview", "assessment", "materials", "clos", "schedule", "questions")


def _syllabi() -> dict:
    try:
        m = FLM_FILE.stat().st_mtime
    except OSError:
        return {}
    if _cache["mtime"] != m:
        try:
            d = json.loads(FLM_FILE.read_text(encoding="utf-8"))
        except Exception:
            d = {}
        s = d.get("syllabi") if isinstance(d, dict) else None
        _cache.update(mtime=m, data=s if isinstance(s, dict) else {})
    return _cache["data"]


def _k(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def _get(d: dict, *names, default=""):
    nd = {_k(k): v for k, v in d.items()}
    for n in names:
        if _k(n) in nd and str(nd[_k(n)]).strip():
            return nd[_k(n)]
    return default


def _cut(s, n):
    s = str(s or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _num(s):
    m = re.search(r"\d+(?:[.,]\d+)?", str(s or ""))
    return float(m.group().replace(",", ".")) if m else None


def available_subjects() -> list:
    return sorted(v.get("subject_code", k) for k, v in _syllabi().items())


def has_subject(code: str) -> bool:
    return bool(code) and code.strip().upper() in _syllabi()


def find_code_in_text(text: str):
    """Tìm mã môn (đã có syllabus) xuất hiện trong câu hỏi, không phân biệt hoa thường."""
    low = text.lower()
    for key, v in _syllabi().items():
        code = str(v.get("subject_code", key))
        if re.search(rf"(?<![a-z0-9]){re.escape(code.lower())}(?![a-z0-9])", low):
            return code
    return None


def _assessment_rows(syl: dict) -> list:
    out = []
    for r in syl.get("assessments", []):
        out.append({
            "category": _get(r, "Category"),
            "type": _get(r, "Type"),
            "part": _num(_get(r, "Part")),
            "weight_percent": _num(_get(r, "Weight")),
            "completion_criteria": _get(r, "Completion Criteria"),
            "duration": _cut(_get(r, "Duration"), 200),
            "clo": _cut(_get(r, "CLO"), 200),
            "question_type": _cut(_get(r, "Question Type"), 200),
            "number_of_questions": _cut(_get(r, "No Question"), 120),
            "knowledge_and_skill": _cut(_get(r, "Knowledge and Skill"), 200),
            "grading_guide": _cut(_get(r, "Grading Guide"), 500),
            "note": _cut(_get(r, "Note"), 600),
        })
    return out


def get_subject_info(subject_code: str, section: str = "overview") -> dict:
    syl = _syllabi().get((subject_code or "").strip().upper())
    if not syl:
        return {"error": f"Chưa có dữ liệu syllabus cho môn '{subject_code}'.",
                "available_subjects": available_subjects()}
    section = (section or "overview").strip().lower()
    if section not in SECTIONS:
        section = "overview"
    info = syl.get("info", {})
    base = {"subject_code": syl.get("subject_code"), "section": section,
            "data_source": "FLM (syllabus đã lưu)", "exported_at": syl.get("exported_at")}

    if section == "assessment":
        rows = _assessment_rows(syl)
        total = sum(r["weight_percent"] or 0 for r in rows)
        return {**base, "name": _get(info, "Course Name English", "Syllabus Name"),
                "assessments": rows, "total_weight_percent": round(total, 1),
                "min_avg_mark_to_pass": _num(_get(info, "MinAvgMarkToPass")),
                "scoring_scale": _num(_get(info, "Scoring Scale")),
                "student_tasks": _cut(_get(info, "StudentTasks"), 600)}
    if section == "materials":
        return {**base, "materials": [{k: v for k, v in r.items() if v} for r in syl.get("materials", [])]}
    if section == "clos":
        return {**base, "clos": [{"clo": _get(r, "CLO Name"), "details": _get(r, "CLO Details")} for r in syl.get("clos", [])]}
    if section == "schedule":
        return {**base, "sessions": [{"session": _get(r, "Session"), "topic": _cut(_get(r, "Topic"), 160),
                                      "lo": _cut(_get(r, "LO"), 80)} for r in syl.get("schedule", [])]}
    if section == "questions":
        return {**base, "constructive_questions": [{"session": _get(r, "Session No"), "name": _get(r, "Name"),
                                                    "details": _get(r, "Details")} for r in syl.get("questions", [])]}
    # overview
    rows = _assessment_rows(syl)
    return {**base,
            "name": _get(info, "Syllabus Name"), "name_en": _get(info, "Course Name English"),
            "credits": _num(_get(info, "NoCredit")),
            "prerequisite": _get(info, "Pre-Requisite") or "Không có",
            "time_allocation": _get(info, "Time Allocation"),
            "min_avg_mark_to_pass": _num(_get(info, "MinAvgMarkToPass")),
            "scoring_scale": _num(_get(info, "Scoring Scale")),
            "description": _cut(_get(info, "Description"), 800),
            "student_tasks": _cut(_get(info, "StudentTasks"), 500),
            "assessment_summary": [{"category": r["category"], "weight_percent": r["weight_percent"],
                                    "part": r["part"]} for r in rows],
            "counts": {"clos": len(syl.get("clos", [])), "sessions": len(syl.get("schedule", [])),
                       "materials": len(syl.get("materials", []))}}
