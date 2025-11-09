import streamlit as st
import streamlit as st
import pandas as pd
# 페이지 기본 설정
st.set_page_config(page_title="태양광 발전량 대시보드", page_icon="☀️", layout="wide")

st.title("☀️ 태양광 발전량 대시보드")
st.write("탭 구조 테스트용 기본 버전입니다.")

# 탭 3개 구성
tab1, tab2, tab3 = st.tabs(["🔴 실시간 발전량", "📈 발전량 예측 비교", "🌤️ 날씨 현황"])

with tab1:
    st.subheader("🔴 실시간 발전량 탭")
    st.write("여기는 실시간 발전량 데이터를 표시할 영역입니다.")

with tab2:
    st.subheader("📈 발전량 예측 비교 탭")
    st.write("여기는 예측값과 실측값을 비교하는 그래프가 들어갈 자리입니다.")

with tab3:
    st.subheader("🌤️ 날씨 현황 (Google Drive CSV 연동)")

    # Google Drive 파일 ID (예: https://drive.google.com/file/d/📁ID/view?usp=sharing)
    file_id = "1mSRBAQwTWhIPK9XMJmhTr7dw0TFCHX7E"   # 👉 네 파일 ID로 교체
    url = f"https://drive.google.com/uc?id={file_id}"

    try:
        # CSV 불러오기
        df = pd.read_csv(url)

        # 날짜 변환
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])

        # Plotly 그래프
        if {"datetime", "temperature", "humidity"}.issubset(df.columns):
            fig = px.line(
                df,
                x="datetime",
                y=["temperature", "humidity"],
                labels={"value": "값", "variable": "항목", "datetime": "시간"},
                title="📈 온도 & 습도 변화 추이",
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ 'datetime', 'temperature', 'humidity' 열이 필요합니다.")

    except Exception as e:
        st.error(f"CSV 불러오기 실패: {e}")
