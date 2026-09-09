import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="영화 관객수 분석 앱",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 영화 관객수 분석 웹앱")
st.markdown("KOBIS 박스오피스 데이터를 기반으로 영화별 관객수 변화를 분석합니다.")

# -----------------------------------------------------------------------------
# [1. 데이터 불러오기]
# st.cache_data를 사용하여 한 번 불러온 데이터를 저장(캐싱)하고 재사용합니다.
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    data = pd.read_csv(url)
    
    # [2. 날짜 전처리]
    # '기준일자' 컬럼을 datetime 형식으로 변환합니다.
    data["기준일자"] = pd.to_datetime(data["기준일자"])
    
    # 전체 데이터를 기준일자 순서대로 정렬합니다.
    data = data.sort_values(by="기준일자").reset_index(drop=True)
    
    return data

# 데이터 로드
df = load_data()

# -----------------------------------------------------------------------------
# 사이드바: [3. 영화 선택 기능]
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 옵션 선택")

# '영화명' 컬럼에서 중복 없이 영화 목록을 추출합니다.
movie_list = sorted(df["영화명"].unique())

# 사용자가 목록에서 영화를 선택할 수 있는 드롭다운(selectbox)을 생성합니다.
selected_movie = st.sidebar.selectbox("영화를 선택하세요:", movie_list)

# 선택한 영화 데이터만 필터링합니다.
filtered_df = df[df["영화명"] == selected_movie].copy()

# -----------------------------------------------------------------------------
# [탭 구역 생성]
# 1탭: 일별 관객수 추이 (선그래프)
# 2탭: 누적 관객수 변화 (영역차트)
# 3탭: 추가 분석 구역 (예정)
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📈 선택 영화 관객수 추이", "🌊 누적 관객수 변화 (영역차트)", "➕ 추가 분석 구역 (예정)"])

# -----------------------------------------------------------------------------
# 첫 번째 그래프: [선그래프]
# -----------------------------------------------------------------------------
with tab1:
    st.subheader(f"'{selected_movie}' 날짜별 관객수 변화")
    
    if not filtered_df.empty:
        # Plotly를 사용하여 날짜별('기준일자') 해당일관객수 변화를 선그래프로 그립니다.
        fig1 = px.line(
            filtered_df,
            x="기준일자",
            y="해당일관객수",
            title=f"[{selected_movie}] 일별 관객수 추이",
            labels={"기준일자": "날짜", "해당일관객수": "관객수 (명)"},
            markers=True  # 데이터 점 표시
        )
        
        # 그래프 레이아웃 스타일 설정
        fig1.update_layout(
            hovermode="x unified",
            xaxis_title="기준일자",
            yaxis_title="해당일관객수"
        )
        
        # Streamlit에 Plotly 그래프 표시
        st.plotly_chart(fig1, use_container_width=True)
        
        # '이 그래프로 알 수 있는 것' 안내문
        st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}' 영화는 특정 날짜에 관객수가 가장 높았으며, 개봉/상영 기간 동안 일별 흥행 추이를 확인할 수 있습니다.")
    else:
        st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

# -----------------------------------------------------------------------------
# 두 번째 그래프: [영역차트 - 누적 관객수]
# -----------------------------------------------------------------------------
with tab2:
    st.subheader(f"'{selected_movie}' 기준일자별 누적 관객수 변화")
    
    if not filtered_df.empty:
        # Plotly를 사용하여 날짜별('기준일자') 누적관객수 변화를 영역차트(area chart)로 그립니다.
        fig2 = px.area(
            filtered_df,
            x="기준일자",
            y="누적관객수",
            title=f"[{selected_movie}] 누적 관객수 변화 추이",
            labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)"}
        )
        
        # 그래프 레이아웃 스타일 설정
        fig2.update_layout(
            hovermode="x unified",
            xaxis_title="기준일자",
            yaxis_title="누적관객수"
        )
        
        # Streamlit에 Plotly 영역차트 표시
        st.plotly_chart(fig2, use_container_width=True)
        
        # '이 그래프로 알 수 있는 것' 안내문
        st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}' 영화의 상영 기간 동안 누적 관객수가 어떻게 지속적으로 증가했는지 전체적인 흥행 스케일을 확인할 수 있습니다.")
    else:
        st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

# -----------------------------------------------------------------------------
# 세 번째 탭: [추가 예정 구역]
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📊 추가 그래프 영역")
    st.write("앞으로 이 구역에 추가적인 분석 그래프나 통계 정보를 확장할 수 있습니다.")
    st.info("💡 **이 그래프로 알 수 있는 것:** (추가 예정 그래프에 대한 설명이 들어갈 자리입니다.)")
