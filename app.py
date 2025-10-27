import io
import re
import pdfplumber
import pandas as pd
import streamlit as st
from pathlib import Path

# =========================
# 설정
# =========================
PDF_PATH = Path("2025학년도 1학년 수련활동 사전안전교육(배부용).pdf")  # 첨부 파일명 그대로 사용

# =========================
# 상큼한 스타일 세팅
# =========================
st.set_page_config(page_title="가재울 1학년 수련활동 · 보기 쉽게", page_icon="🍊", layout="wide")
st.markdown("""
<style>
:root { --accent: #FF9E80; --accent2: #80CBC4; --chip: #FFE7DF; }
.block-container { padding-top: 1.4rem; }
h1, h2, h3 { letter-spacing: .3px; }
.metric-label { color:#666 !important; }
.stTabs [data-baseweb="tab-list"] { gap: .4rem; }
.stTabs [data-baseweb="tab"] { background: #fff; border-radius: 12px; padding: .6rem .9rem; border: 1px solid #eee; }
.stTabs [aria-selected="true"] { border-color: var(--accent); box-shadow: 0 0 0 2px #fff inset; }
.code-like { background:#fff; border:1px solid #eee; border-radius:12px; padding:.75rem 1rem; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre-wrap; }
.kv { display:grid; grid-template-columns: 120px 1fr; gap:.4rem .8rem; align-items:center; }
.kv .k { color:#666; }
.badge { display:inline-block; background:var(--chip); border-radius:999px; padding:.2rem .6rem; margin:.15rem .2rem 0 0; font-size:.9rem; }
.card { border:1px solid #eee; border-radius:16px; padding:1rem; background:#fff; }
hr.soft { border:none; border-top:1px dashed #eee; margin:1.0rem 0; }
.small { color:#777; font-size:.92rem; }
</style>
""", unsafe_allow_html=True)

st.title("🍊 2025학년도 1학년 수련활동 · 보기 쉽게")
st.caption("첨부된 배부용 PDF를 그대로 분석해 일정·숙소·집합, 준비물/금지물품, 준수사항, 안전교육(①~⑥), 프로그램(3일), 숙소 배정을 상큼하게 정리해 보여줍니다.")

# =========================
# 유틸 함수
# =========================
@st.cache_data(show_spinner=False)
def extract_text_from_pdf(pdf_path: Path) -> str:
    text_parts = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for p in pdf.pages:
            text_parts.append(p.extract_text() or "")
    return "\n".join(text_parts)

def _clean(txt: str) -> str:
    return re.sub(r"\u00a0", " ", txt).strip()

def _pick(text: str, pattern: str, grp: int = 1) -> str:
    m = re.search(pattern, text)
    return (m.group(grp).strip() if m else "")

def _match_block(text: str, pattern: str) -> str:
    m = re.search(pattern, text)
    return m.group(0) if m else ""

def _bullet_items(block: str):
    if not block: return []
    items = re.split(r"\n\s*[-•·]\s*", block)[1:]
    return [re.sub(r"\s+", " ", x).strip() for x in items if x.strip()]

def _dash_items(block: str):
    if not block: return []
    return [ln.strip("- ").strip() for ln in block.splitlines() if ln.strip().startswith("-")]

def parse_doc(txt: str) -> dict:
    t = _clean(txt)

    # ----- 기본 계획 -----
    tripRange = _pick(t, r"일정\s*[:：]\s*([0-9.\-()~\s,]+)")
    lodging   = _pick(t, r"숙소\s*정보\s*[:：]\s*([^\n]+)")                # 예: 청포대썬셋수련원 / 041-674-9393
    meetTime  = _pick(t, r"집합\s*일시\s*[:：]\s*([^\n]+)")                # 예: 2025년 10월 27일(월) 08:00
    meetPlace = _pick(t, r"집합\s*장소\s*[:：]\s*([^\n]+)")                # 예: 각 학급 교실

    # ----- 준비물 / 금지물품 -----
    required, banned = [], []
    if "필수품" in t and "규제 대상 물건" in t:
        after_req = t.split("필수품", 1)[1]
        before_ban = after_req.split("규제 대상 물건", 1)[0]
        required = _bullet_items(before_ban)

        after_ban = t.split("규제 대상 물건", 1)[1]
        banned_blk = re.split(r"(학생\s*기본\s*준수사항|5\.\s*학생\s*기본\s*준수사항|<안전사고\s*예방\s*교육>)", after_ban)[0]
        banned = _bullet_items(banned_blk)

    # ----- 학생 기본 준수사항 (가.~하.) -----
    rulesBlock = _match_block(t, r"학생\s*기본\s*준수사항[\s\S]*?(?=\n\s*\d+\.\s|<안전사고\s*예방\s*교육>|$)")
    rules = []
    if rulesBlock:
        rules = [x for x in re.split(r"\n\s*[가-하]\.\s*", rulesBlock)[1:] if x.strip()]
        rules = [re.sub(r"\s+", " ", x).strip() for x in rules]

    # ----- 안전사고 예방 교육 (①~⑥) -----
    safetyBlock = _match_block(t, r"<안전사고\s*예방\s*교육>[\s\S]*?(?=\n\s*※|$)")
    safetyParts = {}
    if safetyBlock:
        def slice_between(src, start, end=None):
            a = src.find(start)
            if a < 0: return ""
            if end:
                b = src.find(end, a + len(start))
                return src[a+len(start): b if b > -1 else None]
            return src[a+len(start):]
        safetyParts["① 도보 이동 시"] = _dash_items(slice_between(safetyBlock, "① 도보 이동 시", "②"))
        safetyParts["② 버스 이동 시"] = _dash_items(slice_between(safetyBlock, "② 버스 이동 시", "③"))
        safetyParts["③ 숙소 안전"]   = _dash_items(slice_between(safetyBlock, "③ 숙소 안전", "④"))
        safetyParts["④ 식품 안전"]   = _dash_items(slice_between(safetyBlock, "④ 식품 안전", "⑤"))
        safetyParts["⑤ 폭력으로부터 안전"] = _dash_items(slice_between(safetyBlock, "⑤ 폭력으로부터 안전", "⑥"))
        safetyParts["⑥ 도난으로부터 안전"] = _dash_items(slice_between(safetyBlock, "⑥ 도난으로부터 안전", "※"))

    # ※ 성폭력 예방
    sexual_block = _match_block(t, r"※\s*성폭력\s*예방[\s\S]*?(?=\n\s*\[|$)")
    sexualViolenceTips = _dash_items(sexual_block) if sexual_block else []

    # ----- 프로그램(1~3일차) -----
    scheduleBlock = _match_block(t, r"1일차[\s\S]*?숙소\s*정리\s*및\s*취침")
    if not scheduleBlock:
        scheduleBlock = _match_block(t, r"1일차[\s\S]*?3일차[\s\S]*?(숙소\s*정리\s*및\s*취침)?")

    # 하이라이트 키워드(가벼운 룰 기반)
    programHighlights = []
    if scheduleBlock:
        hot = [
            "대형젠가", "미션페스티벌", "사진작가", "맛조개", "해변 트레킹",
            "명랑 운동회", "레크리에이션", "장기자랑", "캠프파이어",
            "Balance Quiz", "해솔길", "도전 골든벨", "도미노", "한마음 한뜻"
        ]
        lines = [ln.strip() for ln in scheduleBlock.splitlines() if ln.strip()]
        for h in hot:
            if any(h in ln for ln in lines):
                programHighlights.append(h)
        programHighlights = sorted(set(programHighlights))

    # ----- 숙소 배정 -----
    roomBlock = _match_block(t, r"학생\s*숙소\s*배정[\s\S]*")
    roomSummary = []
    if roomBlock:
        blocks = re.split(r"\n\s*(\d+반)\s*\n", roomBlock)  # ["...", "1반", "섹션", "2반", "섹션", ...]
        for i in range(1, len(blocks), 2):
            klass = blocks[i]
            sect  = blocks[i+1] if i+1 < len(blocks) else ""
            rooms = re.findall(r"(오션[A-D]?|벨|필드)\s*[A-Z]?\s*\d+호", sect)
            females = re.findall(r"\(여\s*\d+\)", sect)
            males   = re.findall(r"\(남\s*\d+\)", sect)
            roomSummary.append({
                "반": klass,
                "객실수(추정)": len(rooms),
                "남 객실(표기수)": len(males),
                "여 객실(표기수)": len(females),
            })

    # ----- 부록(학교폭력의 유형 등) -----
    appendixBlock = _match_block(t, r"\[\s*학교폭력의\s*유형\s*\][\s\S]*")

    return {
        "tripRange": tripRange, "lodging": lodging,
        "meetTime": meetTime,   "meetPlace": meetPlace,
        "required": required,   "banned": banned,
        "rules": rules,         "safetyParts": safetyParts,
        "sexualViolenceTips": sexualViolenceTips,
        "scheduleBlock": scheduleBlock or "",
        "programHighlights": programHighlights,
        "roomBlock": roomBlock or "",
        "roomSummary": roomSummary,
        "appendixBlock": appendixBlock or ""
    }

def df_or_empty(title, rows):
    st.markdown(f"**{title}**")
    if rows:
        st.dataframe(pd.DataFrame({"항목": rows}), use_container_width=True, hide_index=True)
    else:
        st.info("해당 섹션을 문서에서 찾지 못했습니다.")

def pills(items):
    if not items: return
    st.markdown("".join([f"<span class='badge'>{x}</span>" for x in items]), unsafe_allow_html=True)

# =========================
# 본문 렌더링
# =========================
if not PDF_PATH.exists():
    st.error(f"PDF 파일을 찾을 수 없습니다: {PDF_PATH.name}\n\napp.py와 같은 폴더에 PDF를 두고 실행해 주세요.")
    st.stop()

with st.spinner("PDF 텍스트 추출 중..."):
    raw_text = extract_text_from_pdf(PDF_PATH)

with st.spinner("문서 구조 분석 중..."):
    data = parse_doc(raw_text)

# ===== 상단 핵심 카드 =====
st.subheader("🍃 기본 계획")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("일정", data["tripRange"] or "미탐지")
    st.caption("문서의 <기본 계획>에서 추출")
with c2:
    st.metric("숙소", data["lodging"] or "미탐지")
    st.caption("숙소명 / 연락처")
with c3:
    st.metric("집합", data["meetTime"] or "미탐지")
    st.caption(f"장소: {data['meetPlace'] or '미탐지'}")

st.markdown("<hr class='soft'/>", unsafe_allow_html=True)

# ===== 탭 =====
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧳 준비물·금지물품", "✅ 준수사항", "🛡 안전교육(①~⑥)", "📖 프로그램(3일)", "🏠 숙소 배정", "📎 부록"
])

with tab1:
    colA, colB = st.columns(2)
    with colA:
        df_or_empty("📝 필수 준비물", data["required"])
    with colB:
        df_or_empty("🚫 반입 금지 물품", data["banned"])

with tab2:
    st.markdown("### 학생 기본 준수사항")
    if data["rules"]:
        for i, r in enumerate(data["rules"], 1):
            st.markdown(f"{i}. {r}")
    else:
        st.info("문서에서 '학생 기본 준수사항' 섹션을 찾지 못했습니다.")

with tab3:
    st.markdown("### 안전사고 예방 교육 (①~⑥)")
    if data["safetyParts"]:
        for k, v in data["safetyParts"].items():
            with st.expander(k, expanded=False):
                for it in v:
                    st.markdown(f"- {it}")
    else:
        st.info("문서에서 '안전사고 예방 교육' 섹션을 찾지 못했습니다.")
    if data["sexualViolenceTips"]:
        st.markdown("### ※ 성폭력 예방")
        for it in data["sexualViolenceTips"]:
            st.markdown(f"- {it}")

with tab4:
    st.markdown("### 원문 블록")
    st.markdown("<div class='code-like'>"+(data["scheduleBlock"] or "시간표 원문 블록을 탐지하지 못했습니다.")+"</div>", unsafe_allow_html=True)
    st.markdown("### 하이라이트")
    if data["programHighlights"]:
        pills(data["programHighlights"])
    else:
        st.info("하이라이트 키워드를 찾지 못했습니다. (문서 포맷 차이 가능)")

with tab5:
    st.markdown("### 원문 블록")
    st.markdown("<div class='code-like'>"+(data["roomBlock"] or "숙소 배정 원문 블록을 탐지하지 못했습니다.")+"</div>", unsafe_allow_html=True)
    if data["roomSummary"]:
        st.markdown("### 반별 요약")
        st.dataframe(pd.DataFrame(data["roomSummary"]), use_container_width=True, hide_index=True)
    else:
        st.info("반별 요약을 생성하지 못했습니다. (표/줄바꿈 포맷 차이 가능)")

with tab6:
    if data["appendixBlock"]:
        st.markdown("### 부록(학교폭력의 유형 등)")
        st.markdown("<div class='code-like'>"+data["appendixBlock"]+"</div>", unsafe_allow_html=True)
    else:
        st.info("부록 섹션을 탐지하지 못했습니다.")

# ===== 내려받기(학부모 안내문 초안) =====
st.markdown("<hr class='soft'/>", unsafe_allow_html=True)
st.subheader("👨‍👩‍👧 학부모 안내문 초안")
parent_note = f"""[가정 통신문 안내]

1. 일정: {data['tripRange'] or '(문서에서 탐지)'}
2. 숙소: {data['lodging'] or '(문서에서 탐지)'}
3. 집합 일시/장소: {data['meetTime'] or '(문서에서 탐지)'} / {data['meetPlace'] or '(문서에서 탐지)'}
4. 준비물: {", ".join(data['required']) or '(문서 참조)'}
5. 반입 금지: {", ".join(data['banned']) or '(문서 참조)'}
6. 기본 준수사항(요약): {", ".join(data['rules'][:5]) or '(문서 참조)'}

※ 상세 시간표와 숙소 배정은 학교 사정에 따라 변경될 수 있습니다.
"""
st.code(parent_note, language="markdown")
st.download_button("안내문 .txt 다운로드", parent_note.encode("utf-8"),
                   file_name="parent_note.txt", mime="text/plain")

# 디버그용 원문 텍스트 보기
with st.expander("🔎 원문 전체 텍스트 (디버그용)"):
    st.text(raw_text)
