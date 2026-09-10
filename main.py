import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# [1. 데이터 불러오기 및 캐싱]
# ==========================================
# @st.cache_data를 사용해 데이터를 한 번만 불러오고 앱이 느려지지 않게 저장(캐싱)합니다.


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(빈 데이터)가 있는 행 제거
    df = df.dropna()

    # '기준일자' 컬럼을 날짜(datetime) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 '기준일자' 오름차순으로 정렬
    df = df.sort_values("기준일자")

    return df


# 데이터 로드
df = load_data()

# 페이지 기본 설정
st.set_page_config(page_title="영화 박스오피스 분석 앱", layout="wide")
st.title("🎬 영화 박스오피스 데이터 분석")

# ==========================================
# [3. 사이드바 - 영화 선택 기능]
# ==========================================
st.sidebar.header("🔍 검색 옵션")

# 영화별 최고 누적관객수를 기준으로 정렬하여 중복 없는 영화 목록 생성
sorted_movies = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바 드롭다운 메뉴 생성 (기본값: 가장 누적관객수가 높은 첫 번째 영화)
selected_movie = st.sidebar.selectbox("분석할 영화를 선택하세요:", sorted_movies)

# 선택한 영화 데이터만 필터링 (Tab 1, Tab 2 전용)
movie_df = df[df["영화명"] == selected_movie]


# ==========================================
# [4. 대시보드 구역 나누기 및 그래프 그리기]
# ==========================================
# 탭 구역 생성 (Tab 1: 개별 일별, Tab 2: 개별 누적, Tab 3: TOP5 비교, Tab 4: 시장 이동평균)
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 일별 관객수 추이",
        "🏔️ 누적 관객수 추이",
        "🏆 장기 흥행 TOP 5 비교",
        "📊 전체 관객수 & 7일 이동평균",
    ]
)

# [Tab 1: 선택 영화의 일별 관객수 선 그래프]
with tab1:
    st.subheader(f"[{selected_movie}] 일자별 관객수 변화")

    fig_line = px.line(
        movie_df,
        x="기준일자",
        y="해당일관객수",
        title=f"{selected_movie} - 일자별 관객수 추이",
        markers=True,
        labels={"기준일자": "날짜", "해당일관객수": "해당일 관객수(명)"},
    )
    fig_line.update_layout(hovermode="x unified")
    st.plotly_chart(fig_line, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        f"선택한 영화 [{selected_movie}]의 개봉 이후 일자별 관객수 증감 흐름과 전성기 시점을 확인할 수 있습니다."
    )

# [Tab 2: 선택 영화의 누적 관객수 영역 차트]
with tab2:
    st.subheader(f"[{selected_movie}] 기준일자별 누적 관객수 변화")

    fig_area = px.area(
        movie_df,
        x="기준일자",
        y="누적관객수",
        title=f"{selected_movie} - 누적 관객수 성장 추이",
        markers=True,
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
    )
    fig_area.update_layout(hovermode="x unified")
    st.plotly_chart(fig_area, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        f"선택한 영화 [{selected_movie}]의 상영 기간에 따른 전체 관객수의 누적 성장 곡선과 흥행 누적 속도를 시각적으로 확인할 수 있습니다."
    )

# [Tab 3: TOP 10 등재 20일 이상 영화 중 누적관객수 TOP 5 다중 선 그래프]
with tab3:
    st.subheader("🏆 장기 흥행(20일 이상 차트인) TOP 5 영화 추이 비교")

    movie_counts = df["영화명"].value_counts()
    long_run_movies = movie_counts[movie_counts >= 20].index

    top5_filtered_movies = (
        df[df["영화명"].isin(long_run_movies)]
        .groupby("영화명")["누적관객수"]
        .max()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    top5_filtered_df = df[df["영화명"].isin(top5_filtered_movies)]

    fig_multi = px.line(
        top5_filtered_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="20일 이상 차트인한 영화 중 누적관객수 TOP 5 흥행 비교",
        markers=True,
        labels={
            "기준일자": "날짜",
            "누적관객수": "누적 관객수(명)",
            "영화명": "영화 제목",
        },
    )

    fig_multi.update_layout(hovermode="x unified")
    st.plotly_chart(fig_multi, use_container_width=True)

    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "TOP 10 박스오피스에 최소 20일 이상 머무른 '장기 흥행' 영화 중 누적 관객수가 가장 높은 상위 5개 작품의 성과를 비교하여, "
        "단기 반짝 흥행이 아닌 지속적인 관객 유인력을 발휘한 대표작들의 성장 속도를 확인할 수 있습니다."
    )

# [Tab 4: 전체 TOP 10 일별 총 관객수 & 7일 이동평균선]
with tab4:
    st.subheader("📊 전체 박스오피스 일별 총 관객수 및 7일 이동평균 추이")

    # 1. 기준일자별로 TOP10 영화 전체의 해당일관객수 합계 산출
    daily_total = (
        df.groupby("기준일자")["해당일관객수"].sum().reset_index()
    )

    # 2. 7일 이동평균(Rolling Mean) 계산
    daily_total["7일_이동평균"] = (
        daily_total["해당일관객수"].rolling(window=7).mean()
    )

    # 3. Plotly graph_objects를 활용하여 세밀한 스타일 적용
    fig_ma = go.Figure()

    # (1) 일별 총 관객수 원본 선 (연한 색상, 투명도 조절)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["해당일관객수"],
            mode="lines",
            name="일별 총 관객수 (원본)",
            line=dict(color="rgba(100, 149, 237, 0.4)", width=1.5),  # 연한 파란색
        )
    )

    # (2) 7일 이동평균 선 (진한 색상, 두껍게)
    fig_ma.add_trace(
        go.Scatter(
            x=daily_total["기준일자"],
            y=daily_total["7일_이동평균"],
            mode="lines",
            name="7일 이동평균",
            line=dict(color="crimson", width=3),  # 진한 빨간색
        )
    )

    # 그래프 레이아웃 설정
    fig_ma.update_layout(
        title="전체 박스오피스 일별 총 관객수와 7일 이동평균선",
        xaxis_title="날짜",
        yaxis_title="총 관객수(명)",
        hovermode="x unified",
    )

    st.plotly_chart(fig_ma, use_container_width=True)

    # 그래프 설명 문구 자리
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** "
        "주말과 평일의 반복적인 관객수 변동(노이즈)을 평탄화한 '7일 이동평균선'을 통해, "
        "성수기/비수기 및 연휴 시즌 등 전체 극장가 영화 시장의 전반적인 흥행 흐름과 트렌드 변화를 더욱 명확하게 파악할 수 있습니다."
    )
