import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 페이지 기본 설정 (넓은 레이아웃 사용)
st.set_page_config(page_title="영화 관객수 분석 App", layout="wide")


# [1. 데이터 불러오기 및 캐싱]
# @st.cache_data를 사용하여 데이터가 새로고침되어도 매번 새로 받지 않고 재사용합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)

    # [2. 날짜 전처리]
    # 결측치가 하나라도 있는 행 제거
    df = df.dropna()

    # '기준일자' 컬럼을 datetime 날짜 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])

    # 전체 데이터를 '기준일자' 오름차순으로 정렬
    df = df.sort_values(by="기준일자")

    return df


# 데이터 로드
df = load_data()


# [3. 영화 선택 기능]
# 메인 화면 타이틀
st.title("🎬 박스오피스 영화 관객수 분석")

# 누적관객수가 가장 높은 순으로 중복 없는 영화 목록 생성
movie_order = (
    df.groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .index.tolist()
)

# 사용자 영화 선택 드롭다운 (기본값: 누적관객수 1위 영화)
selected_movie = st.selectbox("분석할 영화를 선택하세요:", movie_order)

# 선택한 영화의 데이터만 필터링
filtered_df = df[df["영화명"] == selected_movie]

st.markdown("---")


# [4-1. 선 그래프 구역 - 해당일관객수]
st.header(f"📈 '{selected_movie}' 일별 관객수 추이")

# Plotly 선 그래프 생성
fig1 = px.line(
    filtered_df,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} - 일별 관객수 변화",
    markers=True,  # 데이터 점 표시
    labels={"기준일자": "날짜", "해당일관객수": "관객수 (명)"},
)

# 그래프 X축 날짜 형식 지정
fig1.update_xaxes(dtick="M1", tickformat="%b\n%Y")

# 화면에 Plotly 그래프 출력
st.plotly_chart(fig1, use_container_width=True)

# 첫 번째 그래프 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 개봉 초기 관객수 집중도와 주말/평일 관객수 변동 패턴을 파악할 수 있습니다."
)


st.markdown("---")


# [4-2. 영역 차트 구역 - 누적관객수]
st.header(f"📊 '{selected_movie}' 누적 관객수 성장 추이")

# Plotly 영역 차트(Area Chart) 생성
fig2 = px.area(
    filtered_df,
    x="기준일자",
    y="누적관객수",
    title=f"{selected_movie} - 누적 관객수 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)"},
)

# 그래프 X축 날짜 형식 지정
fig2.update_xaxes(dtick="M1", tickformat="%b\n%Y")

# 화면에 Plotly 그래프 출력
st.plotly_chart(fig2, use_container_width=True)

# 두 번째 그래프 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 영화의 흥행 지속성과 누적 관객수가 급격히 증가하거나 완만해지는 시점을 시각적으로 파악할 수 있습니다."
)


st.markdown("---")


# [4-3. 다중 선그래프 구역 - 조건부 흥행 TOP 5 영화 비교]
st.header("🏆 TOP10 20일 이상 유지 영화 중 누적관객수 TOP 5 비교")

# 1. 영화별 TOP10 차트 등장 일수 계산
movie_days = df.groupby("영화명").size()

# 2. 등장 일수가 20일 이상인 영화만 필터링
movies_over_20days = movie_days[movie_days >= 20].index

# 3. 20일 이상 등장한 영화들 중 누적관객수 상위 5개 영화 선별
top5_filtered_movies = (
    df[df["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

# 4. 해당 5개 영화의 전체 데이터 추출
top5_filtered_df = df[df["영화명"].isin(top5_filtered_movies)]

# Plotly 다중 선그래프 생성
fig3 = px.line(
    top5_filtered_df,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP10 20일 이상 차트인 영화 - 누적관객수 TOP 5 비교",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)", "영화명": "영화 제목"},
)

# 그래프 X축 날짜 형식 지정
fig3.update_xaxes(dtick="M1", tickformat="%b\n%Y")

# 화면에 Plotly 그래프 출력
st.plotly_chart(fig3, use_container_width=True)

# 세 번째 그래프 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 박스오피스 상위권에 최소 20일 이상 장기 집권한 영화들 중에서도 최고 흥행작들의 성장 곡선과 관객 수 모객 속도를 비교 분석할 수 있습니다."
)


st.markdown("---")


# [4-4. 이동평균선 구역 - 전체 박스오피스 일별 관객수 총합 및 7일 이동평균]
st.header("📉 전체 박스오피스 일별 관객 합계 및 7일 이동평균 추이")

# 1. 기준일자별 TOP10 영화의 해당일관객수 총합 계산
daily_total = df.groupby("기준일자")["해당일관객수"].sum().reset_index()

# 2. 7일 이동평균 계산
daily_total["7일_이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()
)

# 3. graph_objects를 활용하여 커스텀 시각화
fig4 = go.Figure()

# 원본 관객수 선 (연한 색상)
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 총 관객수",
        line=dict(color="rgba(150, 180, 220, 0.5)", width=1.5),
    )
)

# 7일 이동평균 선 (진한 색상)
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#D32F2F", width=3),
    )
)

fig4.update_layout(
    title="전체 박스오피스 일별 관객수 총합 및 7일 이동평균 트렌드",
    xaxis_title="날짜",
    yaxis_title="관객수 (명)",
    hovermode="x unified",
)

fig4.update_xaxes(dtick="M1", tickformat="%b\n%Y")

st.plotly_chart(fig4, use_container_width=True)

st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 주말과 평일의 심한 일별 관객수 변동 노이즈를 제하고, 전체 극장가의 성수기/비수기 시즌성 흐름 및 장기 트렌드를 명확히 파악할 수 있습니다."
)


st.markdown("---")


# [4-5. 막대그래프 구역 - 월별 전체 관객수 합계]
st.header("📅 월별 전체 박스오피스 관객수 합계")

# 1. daily_total 데이터프레임의 기준일자를 연-월(YYYY-MM) 문자열 형식으로 변환
daily_total["연월"] = daily_total["기준일자"].dt.to_period("M").astype(str)

# 2. 연-월 단위로 그룹화하여 관객수 합산
monthly_total = (
    daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
)

# 3. Plotly 막대그래프 생성
fig5 = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 전체 박스오피스 관객수 합계",
    text_auto=".2s",
    labels={"연월": "월 (연-월)", "해당일관객수": "월간 총 관객수 (명)"},
    color="해당일관객수",
    color_continuous_scale="Viridis",
)

# 그래프 X축 및 레이아웃 설정
fig5.update_xaxes(type="category")
fig5.update_layout(showlegend=False)

# 화면에 Plotly 그래프 출력
st.plotly_chart(fig5, use_container_width=True)

# 다섯 번째 그래프 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 연중 어떤 월(달)에 영화관 전체 관객수가 가장 많고 적은지 월별 총 수요와 성수기/비수기의 규모 차이를 직관적으로 비교할 수 있습니다."
)


st.markdown("---")


# [4-6. 캘린더 히트맵 구역 - 주차 및 요일별 관객수 히트맵]
st.header("🗓️ 주차 및 요일별 관객수 캘린더 히트맵")

# 1. 히트맵 전용 데이터 생성 (daily_total 활용)
heatmap_df = daily_total.copy()

# 연-주차(YYYY-Www) 정보 추출
heatmap_df["주차"] = heatmap_df["기준일자"].dt.strftime("%Y-W%U")

# 요일 이름 추출 (영문 요일)
heatmap_df["요일_영문"] = heatmap_df["기준일자"].dt.day_name()

# 요일을 월요일~일요일 순서로 정렬하기 위한 범주형 데이터 설정
days_order = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
korean_days = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
day_map = dict(zip(days_order, korean_days))

# 요일을 한글 요일명으로 변환
heatmap_df["요일"] = heatmap_df["요일_영문"].map(day_map)

# 툴팁에 띄울 YYYY-MM-DD 날짜 문자열
heatmap_df["날짜_str"] = heatmap_df["기준일자"].dt.strftime("%Y-%m-%d")

# 2. 피벗 테이블 생성 (행: 주차, 열: 요일)
pivot_values = heatmap_df.pivot(
    index="주차", columns="요일", values="해당일관객수"
)
pivot_dates = heatmap_df.pivot(
    index="주차", columns="요일", values="날짜_str"
)

# 요일 순서에 맞춰 컬럼 재정렬
pivot_values = pivot_values.reindex(columns=korean_days)
pivot_dates = pivot_dates.reindex(columns=korean_days)

# 3. Plotly 히트맵 생성 (px.imshow 활용)
fig6 = px.imshow(
    pivot_values,
    labels=dict(x="요일", y="연도별 주차", color="관객수 (명)"),
    x=korean_days,
    y=pivot_values.index,
    color_continuous_scale="Reds",  # 관객이 많을수록 진한 붉은색
    aspect="auto",
    title="주차 및 요일별 박스오피스 총 관객수 분포",
)

# 마우스 호버 시 실제 YYYY-MM-DD 날짜와 관객수가 함께 표시되도록 설정
custom_hover = []
for i in range(len(pivot_values)):
    row_hover = []
    for j in range(len(korean_days)):
        val = pivot_values.iloc[i, j]
        date_str = pivot_dates.iloc[i, j]
        if pd.isna(val):
            row_hover.append("데이터 없음")
        else:
            row_hover.append(
                f"날짜: {date_str}<br>요일: {korean_days[j]}<br>관객수: {val:,.0f}명"
            )
    custom_hover.append(row_hover)

fig6.update_traces(
    hovertemplate="%{customdata}<extra></extra>", customdata=custom_hover
)

# 화면에 Plotly 그래프 출력
st.plotly_chart(fig6, use_container_width=True)

# 여섯 번째 그래프 설명 문구
st.caption(
    "💡 **이 그래프로 알 수 있는 것:** 특정 주차의 주말/평일 및 공휴일 여부에 따른 관객수 집중 패턴을 캘린더 형태의 색상 농도로 한눈에 파악할 수 있습니다."
)
