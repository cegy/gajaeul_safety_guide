import io
import pdfplumber
import pandas as pd
import streamlit as st
from parser import parse_doc

st.set_page_config(page_title="가재울 수련활동 안내(보기 쉽게)", layout="wide")

st.title("📘 2025학년도 1학년 수련활동 — 보기 쉽게 정리")
st.caption("배부용 PDF를 업로드하면, 문서 내용을 그대로 보되 더 읽기 쉽게 탭·표·접이식으로 정리해 보여줍니다.")

uploaded = st.file_uploader("배부용 PDF 업로드", type=["pdf"])

@st.cache_data(show_spinner=False)
def extract_text(file_bytes: bytes) -> str:
    parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for p in pdf.pages:
            parts.append(p.extract_text() or "")
    return "\n".join(parts)

if not uploaded:
    st.info("상단에서 PDF를 업로드해 주세요. (배부용 안내문 원본 그대로 → 보기 쉽게 정리)")
else:
    raw_text = extract_text(uploaded.read())
    data = parse_doc(raw_text)

    # ===== 상단 핵심 카드 =====
    st.subheader("📅 기본 정보")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("일정", data["tripRange"] or "미탐지")
        st.caption("문서의 <기본 계획>에서 추출")  # 일정
    with c2:
        st.metric("숙소", data["lodging"] or "미탐지")
        st.caption("숙소 정보/연락처")  # 숙소
    with c3:
        st.metric("집합", (data["meetTime"] or "미탐지") + " / " + (data["meetPlace"] or "미탐지"))

    # ===== 탭 구성 =====
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "① 준비물/금지물품", "② 준수사항", "③ 안전교육", "④ 프로그램(3일간)", "⑤ 숙소 배정", "⑥ 부록"
    ])

    # --- 탭1: 준비물 / 금지물품 ---
    with tab1:
        st.markdown("### 📝 필수 준비물")
        req_df = pd.DataFrame({"항목": data["required"]}) if data["required"] else pd.DataFrame({"항목": []})
        st.dataframe(req_df, use_container_width=True)

        st.markdown("### 🚫 반입 금지 물품")
        ban_df = pd.DataFrame({"항목": data["banned"]}) if data["banned"] else pd.DataFrame({"항목": []})
        st.dataframe(ban_df, use_container_width=True)

        if not (data["required"] or data["banned"]):
            st.info("문서에서 준비물/금지물품 블록을 찾지 못했습니다. (레이블 변경 또는 PDF 텍스트 추출 상태 확인)")

    # --- 탭2: 학생 기본 준수사항 ---
    with tab2:
        st.markdown("### 📌 학생 기본 준수사항")
        if data["rules"]:
            for i, r in enumerate(data["rules"], 1):
                st.markdown(f"{i}. {r}")
        else:
            st.info("문서에서 '학생 기본 준수사항' 항목을 찾지 못했습니다.")

    # --- 탭3: 안전사고 예방 교육 ---
    with tab3:
        st.markdown("### 🛡 안전사고 예방 교육 (①~⑥)")
        if data["safetyParts"]:
            for sec, items in data["safetyParts"].items():
                with st.expander(sec, expanded=False):
                    for it in items:
                        st.markdown(f"- {it}")
        else:
            st.info("문서에서 안전사고 예방 교육 섹션을 찾지 못했습니다.")
        if data["sexualViolenceTips"]:
            st.markdown("### ※ 성폭력 예방")
            for it in data["sexualViolenceTips"]:
                st.markdown(f"- {it}")

    # --- 탭4: 3일간 프로그램 ---
    with tab4:
        st.markdown("### 📖 프로그램(원문 그대로 보이기 + 핵심 포인트)")
        col_a, col_b = st.columns(2)
        with col_a:
            st.caption("원문 블록")
            st.text(data["scheduleBlock"] or "시간표 원문 블록 탐지 실패")
        with col_b:
            st.caption("핵심 프로그램 키워드(문서에서 뽑아 하이라이트)")
            if data["programHighlights"]:
                for kw in data["programHighlights"]:
                    st.markdown(f"- {kw}")
            else:
                st.info("키워드 추출 결과가 비어있습니다. (문서 포맷에 따라 다를 수 있어요)")

    # --- 탭5: 숙소 배정 ---
    with tab5:
        st.markdown("### 🏠 학급별 숙소 배정")
        st.caption("원문 블록")
        st.text(data["roomBlock"] or "숙소 배정 원문 블록 탐지 실패")

        if data["roomSummary"]:
            st.markdown("#### 반별 요약")
            room_df = pd.DataFrame(data["roomSummary"])
            st.dataframe(room_df, use_container_width=True)

    # --- 탭6: 부록(학교폭력 유형 등) ---
    with tab6:
        st.markdown("### 📎 부록")
        if data["appendixBlock"]:
            st.text(data["appendixBlock"])
            st.caption("문서의 [학교폭력의 유형] 등 참고용 부록 블록")
        else:
            st.info("부록 블록을 찾지 못했습니다.")

    # 원문 전체 보기(옵션)
    with st.expander("🔎 원문 텍스트 전체 보기 (디버그용)"):
        st.text(raw_text)
