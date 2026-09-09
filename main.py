import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정 (넓은 화면 레이아웃 적용)
st.set_page_config(page_title="영화 박스오피스 분석 앱", layout="wide")


# [1. 데이터 불러오기]
# @st.cache_data를 사용해 데이터를 한 번만 로드하고 캐시(저장소)에 보관합니다.
# 이렇게 하면 매번 클릭할 때마다 인터넷에서 데이터를 다시 받지 않아 앱이 빨라집니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 데이터 전처리]
    # 결측치(빈 데이터)가 하나라도 있는 행은 삭제합니다.
    df = df.dropna()

    # '기준일자'와 '개봉일' 컬럼을 문자열에서 날짜(datetime) 형식으로 변환합니다.
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    df["개봉일"] = pd.to_datetime(df["개봉일"])

    # 전체 데이터를 기준일자 순서대로 오름차순 정렬합니다.
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드 실행
df = load_data()

# 웹앱 상단 제목 표시
st.title("🎬 박스오피스 영화 데이터 분석")

# [3. 영화 선택 기능]
# '영화명' 컬럼에서 중복을 제거한 영화 목록을 뽑아냅니다.
movie_list = df["영화명"].unique()

# 사이드바에 드롭다운 메뉴(셀렉트박스)를 만들어 영화를 선택하게 합니다.
selected_movie = st.sidebar.selectbox("분석할 영화를 선택하세요", movie_list)


# [4. 데이터 필터링]
# 사용자가 선택한 영화의 데이터만 추출합니다.
selected_df = df[df["영화명"] == selected_movie]

# 개봉일 이후의 데이터만 필터링합니다 (기준일자 >= 개봉일).
filtered_df = selected_df[selected_df["기준일자"] >= selected_df["개봉일"]]


# [5. 시각화 구역 나누기 및 그래프 그리기]
# 구분선 추가
st.divider()

# 구역 1: 개봉 후 관객수 변화 그래프
with st.container():
    st.subheader(f"📈 [{selected_movie}] 개봉 후 관객수 변화")

    # Plotly를 이용한 선그래프 생성
    fig = px.line(
        filtered_df,
        x="기준일자",
        y="해당일관객수",
        title=f"{selected_movie} - 일별 관객수 추이",
        labels={"기준일자": "날짜", "해당일관객수": "일별 관객수(명)"},
        markers=True,  # 그래프 선 위에 데이터 점을 표시
    )

    # Streamlit 화면에 Plotly 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 그래프 하단 설명 문구 자리
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 개봉 이후 일자별 관객수의 증감 흐름과 가장 많은 관객이 방문한 피크 시점을 확인할 수 있습니다."
    )

# 구역 2: 추후 다른 그래프를 추가할 여분 구역
st.divider()
with st.container():
    st.subheader("📊 추가 분석 구역 (예정)")
    st.caption("이 구역에 추후 새로운 시각화 그래프를 추가할 수 있습니다.")
