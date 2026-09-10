import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정 (타이틀 및 레이아웃)
st.set_page_config(
    page_title="박스오피스 데이터 분석 웹앱",
    layout="wide"
)

# App 제목
st.title("🎬 KOBIS 박스오피스 데이터 분석")
st.markdown("---")


# [1. 데이터 불러오기 및 캐싱]
# @st.cache_data를 사용하면 데이터를 매번 새로 다운로드하지 않고 메모리에 저장해두어 앱 속도가 빨라집니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)
    
    # [2. 날짜 전처리 및 정렬]
    # 결측치(값이 없는 데이터)가 있는 행을 삭제합니다.
    df = df.dropna()
    
    # "기준일자" 컬럼을 문자열에서 날짜(datetime) 형식으로 변환합니다.
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    
    # 데이터를 기준일자 순서대로 오름차순 정렬합니다.
    df = df.sort_values(by="기준일자")
    
    return df

# 데이터 로드 실행
df = load_data()


# [3. 영화 선택 기능]
# 데이터 내 영화별 최고 누적관객수를 구해 내림차순 정렬한 뒤 중복 없는 영화 목록을 만듭니다.
movie_audience = df.groupby("영화명")["누적관객수"].max().reset_index()
movie_audience_sorted = movie_audience.sort_values(by="누적관객수", ascending=False)
movie_list = movie_audience_sorted["영화명"].tolist()

# 사이드바에서 영화 선택
st.sidebar.header("🔍 설정")
selected_movie = st.sidebar.selectbox("분석할 영화를 선택하세요:", movie_list)


# [5. 기타 - 구역 나누기]
# 추후 다른 그래프를 추가하기 쉽도록 구역(Section)을 나누었습니다.
st.header("📈 1. 영화별 일별 관객수 추이")

# 사용자가 선택한 영화의 데이터만 추출
filtered_df = df[df["영화명"] == selected_movie]


# [4. 선그래프 그리기]
# Plotly를 사용하여 선택한 영화의 기준일자별 해당일관객수 변화 선그래프 생성
fig = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}' 기준일자별 일별 관객수 변화",
    labels={"기준일자": "날짜", "해당일관객수": "일별 관객수(명)"},
    markers=True  # 데이터 포인트에 점 표시
)

# 선그래프 스타일 조정 (선 색상 및 레이아웃)
fig.update_traces(line_color="#1f77b4")
fig.update_layout(hovermode="x unified")

# Streamlit 화면에 그래프 출력
st.plotly_chart(fig, use_container_width=True)

# [5. 기타 - 알 수 있는 것 한 문장 가이드]
st.info(f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 날짜 경과에 따른 일별 관객수 증감 흐름과 전성기 시점을 확인할 수 있습니다.")


# --- 추후 그래프 추가용 예시 구역 ---
st.markdown("---")
st.header("📊 2. 추가 분석 구역 (예정)")
st.caption("이 구역에는 추후 다른 형태의 시각화 그래프를 추가할 수 있습니다.")
