# 가재울 수련활동 안내 생성기

이 앱은 **2025학년도 1학년 수련활동 사전안전교육(배부용) PDF**를 업로드하면
- 일정 / 숙소 / 집합 시각·장소
- 학생 필수 준비물
- 반입 금지 물품
- 기본 준수사항
- 안전사고 예방 교육
- 3일간 프로그램 시간표
- 학급별 숙소 배정

을 자동으로 파싱하여 학생·학부모 안내용 요약을 제공합니다.

---

## 🚀 배포 방법
1. 이 저장소를 GitHub에 업로드
2. [Streamlit Cloud](https://share.streamlit.io) → **New app**
3. 저장소: `<username>/gajaeul_safety_guide`  
   브랜치: `main`  
   Main file: `app.py`
4. **Deploy** 클릭 후 URL 공유

---

## ⚙️ 커스터마이징
- `parser.py` 정규식을 학교 문서 포맷에 맞게 조정
- 반별 체크리스트 CSV 자동 분리 가능
- 시간표가 표 형태라면 `camelot`/`tabula` 활용 가능
