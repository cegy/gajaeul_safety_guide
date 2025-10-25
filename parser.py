import re

def parse_doc(txt: str):
    clean = re.sub(r"\u00a0", " ", txt)

    tripRange = re.search(r"일정\s*[:：]\s*([0-9.\-~()\s]+)", clean)
    lodging   = re.search(r"숙소 정보[:：]\s*([^\n]+)", clean)
    meetTime  = re.search(r"집합 일시\s*[:：]\s*([^\n]+)", clean)
    meetPlace = re.search(r"집합 장소\s*[:：]\s*([^\n]+)", clean)

    required = re.findall(r"- ([^-\n]+)", clean.split("필수품")[1].split("규제")[0]) if "필수품" in clean else []
    banned   = re.findall(r"- ([^-\n]+)", clean.split("규제 대상 물건")[1].split("학생 기본 준수사항")[0]) if "규제 대상 물건" in clean else []

    rules_block = re.search(r"학생 기본 준수사항[\s\S]*?(?=\n\s*\d+\.\s|<안전사고 예방 교육>)", clean)
    rules = []
    if rules_block:
        rules = re.split(r"\n\s*[가-하]\.\s*", rules_block.group(0))[1:]

    safety_block = re.search(r"<안전사고 예방 교육>[\s\S]*?(?=성폭력 예방|학교폭력)", clean)
    safetyParts = {}
    if safety_block:
        sections = {
            "도보 이동 시": r"① 도보 이동 시[\s\S]*?(?=② 버스 이동 시)",
            "버스 이동 시": r"② 버스 이동 시[\s\S]*?(?=③ 숙소 안전)",
            "숙소 안전":   r"③ 숙소 안전[\s\S]*?(?=④ 식품 안전)",
            "식품 안전":   r"④ 식품 안전[\s\S]*?(?=⑤ 폭력으로부터 안전)",
            "폭력으로부터 안전": r"⑤ 폭력으로부터 안전[\s\S]*?(?=⑥ 도난으로부터 안전)",
            "도난으로부터 안전": r"⑥ 도난으로부터 안전[\s\S]*"
        }
        for k, pat in sections.items():
            m = re.search(pat, safety_block.group(0))
            if m:
                safetyParts[k] = [x.strip("- ").strip() for x in m.group(0).split("\n") if x.strip().startswith("-")]

    scheduleBlock = re.search(r"1일차[\s\S]*?취침", clean)
    roomBlock     = re.search(r"학생 숙소 배정[\s\S]*", clean)

    return {
        "tripRange": tripRange.group(1).strip() if tripRange else "",
        "lodging": lodging.group(1).strip() if lodging else "",
        "meetTime": meetTime.group(1).strip() if meetTime else "",
        "meetPlace": meetPlace.group(1).strip() if meetPlace else "",
        "required": required,
        "banned": banned,
        "rules": [r.strip() for r in rules if r.strip()],
        "safetyParts": safetyParts,
        "scheduleBlock": scheduleBlock.group(0).strip() if scheduleBlock else "",
        "roomBlock": roomBlock.group(0).strip() if roomBlock else ""
    }
