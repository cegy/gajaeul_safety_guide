# streamlit_app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import io
import textwrap

st.set_page_config(
    page_title="1학년 수련활동 안내 자료",
    page_icon="🏕️",
    layout="wide",
)

# -----------------------
# 기본 데이터 (문서에서 발췌·구조화)
# -----------------------
BASIC_INFO = {
    "일정": "2025-10-27(월) ~ 2025-10-29(수), 2박 3일",
    "숙소": "청포대썬셋수련원",
    "숙소 연락처": "041-674-9393",
    "집합 일시": "2025-10-27(월) 08:00",
    "집합 장소": "각 학급 교실",
    "버스 탑승": "08:30 (학교 인근)"
}

REQUIRED_ITEMS = [
    "개인 물병(텀블러 등, 정수기 이용 시 필요)",
    "편안한 운동화",
    "우천·저온 대비: 우산/우의, 방한복(바람막이 등)",
    "휴대전화 및 충전기",
    "자외선 차단제(선크림)",
    "세면도구(비누·치약·칫솔·샴푸 등)",
    "수건 충분히(제공되지 않음)",
    "여벌옷 충분히",
    "해변 체험용 복장(어두운 색 상·하의, 두꺼운 양말, 샌들/아쿠아슈즈 등)",
    "개인 상비약(멀미약·알레르기약·소화제·진통제·평소 복용약 등)",
    "필기도구",
    "그 외 개인용품"
]

BANNED_ITEMS = [
    "과다한 현금",
    "고가 전자기기·귀중품",
    "과도한 액세서리, 노출이 과한 의상",
    "흉기류(유사품 포함), 인화성 물질",
    "위험물(칼·가위·본드·부탄가스·라이터·폭죽 등)",
    "사행성 도구(화투·카드놀이 등)",
    "주류, (전자)담배 등 청소년 금지 약물",
]

STUDENT_RULES = [
    "일정표 시간 숙지·준수",
    "활동 중 휴대폰 사용 등 개인행동 자제, 프로그램 집중",
    "음주·흡연·도박 금지(위반 시 학교 규정에 따라 징계)",
    "인솔교사·진행자 지도사항 준수",
    "바른 언행·단정한 복장",
    "숙소 내 과도한 소음·난동 금지",
    "버스 탑승 즉시 안전벨트 착용, 좌석 이동 금지",
    "타인의 물건을 허락 없이 만지지 않기",
]

HEALTH_NOTES = [
    "신체 허약·복용약 학생은 사전에 교사에게 알림",
    "수련 중 대비하여 미리 병원 치료/약 처방",
    "개인 비상약 지참(멀미약 별도 제공 없음)",
    "활동하기 편한 복장·신발(슬리퍼·구두 지양)",
]

SAFETY_SECTIONS = {
    "도보 이동": [
        "신호 준수, 차량 완전 정지 확인 후 횡단",
        "도보 중 휴대폰·이어폰 금지",
        "인도 이용, 인도/차도 구분 없으면 가장자리 보행",
        "단체 이동 시 무리에서 이탈 금지, 교통법규 준수",
    ],
    "버스 이동": [
        "출발 전 안전벨트 이상 유무 확인 후 착용",
        "이동 중 자리 이동 금지, 창문 밖으로 신체 내밀지 않기",
        "멀미 시 승차 전 예방약 복용, 필요 시 환기",
        "버스 내 화재 시 큰 소리로 알리고 신속 대처",
        "문 탈출 곤란 시 비상망치로 유리 파괴 후 탈출",
    ],
    "숙소 안전": [
        "비상 대피요령·대피경로 확인",
        "시설물 안전 설치 여부 확인, 비품 원상 유지",
        "정해진 시간 이후 무단이탈 금지",
        "취침시간 준수, 분쟁 발생 시 즉시 교사에게 알림",
        "화재 시 젖은 수건으로 몸을 낮춰 대피, 소화기·소화전 위치·사용법 숙지",
    ],
    "식품 안전": [
        "체험 후·식사 전 비누로 손 씻기",
        "식품 알레르기 학생은 사전 신고 및 해당 음식 비섭취",
        "상온에서 상하기 쉬운 음식·간식 반입 지양",
        "유통기한·보관상태 불량 식품 섭취 금지",
        "식중독 의심(설사·복통·발열·두통)이 2명 이상 발생 시 즉시 교사에게 보고",
    ],
    "폭력·도난 예방": [
        "폭력·심한 장난 금지, 질서·배려",
        "불필요한 귀중품 지참 지양, 필요 시 교사에게 보관",
    ],
    "성폭력 예방": [
        "어두운·후미진 장소 출입 금지, 문단속 철저",
        "원치 않는 상황은 명확히 거절 의사표시",
        "피해 시 즉시 신뢰할 수 있는 어른/교사에게 신고",
        "피해 사실·경과를 육하원칙에 따라 기록",
    ],
    "학교폭력 유형(요약)": [
        "신체폭력(상해·폭행·감금·약취·유인·과한 장난 등)",
        "언어폭력(명예훼손·모욕·협박 등)",
        "금품갈취(공갈·상습적 대여 미반환 등)",
        "강요(빵·와이파이 셔틀, 대행·심부름 강요 등)",
        "따돌림(의도적·반복적 배제, 조롱·골탕·비웃기 등)",
        "성희롱·성폭력(강제 성행위·신체 접촉·성적 발언 등)",
        "사이버폭력(모욕·허위정보 유포·협박·따돌림·영상유포 등)",
    ],
}

# 일정표
schedule_data = [
    {"일자": "10/27(월)", "시간대": "08:00~", "활동": "집합(각 교실), 버스 탑승 08:30"},
    {"일자": "10/27(월)", "시간대": "점심", "활동": "수련원 도착 / 점심"},
    {"일자": "10/27(월)", "시간대": "오후", "활동": "숙소배정·생활안내(소방·안전), 해변 체험(맛조개 잡기·트레킹)"},
    {"일자": "10/27(월)", "시간대": "저녁~밤", "활동": "레크리에이션·장기자랑·캠프파이어"},
    {"일자": "10/28(화)", "시간대": "오전", "활동": "기상·아침 식사, 명랑운동회 / 사진 미션 페스티벌"},
    {"일자": "10/28(화)", "시간대": "오후", "활동": "Smart Lan Media Balance Quiz Show, 해솔길 트레킹(우천 시 실내 대체)"},
    {"일자": "10/28(화)", "시간대": "저녁~밤", "활동": "저녁, 취침"},
    {"일자": "10/29(수)", "시간대": "오전~점심", "활동": "기상·아침, 소감문 작성, 점심 후 학교로 출발"},
]
schedule_df = pd.DataFrame(schedule_data)

# 숙소 배정 (표시는 간략/원문 반영)
dorm_rows = [
    ("1반", "벨 201(남6), 202(남6)", "오션B 201(여3), 202(여8), 205(여3)"),
    ("2반", "벨 203(남6)", "오션B 101(여5), 102(여5), 103(여5)"),
    ("3반", "벨 204(남5), 205(남5)", "오션C 101(여6), 102(여5)"),
    ("4반", "필드 105(남4), 벨 206(남5)", "오션C 103(여4), 201(여3)"),
    ("5반", "필드 106(남4), 벨 207(남5)", "오션C 105(여5), 202(여7)"),
    ("6반", "벨 208(남6), 209(남5)", "오션D 101(여6), 102(여5), 103(여5)"),
    ("7반", "벨 210(남6), 211(남6)", "오션D 105(여6), 201(여3), 205(여3)"),
    ("8반", "오션A 201(남4)", "필드 101(여1)"),
]
dorm_df = pd.DataFrame(dorm_rows, columns=["반", "남학생 객실", "여학생 객실"])


# -----------------------
# 유틸: 파일 다운로드 컨텐츠 생성
# -----------------------
def to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8-sig")

def markdown_student_handout() -> str:
    md = f"""# 1학년 수련활동 안내(학생 배부용)

**일정**: {BASIC_INFO['일정']}  
**숙소**: {BASIC_INFO['숙소']} (☎ {BASIC_INFO['숙소 연락처']})  
**집합**: {BASIC_INFO['집합 일시']} / {BASIC_INFO['집합 장소']}  
**버스 탑승**: {BASIC_INFO['버스 탑승']}

---

## 준비물 (필수)
- """ + "\n- ".join(REQUIRED_ITEMS) + """

## 반입 금지 물품
- """ + "\n- ".join(BANNED_ITEMS) + """

## 학생 준수사항
- """ + "\n- ".join(STUDENT_RULES) + """

## 건강 관리 유의
- """ + "\n- ".join(HEALTH_NOTES) + """

## 안전사고 예방 요약
""" 
    for sec, items in SAFETY_SECTIONS.items():
        md += f"\n### {sec}\n- " + "\n- ".join(items) + "\n"
    md += "\n---\n※ 우천·현지 사정에 따라 일부 프로그램은 실내 활동으로 대체될 수 있습니다.\n"
    return md

# -----------------------
# 사이드바
# -----------------------
with st.sidebar:
    st.title("🏕️ 수련활동 대시보드")
    st.caption("2025학년도 1학년 수련활동 안내")
    page = st.radio("메뉴", ["개요", "체크리스트", "일정표", "안전수칙", "숙소 배정", "다운로드"])
    st.divider()
    st.info("날짜: 2025-10-27(월) ~ 10-29(수)\n장소: 청포대썬셋수련원")

# -----------------------
# 상단 헤더
# -----------------------
st.markdown(
    """
    <style>
      .big-title {font-size: 30px; font-weight: 800;}
      .sub {color:#666;}
      .bullet {line-height:1.7;}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="big-title">2025학년도 1학년 수련활동 안내</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">학생·보호자·교사용 안내를 한 곳에서 확인하세요.</div>', unsafe_allow_html=True)
st.divider()

# -----------------------
# 페이지별 렌더
# -----------------------
if page == "개요":
    col1, col2, col3 = st.columns([1.1, 1, 1])
    with col1:
        st.subheader("기본 계획")
        st.write(f"**일정:** {BASIC_INFO['일정']}")
        st.write(f"**숙소:** {BASIC_INFO['숙소']} (☎ {BASIC_INFO['숙소 연락처']})")
        st.write(f"**집합:** {BASIC_INFO['집합 일시']} · {BASIC_INFO['집합 장소']}")
        st.write(f"**버스 탑승:** {BASIC_INFO['버스 탑승']}")
        st.warning("날씨·현지 사정에 따라 일부 프로그램은 변경될 수 있습니다.")
    with col2:
        st.subheader("필수 준비물")
        st.markdown("<div class='bullet'>" + "<br>".join(f"• {x}" for x in REQUIRED_ITEMS) + "</div>", unsafe_allow_html=True)
    with col3:
        st.subheader("반입 금지 물품")
        st.markdown("<div class='bullet'>" + "<br>".join(f"• {x}" for x in BANNED_ITEMS) + "</div>", unsafe_allow_html=True)

elif page == "체크리스트":
    st.subheader("개인 준비물 체크리스트")
    if "checklist" not in st.session_state:
        st.session_state.checklist = {item: False for item in REQUIRED_ITEMS}

    cols = st.columns(2)
    for i, item in enumerate(REQUIRED_ITEMS):
        with cols[i % 2]:
            st.session_state.checklist[item] = st.checkbox(item, value=st.session_state.checklist[item])

    done_count = sum(1 for v in st.session_state.checklist.values() if v)
    st.progress(done_count / len(REQUIRED_ITEMS))
    st.caption(f"완료: {done_count} / {len(REQUIRED_ITEMS)}")

    # 다운로드(완료 항목만)
    checked = [k for k, v in st.session_state.checklist.items() if v]
    md = "# 개인 준비물 체크리스트(완료)\n\n" + "\n".join(f"- [x] {x}" for x in checked)
    st.download_button("완료 항목 내보내기 (Markdown)", md.encode("utf-8"), file_name="checklist_done.md")

elif page == "일정표":
    st.subheader("주요 일정표")
    st.dataframe(schedule_df, use_container_width=True)
    st.download_button("일정표 다운로드 (CSV)", to_csv_bytes(schedule_df), file_name="schedule.csv")

    st.info("※ 우천 시 실내 대체 프로그램: 도전 골든벨, 창의적 도미노, 도전 99초, 공동체 활동, 전지신문 만들기")

elif page == "안전수칙":
    st.subheader("안전사고 예방 교육")
    tabs = st.tabs(list(SAFETY_SECTIONS.keys()))
    for tab, (sec, items) in zip(tabs, SAFETY_SECTIONS.items()):
        with tab:
            st.markdown("<div class='bullet'>" + "<br>".join(f"• {x}" for x in items) + "</div>", unsafe_allow_html=True)

    st.warning("학교폭력·성폭력 등 위기 상황 발생 시 즉시 인솔교사에게 신고하세요.")

elif page == "숙소 배정":
    st.subheader("학생 숙소 배정(요약)")
    st.dataframe(dorm_df, use_container_width=True, height=380)
    st.download_button("숙소 배정표 다운로드 (CSV)", to_csv_bytes(dorm_df), file_name="dorm_assignment.csv")

    # 간단한 검색
    st.divider()
    q = st.text_input("반/객실 검색", placeholder="예: 3반, 오션D, 벨 201 ...")
    if q:
        mask = dorm_df.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1)
        st.dataframe(dorm_df[mask], use_container_width=True)

elif page == "다운로드":
    st.subheader("배포용 파일 내려받기")
    # 학생 배부용 MD
    md_text = markdown_student_handout()
    st.download_button("학생 안내문 (Markdown)", md_text.encode("utf-8"), file_name="학생_안내문.md")

    # 일정/숙소 CSV 묶음 zip (메모리 압축)
    import zipfile
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("schedule.csv", schedule_df.to_csv(index=False))
        zf.writestr("dorm_assignment.csv", dorm_df.to_csv(index=False))
        zf.writestr("student_handout.md", md_text)
    st.download_button("일정·숙소·안내문 묶음(ZIP)", data=zip_buf.getvalue(), file_name="수련활동_배포자료.zip")

# 푸터
st.divider()
st.caption("© 2025 수련활동 안내 자료 • 본 대시보드는 배부용 문서를 바탕으로 구성되었습니다.")
