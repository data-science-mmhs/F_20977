import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# [1. 데이터 불러오기 및 캐싱]
# ==========================================
# @st.cache_data를 사용하면 데이터를 매번 새로 불러오지 않고
# 캐시(메모리)에 저장해 두어 앱 실행 속도가 훨씬 빨라집니다.


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치(빈 값)가 하나라도 있는 행 삭제
    df = df.dropna()

    # '기준일자' 컬럼을 datetime(날짜) 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 '기준일자' 오름차순으로 정렬
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드
df = load_data()

# ==========================================
# [앱 헤더 및 기본 설정]
# ==========================================
st.title("🎬 박스오피스 데이터 분석 웹앱")
st.write("영화별 관객수 변화 및 추이를 분석하는 웹 dashboard입니다.")

st.markdown("---")

# ==========================================
# [3. 영화 선택 기능]
# ==========================================
# 영화별 누적관객수 최대값을 기준으로 내림차순 정렬하여 영화 목록 생성
movie_rank = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사이드바에서 영화 선택
st.sidebar.header("🔍 설정")
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요",
    movie_rank,
)

# 선택된 영화 데이터 미리 필터링
filtered_df = df[df["영화명"] == selected_movie]

# ==========================================
# [4. 선 그래프 구역 (섹션 1)]
# ==========================================
st.header("📈 1. 영화별 일별 관객수 추이")

# Plotly 선 그래프 생성
fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객수 변화",
    markers=True,  # 데이터 지점에 점 표시
)

# 그래프 화면 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 하단 설명 문구 (캡션)
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 상영 기간 동안 일별 관객 수의 증가/감소 추세와 흥행 피크 시점을 파악할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [두 번째 그래프: 영역 차트 구역 (섹션 2)]
# ==========================================
st.header("📊 2. 영화별 누적 관객수 추이")

# Plotly 영역 차트(Area Chart) 생성
fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}'의 누적 관객수 변화 (영역 차트)",
    markers=True,
)

# 그래프 화면 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 하단 설명 문구 (캡션)
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 '{selected_movie}'의 전체 누적 관객 수가 증가하는 완만함/경사도를 확인하여 흥행의 지속성을 파악할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [세 번째 그래프: 조건부 다중 선 그래프 구역 (섹션 3)]
# ==========================================
st.header("🏆 3. 장기 흥행 TOP 5 영화의 누적 관객수 비교")

# 1. 영화별 TOP 10 차트 등장 일수 집계
movie_counts = df["영화명"].value_counts()

# 2. 20일 이상 등장한 영화 목록 추출
long_running_movies = movie_counts[movie_counts >= 20].index

# 3. 해당 영화들 중 누적관객수 상위 5개 영화 선정
filtered_top5_df = df[df["영화명"].isin(long_running_movies)]
top5_movies = (
    filtered_top5_df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# 4. 최종 선정된 5개 영화의 데이터 필터링
top5_df = df[df["영화명"].isin(top5_movies)]

# Plotly 다중 선 그래프 생성
fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",  # 영화별 색상 구분 및 범례 자동 생성
    title="TOP 10에 20일 이상 등재된 흥행 상위 5개 영화 비교",
    markers=True,
)

# 그래프 화면 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 하단 설명 문구 (캡션)
top5_str = ", ".join(top5_movies)
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 박스오피스 TOP 10에 20일 이상 머무르며 장기 흥행에 성공한 상위 5개 영화({top5_str})의 누적 관객수 증가 양상을 비교할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [네 번째 그래프: 전체 관객수 및 7일 이동평균선 구역 (섹션 4)]
# ==========================================
st.header("📉 4. 전체 박스오피스 일별 총 관객수 및 7일 이동평균")

# 1. 기준일자별 TOP 10 영화의 '해당일관객수' 합계 구하기
daily_total = (
    df.groupby("기준일자")["해당일관객수"].sum().reset_index()
)

# 2. 7일 이동평균 계산 (rolling, window=7)
daily_total["7일이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7).mean()
)

# 3. Plotly graph_objects를 활용하여 두 선을 겹쳐서 시각화
fig4 = go.Figure()

# 원본 일별 총 관객수 선 (연하게 표시: 투명도 조정)
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 총 관객수 (일간 데이터)",
        line=dict(color="rgba(100, 149, 237, 0.35)", width=1.5),
    )
)

# 7일 이동평균선 (진하게 표시)
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#1f77b4", width=3),
    )
)

# 레이아웃 설정
fig4.update_layout(
    title="일별 박스오피스 전체 관객수 합계 및 7일 이동평균 추이",
    xaxis_title="기준일자",
    yaxis_title="관객수",
    hovermode="x unified",
)

# 그래프 화면 출력
st.plotly_chart(fig4, use_container_width=True)

# 그래프 하단 설명 문구 (캡션)
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 주말/평일 노이즈(급격한 등락)를 제거한 7일 이동평균선을 통해 전체 극장가 관객수의 전반적인 시장 트렌드와 성수기/비수기 흐름을 부드럽게 파악할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [다섯 번째 그래프: 월별 전체 관객수 막대그래프 구역 (섹션 5)]
# ==========================================
st.header("📊 5. 월별 전체 박스오피스 관객수 합계")

# 1. 기준일자에서 '연-월(YYYY-MM)' 문자열 추출
daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

# 2. 연-월 단위로 그룹화하여 해당일관객수 합산
monthly_total = (
    daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
)

# 3. Plotly 막대그래프 생성
fig5 = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 박스오피스 전체 관객수 합계",
    labels={"연월": "월(Year-Month)", "해당일관객수": "월간 총 관객수"},
    text_auto=".2s",  # 막대 위에 축약된 숫자로 관객수 표시 (예: 1.5M)
)

# 막대 색상 및 디자인 가독성 조정
fig5.update_traces(
    marker_color="#4682B4", textposition="outside"
)
fig5.update_layout(xaxis_type="category")

# 그래프 화면 출력
st.plotly_chart(fig5, use_container_width=True)

# 그래프 하단 설명 문구 (캡션)
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 월별 총 관객 규모를 직관적으로 비교하여 영화 시장의 계절적 성수기(여름·겨울 방학, 연말 등)와 비수기의 차이를 명확히 구분할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [여섯 번째 그래프: 월 x 요일별 관객수 히트맵 구역 (섹션 6)]
# ==========================================
st.header("🗓️ 6. 월 × 요일별 전체 관객수 히트맵")

# 1. 월(YYYY-MM)과 요일 정보 추출
heatmap_data = daily_total.copy()
heatmap_data["월"] = heatmap_data["기준일자"].dt.strftime("%Y-%m")
heatmap_data["요일"] = heatmap_data["기준일자"].dt.day_name()

# 2. 요일 순서 지정 (월요일 ~ 일요일)
day_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
day_kr_map = {
    "Monday": "월요일",
    "Tuesday": "화요일",
    "Wednesday": "수요일",
    "Thursday": "목요일",
    "Friday": "금요일",
    "Saturday": "토요일",
}
day_kr_map["Sunday"] = "일요일"

# 요일 정렬을 위한 카테고리화
heatmap_data["요일"] = pd.Categorical(
    heatmap_data["요일"], categories=day_order, ordered=True
)

# 3. 데이터 원본의 날짜 오름차순 순서를 유지하여 '연월' 고유 목록 추출 (년도/월 순서 보장)
month_order = heatmap_data["월"].unique().tolist()

# 4. 월 x 요일 그룹화 및 피벗 테이블 생성
pivot_df = (
    heatmap_data.groupby(["월", "요일"], observed=False)["해당일관객수"]
    .sum()
    .unstack(level="요일")
)

# 연-월 순서(오름차순)가 보장되도록 reindex 설정
pivot_df = pivot_df.reindex(month_order)

# 요일 컬럼명을 한글로 변경
pivot_df.columns = [
    day_kr_map[col] for col in pivot_df.columns
]

# 5. Plotly 히트맵 생성
fig6 = px.imshow(
    pivot_df,
    labels=dict(x="요일", y="월(연도-월)", color="관객수 합계"),
    x=[day_kr_map[d] for d in day_order],
    y=pivot_df.index.tolist(),
    color_continuous_scale="Reds",  # 진할수록 관객수가 많은 색상 패턴
    title="월 × 요일별 전체 관객수 집계 (히트맵)",
    aspect="auto",
)

# Y축의 연-월 순서가 위에서 아래로 시간 순서대로 정렬되도록 조정 ('reversed' 축 설정)
fig6.update_layout(
    xaxis_title="요일",
    yaxis_title="월(연도-월)",
    yaxis=dict(autorange="reversed"),  # 상단이 과거, 하단이 최근 연-월로 정렬
)

# 그래프 화면 출력
st.plotly_chart(fig6, use_container_width=True)

# 그래프 하단 설명 문구 (캡션)
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 연도 및 월 순서대로 배치된 히트맵을 통해 특정 시기(월)와 요일별 관객 집중도를 관객수가 많을수록 짙어지는 색상 패턴으로 직관적으로 파악할 수 있습니다."
)
