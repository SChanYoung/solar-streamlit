import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import random


# Google Drive 파일 ID (예: https://drive.google.com/file/d/📁ID/view?usp=sharing)
# 페이지 기본 설정
st.set_page_config(page_title="태양광 발전량 대시보드", page_icon="☀️", layout="wide")

st.title("태양광 발전량 대시보드")
# st.write("나중에 정함")

# 탭 3개 구성
tab1, tab2, tab3 = st.tabs(["🔴 실시간 발전량 비교", "📈 발전량 예측", "🌤️ 기상 현황"])


with tab2:
    st.subheader("📈 발전량 예측")
    file_id = "1oXtwoKlvHTLvUMCG-ujigpiKw4w0kLnC"  # 👉 교체하세요
    url = f"https://drive.google.com/uc?id={file_id}"
    
    try:
        df = pd.read_csv(url)
    
        # 🔧 실제 CSV 열 이름에 맞게 변경
        df.rename(columns={
            "datetime": "datetime",     # 시간 열 이름에 맞게 변경
            "predicted_pv": "predicted"    # 예측 발전량 열 이름에 맞게 변경
        }, inplace=True)
    
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    
        # === 날짜 범위 선택 ===
        available_dates = sorted(df["datetime"].dt.date.unique())
        default_range = [min(available_dates), max(available_dates)]
    
        selected_range = st.date_input(
            "날짜 범위를 선택하세요",
            value=default_range,
            min_value=min(available_dates),
            max_value=max(available_dates)
        )
    
        # ✅ 하루 or 범위 모두 지원
        if isinstance(selected_range, tuple):
            start_date, end_date = selected_range
        elif isinstance(selected_range, list):
            start_date, end_date = selected_range[0], selected_range[-1]
        else:
            start_date = end_date = selected_range
    
        # === 데이터 필터링 ===
        mask = (df["datetime"].dt.date >= start_date) & (df["datetime"].dt.date <= end_date)
        filtered = df.loc[mask]
    
        if filtered.empty:
            st.warning("⚠️ 선택한 기간에 해당하는 예측 데이터가 없습니다.")
        else:
            # === 그래프 ===
            fig = px.line(
                filtered,
                x="datetime",
                y="predicted",
                labels={"datetime": "시간", "predicted_pv": ""},  # ← y축 텍스트 제거
                color_discrete_sequence=["orange"]
            )
            
            # 그래프 선 스타일 설정
            fig.update_traces(mode="lines", line=dict(width=2.2))
            
            # 그래프 제목, 폰트, 위치 설정
            fig.update_layout(
                xaxis_title=" ",
                yaxis_title="발전량 (W)",
                # yaxis_title=None,   # ← y축 제목 완전히 제거
                template="plotly_white",
                margin=dict(l=40, r=40, t=50, b=40)
            )
            
            
            
            st.plotly_chart(fig, use_container_width=True)

    
    except Exception as e:
        st.error(f"CSV 불러오기 실패: {e}")
with tab3:
    st.subheader("🌤️ 기상 현황")

    file_id = "1mSRBAQwTWhIPK9XMJmhTr7dw0TFCHX7E"   # 날씨 파일 ID로 바꾸면됨
    url = f"https://drive.google.com/uc?id={file_id}"

    try:
        # CSV 불러오기
        df = pd.read_csv(url)

             # 날짜 변환
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"])
    
        # 필요한 컬럼 확인
        if {"datetime", "ghi", "cloud_opacity", "air_temp"}.issubset(df.columns):
            # Plotly 그래프 객체 생성
            fig = go.Figure()
    
            # (1) GHI (왼쪽 y축)
            fig.add_trace(go.Scatter(
                x=df["datetime"],
                y=df["ghi"],
                mode="lines",  # ✅ 점(marker) 제거
                name="GHI (W/m²)",
                line=dict(color="orange", width=2)
            ))
    
            # (2) Cloud opacity (오른쪽 y축)
            fig.add_trace(go.Scatter(
                x=df["datetime"],
                y=df["cloud_opacity"],
                mode="lines",
                name="Cloud Opacity (%)",
                line=dict(color="blue", width=2, dash="dot"),
                yaxis="y2"  # ✅ 두 번째 y축 사용
            ))
    
            # (3) 레이아웃 설정
            fig.update_layout(            
                xaxis=dict(title=" "),
                yaxis=dict(title="GHI (W/m²)", side="left", showgrid=True),
                yaxis2=dict(
                    title="Cloud opacity (%)",
                    overlaying="y",  # ✅ GHI 축 위에 겹쳐서 표시
                    side="right",
                    range=[0, 100],  # ✅ 구름량은 0~100으로 고정
                    showgrid=False
                ),
                legend=dict(x=0.02, y=0.95),
                template="plotly_white",
                margin=dict(l=50, r=50, t=60, b=40)
            )

             # ✅ air_temp의 최근 유효값만 표시
            valid_temps = df["air_temp"].dropna()
            if not valid_temps.empty:
                latest_temp = valid_temps.iloc[-1]
                fig.add_annotation(
                    text=f"Temperature: {latest_temp:.1f} °C",
                    xref="paper", yref="paper",
                    x=0.01, y=1.05,
                    showarrow=False,
                    font=dict(size=14, color="crimson", family="Arial Black")
                )
            else:
                fig.add_annotation(
                    text="🌡️ 현재기온: 데이터 없음",
                    xref="paper", yref="paper",
                    x=0.01, y=1.05,
                    showarrow=False,
                    font=dict(size=14, color="gray")
                )
                
            # Streamlit 표시
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ 'datetime', 'ghi', 'cloud_opacity' 열이 필요합니다.")
    
    except Exception as e:
        st.error(f"CSV 불러오기 실패: {e}")

with tab1:
    st.subheader("🔴 실시간 발전량 비교")
    

    # === 예측 CSV ===
    pred_file_id = "1BgS87RxvACPnHNnVOw5nXFdRiegsve43"
    pred_url = f"https://drive.google.com/uc?id={pred_file_id}"
    pred_df = pd.read_csv(pred_url, encoding='utf-8')
    pred_df["datetime"] = pd.to_datetime(pred_df["datetime"])
    pred_df.set_index("datetime", inplace=True)

    # === 실시간 CSV ===
    live_file_id = "1vydHZnOWjXRni2FwQ-mLwy3BQm1-I6Ui"
    live_url = f"https://drive.google.com/uc?id={live_file_id}"

    # === 세션 상태 저장 ===
    if "paused" not in st.session_state:
        st.session_state.paused = False

    # 일시정지/재시작 버튼
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.session_state.paused:
            if st.button("▶ 재시작"):
                st.session_state.paused = False
        else:
            if st.button("⏸ 일시정지"):
                st.session_state.paused = True

    # === 그래프 기본 구성 ===
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pred_df.index,
        y=pred_df["predicted_pv"],
        mode="lines",
        name="예측 발전량 (5분 단위)",
        line=dict(color="orange", dash="dot", width=2)
    ))
    fig.add_trace(go.Scatter(
        x=[], y=[],
        mode="lines+markers",
        name="실시간 평균 발전량 (5분 단위)",
        line=dict(color="royalblue", width=3)
    ))
    fig.update_layout(
        template="plotly_white",
        yaxis_title="발전량 (W)",
        legend=dict(yanchor="top", y=1.1, xanchor="left", x=0)
    )

    chart = st.empty()

    # === 5분 주기 자동 업데이트 루프 ===
    while True:
        if not st.session_state.paused:
            try:
                live_df = pd.read_csv(live_url, encoding="utf-8")
                if not live_df.empty:
                    live_df["Timestamp"] = pd.to_datetime(live_df["Timestamp"])
                    live_df.set_index("Timestamp", inplace=True)

                    # 🔹 5분 단위 평균
                    resampled = live_df["PV_P (W)"].resample("15S").mean().reset_index()

                    # 그래프 갱신
                    fig.data[1].x = resampled["Timestamp"]
                    fig.data[1].y = resampled["PV_P (W)"]
                    chart.plotly_chart(fig, use_container_width=True, key=f"chart_{random.randint(0,99999)}")
                    
            except Exception as e:
                st.warning(f"⚠️ 데이터 오류: {e}")
        else:
            st.info("⏸ 데이터 갱신이 일시정지되었습니다.")
        
        time.sleep(15)  # 5분 단위 주기


