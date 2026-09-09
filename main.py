import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ==========================================
# [1. 데이터 불러오기 및 캐싱]
# ==========================================


@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    df = df.dropna()
    df["기준일자"] = pd.to_datetime(df["기준일자"])
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
movie_rank = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

st.sidebar.header("🔍 설정")
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요",
    movie_rank,
)

filtered_df = df[df["영화명"] == selected_movie]

# ==========================================
# [4. 선 그래프 구역 (섹션 1)]
# ==========================================
st.header("📈 1. 영화별 일별 관객수 추이")

fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"'{selected_movie}'의 일별 관객수 변화",
    markers=True,
)

st.plotly_chart(fig1, use_container_width=True)
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 상영 기간 동안 일별 관객 수의 증가/감소 추세와 흥행 피크 시점을 파악할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [두 번째 그래프: 영역 차트 구역 (섹션 2)]
# ==========================================
st.header("📊 2. 영화별 누적 관객수 추이")

fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"'{selected_movie}'의 누적 관객수 변화 (영역 차트)",
    markers=True,
)

st.plotly_chart(fig2, use_container_width=True)
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 시간이 지남에 따라 '{selected_movie}'의 전체 누적 관객 수가 증가하는 완만함/경사도를 확인하여 흥행의 지속성을 파악할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [세 번째 그래프: 조건부 다중 선 그래프 구역 (섹션 3)]
# ==========================================
st.header("🏆 3. 장기 흥행 TOP 5 영화의 누적 관객수 비교")

movie_counts = df["영화명"].value_counts()
long_running_movies = movie_counts[movie_counts >= 20].index

filtered_top5_df = df[df["영화명"].isin(long_running_movies)]
top5_movies = (
    filtered_top5_df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

top5_df = df[df["영화명"].isin(top5_movies)]

fig3 = px.line(
    top5_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP 10에 20일 이상 등재된 흥행 상위 5개 영화 비교",
    markers=True,
)

st.plotly_chart(fig3, use_container_width=True)
top5_str = ", ".join(top5_movies)
st.caption(
    f"💡 **이 그래프로 알 수 있는 것:** 박스오피스 TOP 10에 20일 이상 머무르며 장기 흥행에 성공한 상위 5개 영화({top5_str})의 누적 관객수 증가 양상을 비교할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [네 번째 그래프: 전체 관객수 및 7일 이동평균선 구역 (섹션 4)]
# ==========================================
st.header("📉 4. 전체 박스오피스 일별 총 관객수 및 7일 이동평균")

daily_total = (
    df.groupby("기준일자")["해당일관객수"].sum().reset_index()
)
daily_total["7일이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7).mean()
)

fig4 = go.Figure()

fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 총 관객수 (일간 데이터)",
        line=dict(color="rgba(100, 149, 237, 0.35)", width=1.5),
    )
)

fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#1f77b4", width=3),
    )
)

fig4.update_layout(
    title="일별 박스오피스 전체 관객수 합계 및 7일 이동평균 추이",
    xaxis_title="기준일자",
    yaxis_title="관객수",
    hovermode="x unified",
)

st.plotly_chart(fig4, use_container_width=True)
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 주말/평일 노이즈(급격한 등락)를 제거한 7일 이동평균선을 통해 전체 극장가 관객수의 전반적인 시장 트렌드와 성수기/비수기 흐름을 부드럽게 파악할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [다섯 번째 그래프: 월별 전체 관객수 막대그래프 구역 (섹션 5)]
# ==========================================
st.header("📊 5. 월별 전체 박스오피스 관객수 합계")

daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

monthly_total = (
    daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
)

fig5 = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 박스오피스 전체 관객수 합계",
    labels={"연월": "월(Year-Month)", "해당일관객수": "월간 총 관객수"},
    text_auto=".2s",
)

fig5.update_traces(
    marker_color="#4682B4", textposition="outside"
)
fig5.update_layout(xaxis_type="category")

st.plotly_chart(fig5, use_container_width=True)
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 월별 총 관객 규모를 직관적으로 비교하여 영화 시장의 계절적 성수기(여름·겨울 방학, 연말 등)와 비수기의 차이를 명확히 구분할 수 있습니다."
)

st.markdown("---")

# ==========================================
# [여섯 번째 그래프: 요일 x 월/주차별 관객수 히트맵 구역 (섹션 6 - 수정됨)]
# ==========================================
st.header("🗓️ 6. 요일 × 월/주차별 전체 관객수 히트맵")

# 1. 기초 컬럼 추출 (연-월, 월 내 주차, 요일, YYYY-MM-DD 날짜)
heatmap_data = daily_total.copy()


# 월 내 주차(Week of Month) 계산 함수
def get_week_of_month(dt):
    first_day = dt.replace(day=1)
    adjusted_dom = dt.day + first_day.weekday()
    return (adjusted_dom - 1) // 7 + 1


heatmap_data["연월"] = heatmap_data["기준일자"].dt.strftime("%Y-%m")
heatmap_data["주차"] = heatmap_data["기준일자"].apply(get_week_of_month)
heatmap_data["월_주차"] = (
    heatmap_data["연월"] + " W" + heatmap_data["주차"].astype(str)
)

heatmap_data["요일"] = heatmap_data["기준일자"].dt.day_name()
heatmap_data["날짜str"] = heatmap_data["기준일자"].dt.strftime("%Y-%m-%d")

# 2. 요일 정렬 설정 (월요일 ~ 일요일) 및 한글 매핑
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
    "Sunday": "일요일",
}

heatmap_data["요일"] = pd.Categorical(
    heatmap_data["요일"], categories=day_order, ordered=True
)

# 3. 월/주차 오름차순 목록 추출 및 그룹화
week_order = heatmap_data["월_주차"].unique().tolist()

grouped = (
    heatmap_data.groupby(["요일", "월_주차"], observed=False)
    .agg(
        관객수합계=("해당일관객수", "sum"),
        날짜목록=(
            "날짜str",
            lambda x: "<br>".join(x) if len(x) > 0 else "해당 없음",
        ),
    )
    .reset_index()
)

# 4. 피벗 테이블 생성 (행: 요일, 열: 월/주차)
pivot_sum = grouped.pivot(
    index="요일", columns="월_주차", values="관객수합계"
).reindex(index=day_order, columns=week_order)

pivot_dates = grouped.pivot(
    index="요일", columns="월_주차", values="날짜목록"
).reindex(index=day_order, columns=week_order)

# 행(Y축 요일) 한글화 및 열(X축 월/주차) 라벨 설정
y_labels = [day_kr_map[d] for d in day_order]
x_labels = pivot_sum.columns.tolist()

# 5. Plotly px.imshow 및 호버 툴팁 적용
fig6 = px.imshow(
    pivot_sum,
    labels=dict(x="월 / 주차", y="요일", color="관객수 합계"),
    x=x_labels,
    y=y_labels,
    color_continuous_scale="Reds",  # 관객수가 많을수록 짙어지는 색상
    title="요일 × 월/주차별 전체 관객수 집계 (캘린더 히트맵)",
    aspect="auto",
)

# 마우스 올렸을 때 YYYY-MM-DD 날짜 및 관객수가 표기되도록 설정
fig6.update_traces(
    customdata=pivot_dates.values,
    hovertemplate=(
        "<b>%{y} (%{x})</b><br><br>"
        "<b>📅 해당 날짜:</b><br>%{customdata}<br><br>"
        "<b>👥 관객수 합계:</b> %{z:,}명"
        "<extra></extra>"
    ),
)

# Y축 역순 정렬 (월요일이 맨 위, 일요일이 맨 아래에 배치)
fig6.update_layout(
    xaxis_title="월 / 주차",
    yaxis_title="요일",
    yaxis=dict(autorange="reversed"),
)

# 그래프 화면 출력
st.plotly_chart(fig6, use_container_width=True)

# 그래프 하단 설명 문구 (캡션)
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** Y축(월요일~일요일)과 X축(주차 흐름)에 따른 관객 집중도를 색상 농도로 파악할 수 있으며, 마우스를 올리면 실제 속한 날짜(`YYYY-MM-DD`)와 관객수를 확인할 수 있습니다."
)
