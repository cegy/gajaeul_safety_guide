import re

def _clean(txt: str) -> str:
    return re.sub(r"\u00a0", " ", txt).strip()

def _lines(block: str):
    return [ln.strip() for ln in block.splitlines() if ln.strip()]

def parse_doc(txt: str):
    t = _clean(txt)

    # ===== 기본 계획 =====
    tripRange = _pick(t, r"일정\s*[:：]\s*([0-9.\-()~\s]+)")
    lodging   = _pick(t, r"숙소\s*정보\s*[:：]\s*([^\n]+)")  # 예: 청포대썬셋수련원 / 041-674-9393
    meetTime  = _pick(t, r"집합\s*일시\s*[:：]\s*([^\n]+)")
    meetPlace = _pick(t, r"집합\s*장소\s*[:：]\s*([^\n]+)")

    # ===== 준비물/금지물품 (문서 특정 레이아웃에 최적화) =====
    required, banned = [], []
    if "필수품" in t and "규제" in t:
        after_req = t.split("필수품", 1)[1]
        before_ban = after_req.split("규제", 1)[0]
        required = _bullet_items(before_ban)

        after_ban = t.split("규제", 1)[1]
        # '규제 대상 물건' 헤더 다음 ~ '학생 기본 준수사항' 직전
        banned_blk = re.split(r"(학생\s*기본\s*준수사항|5\.\s*학생\s*기본\s*준수사항)", after_ban)[0]
        banned = _bullet_items(banned_blk)

    # ===== 학생 기본 준수사항 =====
    rulesBlock = _match_block(t, r"학생\s*기본\s*준수사항[\s\S]*?(?=\n\s*\d+\.\s|<안전사고\s*예방\s*교육>|$)")
    rules = []
    if rulesBlock:
        rules = [x for x in re.split(r"\n\s*[가-하]\.\s*", rulesBlock)[1:] if x.strip()]
        rules = [re.sub(r"\s+", " ", x).strip() for x in rules]

    # ===== 안전사고 예방 교육 (①~⑥) =====
    safetyBlock = _match_block(t, r"<안전사고\s*예방\s*교육>[\s\S]*?(?=\n\s*※|$)")
    safetyParts = {}
    if safetyBlock:
        safetyParts["① 도보 이동 시"] = _dash_items(_slice_until(safetyBlock, r"②"))
        safetyParts["② 버스 이동 시"] = _dash_items(_slice_between(safetyBlock, r"②", r"③"))
        safetyParts["③ 숙소 안전"]   = _dash_items(_slice_between(safetyBlock, r"③", r"④"))
        safetyParts["④ 식품 안전"]   = _dash_items(_slice_between(safetyBlock, r"④", r"⑤"))
        safetyParts["⑤ 폭력으로부터 안전"] = _dash_items(_slice_between(safetyBlock, r"⑤", r"⑥"))
        safetyParts["⑥ 도난으로부터 안전"] = _dash_items(_slice_from(safetyBlock, r"⑥"))

    # ※ 성폭력 예방 (안전교육 다음)
    sexual_block = _match_block(t, r"※\s*성폭력\s*예방[\s\S]*?(?=\n\s*\[|$)")
    sexualViolenceTips = _dash_items(sexual_block) if sexual_block else []

    # ===== 프로그램(1~3일차) =====
    scheduleBlock = _match_block(t, r"1일차[\s\S]*?숙소\s*정리\s*및\s*취침")
    programHighlights = []
    if scheduleBlock:
        # 핫 키워드 뽑기 (자연어 라인 중 활동명 추정)
        hot = [
            "대형젠가", "미션페스티벌", "사진작가", "맛조개 잡기", "해변 트레킹",
            "명랑 운동회", "레크리에이션", "장기자랑", "캠프파이어", "Balance Quiz",
            "해솔길", "도전 골든벨", "도미노", "한마음 한뜻"
        ]
        lines = _lines(scheduleBlock)
        for h in hot:
            if any(h in ln for ln in lines):
                programHighlights.append(h)

    # ===== 숙소 배정 =====
    roomBlock = _match_block(t, r"학생\s*숙소\s*배정[\s\S]*")
    roomSummary = []
    if roomBlock:
        # 대략적인 반별 방 수 요약 (정규식 간단 추정)
        # 예: "1반", "2반"… 라인 기준으로 섹션 나누기
        blocks = re.split(r"\n\s*(\d+반)\s*\n", roomBlock)
        # blocks: ["...앞", "1반", "섹션", "2반", "섹션", ...]
        for i in range(1, len(blocks), 2):
            ban = blocks[i]
            sect = blocks[i+1] if i+1 < len(blocks) else ""
            rooms = re.findall(r"(오션|벨|필드|오션A|오션B|오션C|오션D)\s*[A-Z]?\s*\d+호", sect)
            females = re.findall(r"\(여\s*\d+\)", sect)
            males   = re.findall(r"\(남\s*\d+\)", sect)
            roomSummary.append({
                "반": ban,
                "객실수(추정)": len(rooms),
                "남학생 객실(표기수)": len(males),
                "여학생 객실(표기수)": len(females),
            })

    # ===== 부록 (학교폭력의 유형 등) =====
    appendixBlock = _match_block(t, r"\[\s*학교폭력의\s*유형\s*\][\s\S]*")

    return {
        "tripRange": tripRange,
        "lodging": lodging,
        "meetTime": meetTime,
        "meetPlace": meetPlace,
        "required": required,
        "banned": banned,
        "rules": rules,
        "safetyParts": safetyParts,
        "sexualViolenceTips": sexualViolenceTips,
        "scheduleBlock": scheduleBlock or "",
        "programHighlights": sorted(set(programHighlights)),
        "roomBlock": roomBlock or "",
        "roomSummary": roomSummary,
        "appendixBlock": appendixBlock or ""
    }

# ---------- helpers ----------

def _pick(text, pattern, grp=1):
    m = re.search(pattern, text)
    return (m.group(grp).strip() if m else "")

def _match_block(text, pattern):
    m = re.search(pattern, text)
    return m.group(0) if m else ""

def _bullet_items(block):
    if not block: return []
    items = re.split(r"\n\s*[-•·]\s*", block)[1:]
    return [re.sub(r"\s+", " ", x).strip() for x in items if x.strip()]

def _dash_items(block):
    if not block: return []
    return [ln.strip("- ").strip() for ln in block.splitlines() if ln.strip().startswith("-")]

def _slice_until(block, marker):
    m = re.split(marker, block, maxsplit=1)
    return m[0] if m else block

def _slice_between(block, start, end):
    a = re.split(start, block, maxsplit=1)
    if len(a) < 2: return ""
    b = re.split(end, a[1], maxsplit=1)
    return b[0]

def _slice_from(block, start):
    a = re.split(start, block, maxsplit=1)
    return a[1] if len(a) > 1 else ""
