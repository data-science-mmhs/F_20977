import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# 앱 기본 설정 및 페이지 제목
# ==========================================
st.set_page_config(page_title="영화 박스오피스 분석 대시보드", layout="wide")
st.title("🎬 영화 박스오피스 관객수 분석")

# ==========================================
# [1 & 2] 데이터 불러오기 및 전처리 (캐싱 적용)
# ==========================================
# @st.cache_data 데코레이터를 사용하면 데이터를 처음 한 번만 불러오고
# 그 이후로는 저장해 둔(캐시된) 데이터를 사용하여 앱이 느려지지 않습니다.


@st.cache_data
def load_and_preprocess_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"

    # 1. CSV 데이터 불러오기
    df = pd.read_csv(url)

    # 2. 결측치(빈 값)가 포함된 행 삭제
    df = df.dropna()

    # 3. '기준일자' 컬럼을 datetime 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 4. '기준일자' 순서대로 데이터 정렬
    df = df.sort_values("기준일자")

    # 5. '누적관객수' 컬럼 처리 (데이터셋에 누적관객수가 없으면 영화별 누적합 계산)
    if "누적관객수" not in df.columns:
        df["누적관객수"] = df.groupby("영화명")["해당일관객수"].cumsum()

    return df


# 함수를 실행하여 데이터 프레임 준비
df = load_and_preprocess_data()

# ==========================================
# [3] 사이드바: 영화 선택 기능
# ==========================================
st.sidebar.header("🔍 검색 및 필터")

# '영화명' 컬럼에서 중복을 제거한 고유 목록 추출
movie_list = df["영화명"].unique()

# 사용자에게 영화를 선택할 수 있는 드롭다운 메뉴 제공
selected_movie = st.sidebar.selectbox("영화를 선택하세요:", movie_list)

# 선택한 영화에 해당하는 데이터만 필터링
movie_df = df[df["영화명"] == selected_movie].copy()

# ==========================================
# [구역 1] 선택한 영화 - 일별 관객수 추이 (선 그래프)
# ==========================================
st.header(f"📊 [{selected_movie}] 일별 관객수 추이")

# x축: 기준일자, y축: 해당일관객수
fig_line = px.line(
    movie_df,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} - 일별 관객수 변화",
    markers=True,  # 데이터 지점에 점 표시
    labels={"기준일자": "날짜", "해당일관객수": "관객수(명)"},
)

# 그래프 화면에 출력
st.plotly_chart(fig_line, use_container_width=True)

# 그래프 해석 문구 자리
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** {selected_movie}의 개봉 후 일자별 관객수 증감 추이와 최고 흥행 시점을 확인할 수 있습니다."
)

st.divider()

# ==========================================
# [구역 2] 선택한 영화 - 누적 관객수 추이 (영역 차트)
# ==========================================
st.header(f"📈 [{selected_movie}] 누적 관객수 추이")

# Plotly 영역 차트(area chart) 생성
fig_area = px.area(
    movie_df,
    x="기준일자",
    y="누적관객수",
    title=f"{selected_movie} - 기준일자별 누적 관객수 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수(명)"},
)

# 그래프 화면에 출력
st.plotly_chart(fig_area, use_container_width=True)

# 영역 차트 해석 문구 자리
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 시간 흐름에 따라 {selected_movie}의 전체 누적 관객수가 얼마나 빠르게 쌓여가는지 흥행 규모의 성장 곡선을 확인할 수 있습니다."
)

st.divider()

# ==========================================
# [구역 3] 20일 이상 장기 흥행 TOP 5 영화 비교 (다중 선 그래프)
# ==========================================
st.header("🏆 20일 이상 상위권 유지 영화 TOP 5 누적 관객수 비교")

# 1. 영화별 등장 일수(TOP 10 진입 횟수) 계산
movie_counts = df["영화명"].value_counts()

# 2. 등장 일수가 20일 이상인 영화 목록 필터링
over_20days_movies = movie_counts[movie_counts >= 20].index

# 3. 20일 이상 등장한 영화의 데이터만 추출
filtered_df = df[df["영화명"].isin(over_20days_movies)]

# 4. 해당 영화들 중 최고 누적관객수 기준 상위 5개 영화 선정
top5_long_run_movies = (
    filtered_df.groupby("영화명")["누적관객수"].max().nlargest(5).index.tolist()
)

# 5. 최종 상위 5개 영화 데이터만 필터링
top5_df = df[df["영화명"].isin(top5_long_run_movies)]

# 6. Plotly 다중 선 그래프 생성
fig_multi_line = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화별로 다른 색상 및 범례 자동 생성
    title="20일 이상 장기 흥행 TOP 5 영화의 기준일자별 누적 관객수 추이",
    labels={
        "기준일자": "날짜",
        "누적관객수": "누적 관객수(명)",
        "영화명": "영화 제목",
    },
)

# 그래프 화면에 출력
st.plotly_chart(fig_multi_line, use_container_width=True)

# 다중 선 그래프 해석 문구 자리
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** TOP 10에 20일 이상 오랜 기간 이름을 올린 장기 흥행작 중 관객수가 가장 높았던 상위 5개 영화({', '.join(top5_long_run_movies)})의 흥행 페이스와 누적 성과를 비교할 수 있습니다."
)

st.divider()

# ==========================================
# [구역 4] 전체 TOP 10 관객수 합계 및 7일 이동평균선
# ==========================================
st.header("📉 전체 박스오피스 일별 총 관객수 및 7일 이동평균 추이")

# 1. 기준일자별로 모든 TOP10 영화의 해당일관객수 합계 계산
daily_total = (
    df.groupby("기준일자")["해당일관객수"].sum().reset_index()
)

# 2. 7일 이동평균(Rolling Mean) 계산
daily_total["7일이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7).mean()
)

# 3. Plotly graph_objects를 이용해 원본 선과 이동평균 선 함께 그리기
fig_ma = go.Figure()

# (1) 원본 일별 총관객수 (연한 반투명 선)
fig_ma.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 총 관객수",
        line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),  # 연한 회색
    )
)

# (2) 7일 이동평균 (진한 선)
fig_ma.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#FF4B4B", width=3),  # 진한 빨간색
    )
)

# 레이아웃 설정
fig_ma.update_layout(
    title="기준일자별 TOP 10 영화 총 관객수 및 7일 이동평균선",
    xaxis_title="날짜",
    yaxis_title="관객수(명)",
    hovermode="x unified",  # 마우스 호버 시 동일 날짜 데이터 통합 표시
)

# 그래프 화면에 출력
st.plotly_chart(fig_ma, use_container_width=True)

# 이동평균선 해석 문구 자리
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 요일별 관객수 변동(주말 편차 등) 노이즈를 완화하여, 전체 극장가의 성수기/비수기 시즌성 흐름과 전반적인 시장 흥행 추세를 한눈에 파악할 수 있습니다."
)

st.divider()

# ==========================================
# [구역 5] 월별 박스오피스 총 관객수 (막대 그래프)
# ==========================================
st.header("🗓️ 월별 박스오피스 총 관객수 비교")

# 1. '기준일자'에서 연-월('YYYY-MM') 정보를 추출하여 새 컬럼 생성
daily_total["연월"] = daily_total["기준일자"].dt.to_period("M").astype(str)

# 2. 월 단위(연월)로 재그룹화하여 해당일관객수 합산
monthly_total = (
    daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
)

# 3. Plotly 막대 그래프(Bar Chart) 생성
fig_bar = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 극장가 총 관객수 (TOP 10 영화 합계)",
    text_auto=".2s",  # 막대 위에 축약된 숫자로 관객수 표시 (예: 1.2M)
    labels={"연월": "년-월", "해당일관객수": "총 관객수(명)"},
)

# 막대 색상 및 레이아웃 커스텀
fig_bar.update_traces(marker_color="#4F8BF9")
fig_bar.update_layout(xaxis_type="category")  # x축을 연-월 범주형으로 설정

# 그래프 화면에 출력
st.plotly_chart(fig_bar, use_container_width=True)

# 월별 막대 그래프 해석 문구 자리
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 월 단위 전체 관객 수치 비교를 통해 연중 극장가가 가장 붐볐던 최성수기 월과 상대적으로 침체되었던 비수기 월을 한눈에 식별할 수 있습니다."
)

st.divider()

# ==========================================
# [구역 6] 월 × 요일별 관객수 분포 (히트맵)
# ==========================================
st.header("🗓️ 월 × 요일별 관객수 캘린더 히트맵")

# 1. '기준일자'에서 월(1~12) 및 요일명 추출
daily_total["월"] = daily_total["기준일자"].dt.month.astype(
    str
) + "월"  # 예: '1월', '2월'
daily_total["요일_코드"] = daily_total[
    "기준일자"
].dt.dayofweek  # 0: 월요일, ..., 6: 일요일

# 요일명을 월~일 순서로 매핑
weekday_map = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일",
}
daily_total["요일"] = daily_total["요일_코드"].map(weekday_map)

# 2. 월과 요일로 그룹화하여 일관객수 합계 계산
heatmap_df = (
    daily_total.groupby(["월", "요일", "요일_코드"])["해당일관객수"]
    .sum()
    .reset_index()
)

# 3. 피벗 테이블(Pivot Table) 생성 (행: 요일, 열: 월)
pivot_heatmap = heatmap_df.pivot(
    index="요일", columns="월", values="해당일관객수"
)

# 요일 정렬 (월요일 -> 일요일)
weekday_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
]
pivot_heatmap = pivot_heatmap.reindex(weekday_order)

# 4. Plotly 히트맵(Heatmap) 생성
fig_heatmap = px.imshow(
    pivot_heatmap,
    labels=dict(x="월", y="요일", color="총 관객수(명)"),
    x=pivot_heatmap.columns,
    y=pivot_heatmap.index,
    color_continuous_scale="Reds",  # 관객이 많을수록 진한 빨간색
    title="월 × 요일별 총 관객수 분포 히트맵",
    aspect="auto",
)

# 히트맵 레이아웃 커스텀
fig_heatmap.update_xaxes(side="bottom")

# 그래프 화면에 출력
st.plotly_chart(fig_heatmap, use_container_width=True)

# 히트맵 해석 문구 자리
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 각 월별로 주말(토·일)과 평일(월~목)의 관객수 격차 양상을 한눈에 파악할 수 있으며, 연중 어떤 달의 무슨 요일에 극장 방문객이 가장 몰렸는지 색상의 짙기로 직관적으로 비교할 수 있습니다."
)
