import io
import pdfplumber
import pandas as pd
import streamlit as st
from parser import parse_doc

st.set_page_config(page_title="가재울 수련활동 안내", layout="wide")

st.title("📘 2025학년도 1학년 수련활동 안내")
st.caption("PDF 안내문을 자동으로 분석해 학생·학부모용 정보를 제공합니다.")

uploaded = st.file_uploader("배부용 PDF 업로드", type=["pdf"])

@st.cache_data(show_spinner=False)
def extract_text(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for p in pdf.pages:
            text_parts.append(p.extract_text() or "")
    return "\n".join(text_parts)

def checklist_df(items):
    return pd.DataFrame({"항목": items, "준비완료": [""]*len(items)})

if uploaded:
    file_bytes = uploaded.read()
    text = extract_text(file_bytes)
    data = parse_doc(text)

    st.subheader("📅 기본 계획")
    st.markdown(f"- 일정: **{data['tripRange'] or '미탐지'}**")
    st.markdown(f"- 숙소: **{data['lodging'] or '미탐지'}**")
    st.markdown(f"- 집합: {data['meetTime'] or '미탐지'} / 장소: {data['meetPlace'] or '미탐지'}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📝 필수 준비물")
        df_req = checklist_df(data["required"])
        st.dataframe(df_req, use_container_width=True)
        csv_buf = io.StringIO()
        df_req.to_csv(csv_buf, index=False)
        st.download_button("체크리스트 CSV 내려받기", csv_buf.getvalue(),
                           file_name="checklist.csv", mime="text/csv")

        st.subheader("🚫 반입 금지 물품")
        for x in data["banned"]:
            st.markdown(f"- {x}")

    with col2:
        st.subheader("📌 학생 기본 준수사항")
        for x in data["rules"]:
            st.markdown(f"- {x}")

        st.subheader("🛡 안전사고 예방 교육")
        for sec, items in data["safetyParts"].items():
            with st.expander(sec, expanded=False):
                for i in items: st.markdown(f"- {i}")

    st.subheader("📖 3일간 프로그램 일정")
    st.text(data["scheduleBlock"] or "시간표 원문 탐지 실패")

    st.subheader("🏠 학급별 숙소 배정")
    st.text(data["roomBlock"] or "숙소 배정 원문 탐지 실패")

    st.subheader("👨‍👩‍👧 학부모 안내문 초안")
    parent_note = f"""
[가정통신문 안내]

1. 일정: {data['tripRange']}
2. 숙소: {data['lodging']}
3. 집합 일시/장소: {data['meetTime']} / {data['meetPlace']}
4. 준비물: {", ".join(data["required"]) or "문서 참조"}
5. 반입 금지: {", ".join(data["banned"]) or "문서 참조"}
6. 기본 준수사항: {", ".join(data["rules"][:5]) or "문서 참조"}

※ 상세 시간표와 숙소 배정은 학교 사정에 따라 변동될 수 있습니다.
"""
    st.code(parent_note, language="markdown")
    st.download_button("안내문 .txt 다운로드", parent_note.encode("utf-8"),
                       file_name="parent_note.txt", mime="text/plain")

else:
    st.info("왼쪽에서 PDF를 업로드하면 요약 안내가 생성됩니다.")
