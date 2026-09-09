import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 선택 영화 관객수 추이", 
    "🌊 누적 관객수 변화 (영역차트)", 
    "📊 TOP10 관객수 7일 이동평균", 
    "📅 월별 전체 관객수 (막대그래프)",
    "🏆 TOP5 영화 누적관객수 비교 (다중 선그래프)",
    "🗓️ 관객수 캘린더 히트맵"
])

# -----------------------------------------------------------------------------
# 첫 번째 그래프: [선그래프]
# -----------------------------------------------------------------------------
with tab1:
    st.subheader(f"'{selected_movie}' 날짜별 관객수 변화")
    
    if not filtered_df.empty:
        fig1 = px.line(
            filtered_df,
            x="기준일자",
            y="해당일관객수",
            title=f"[{selected_movie}] 일별 관객수 추이",
            labels={"기준일자": "날짜", "해당일관객수": "관객수 (명)"},
            markers=True
        )
        
        fig1.update_layout(
            hovermode="x unified",
            xaxis_title="기준일자",
            yaxis_title="해당일관객수"
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}' 영화는 특정 날짜에 관객수가 가장 높았으며, 개봉/상영 기간 동안 일별 흥행 추이를 확인할 수 있습니다.")
    else:
        st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

# -----------------------------------------------------------------------------
# 두 번째 그래프: [영역차트 - 누적 관객수]
# -----------------------------------------------------------------------------
with tab2:
    st.subheader(f"'{selected_movie}' 기준일자별 누적 관객수 변화")
    
    if not filtered_df.empty:
        fig2 = px.area(
            filtered_df,
            x="기준일자",
            y="누적관객수",
            title=f"[{selected_movie}] 누적 관객수 변화 추이",
            labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)"}
        )
        
        fig2.update_layout(
            hovermode="x unified",
            xaxis_title="기준일자",
            yaxis_title="누적관객수"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}' 영화의 상영 기간 동안 누적 관객수가 어떻게 지속적으로 증가했는지 전체적인 흥행 스케일을 확인할 수 있습니다.")
    else:
        st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

# -----------------------------------------------------------------------------
# 세 번째 그래프: [이동평균선 - TOP10 전체 관객수]
# -----------------------------------------------------------------------------
daily_top10_sum = df.groupby("기준일자")["해당일관객수"].sum().reset_index()
daily_top10_sum = daily_top10_sum.sort_values(by="기준일자")

with tab3:
    st.subheader("🎬 TOP 10 전체 관객수 합계 및 7일 이동평균 추이")
    
    daily_top10_sum["7일_이동평균"] = daily_top10_sum["해당일관객수"].rolling(window=7, min_periods=1).mean()
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Scatter(
        x=daily_top10_sum["기준일자"],
        y=daily_top10_sum["해당일관객수"],
        mode="lines",
        name="일별 총 관객수 (일일 원본)",
        line=dict(color="rgba(100, 149, 237, 0.35)", width=1.5),
        hovertemplate="일별 관객수: %{y:,.0f}명<extra></extra>"
    ))
    
    fig3.add_trace(go.Scatter(
        x=daily_top10_sum["기준일자"],
        y=daily_top10_sum["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#1f77b4", width=3),
        hovertemplate="7일 이동평균: %{y:,.0f}명<extra></extra>"
    ))
    
    fig3.update_layout(
        title="기준일자별 TOP 10 전체 관객수 합계 및 7일 이동평균",
        xaxis_title="기준일자",
        yaxis_title="관객수 합계 (명)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig3, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 요일이나 일별 변동성이 큰 단기 관객수 변동(연한 선)을 7일 이동평균선(진한 선)으로 평활화하여 극장가 전체의 중장기적인 시장 관객 수 흐름과 성수기/비수기 트렌드를 명확하게 파악할 수 있습니다.")

# -----------------------------------------------------------------------------
# 네 번째 그래프: [월별 막대그래프 - 월 단위 전체 관객수 합계]
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("📅 월별(연-월) 전체 관객수 합계")
    
    daily_top10_sum_copy = daily_top10_sum.copy()
    daily_top10_sum_copy["연월"] = daily_top10_sum_copy["기준일자"].dt.strftime("%Y-%m")
    
    monthly_sum = daily_top10_sum_copy.groupby("연월")["해당일관객수"].sum().reset_index()
    monthly_sum = monthly_sum.rename(columns={"해당일관객수": "월별관객수합계"})
    
    fig4 = px.bar(
        monthly_sum,
        x="연월",
        y="월별관객수합계",
        title="월별 전체 관객수 합계 추이",
        labels={"연월": "연-월", "월별관객수합계": "총 관객수 (명)"},
        text_auto=",.0f"
    )
    
    fig4.update_traces(marker_color="#2b5c8f")
    fig4.update_layout(
        xaxis_title="연-월",
        yaxis_title="월별 관객수 합계 (명)",
        xaxis=dict(type="category")
    )
    
    st.plotly_chart(fig4, use_container_width=True)
    st.info("💡 **이 그래프로 알 수 있는 것:** 월별 총 관객수 규모를 집계하여 어느 달(예: 방학 시즌, 연말, 명절 등)에 극장 방문객 수가 가장 많은지 계절성 및 월별 시장 성과를 한눈에 비교할 수 있습니다.")

# -----------------------------------------------------------------------------
# 다섯 번째 그래프: [다중 선그래프 - 20일 이상 TOP10 진입 영화 중 최고 누적관객수 TOP 5]
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("🏆 장기 흥행(20일 이상 차트인) TOP 5 영화의 누적관객수 추이")
    
    movie_counts = df.groupby("영화명")["기준일자"].nunique()
    movies_over_20days = movie_counts[movie_counts >= 20].index
    
    top5_movies = (
        df[df["영화명"].isin(movies_over_20days)]
        .groupby("영화명")["누적관객수"]
        .max()
        .nlargest(5)
        .index
        .tolist()
    )
    
    top5_df = df[df["영화명"].isin(top5_movies)].copy()
    
    fig5 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="TOP10 차트인 20일 이상 영화 중 누적관객수 TOP 5 비교",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)", "영화명": "영화 제목"},
        markers=True
    )
    
    fig5.update_layout(
        hovermode="x unified",
        xaxis_title="기준일자",
        yaxis_title="누적관객수 (명)",
        legend_title_text="영화명"
    )
    
    st.plotly_chart(fig5, use_container_width=True)
    
    top5_str = ", ".join([f"'{m}'" for m in top5_movies])
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 박스오피스 TOP10에 20일 이상 연속/장기 진입하며 꾸준한 관객을 모은 대표 흥행작({top5_str}) 5편의 관객수 누적 속도와 시기별 흥행 격차를 비교할 수 있습니다.")

# -----------------------------------------------------------------------------
# 여섯 번째 그래프: [캘린더 히트맵 - 일별 전체 관객수 합계]
# -----------------------------------------------------------------------------
with tab6:
    st.subheader("🗓️ 전체 관객수 합계 캘린더 히트맵")
    
    # 1. 연속 주차 및 요일 계산
    cal_df = daily_top10_sum.copy()
    
    # 요일 순서 고정 (월요일~일요일)
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    days_kor = ["월", "화", "수", "목", "금", "토", "일"]
    
    # 첫 날 기준으로 리셋 없는 연속 주차 번호 생성 (1, 2, 3... 52, 53...)
    min_date = cal_df["기준일자"].min()
    cal_df["연속주차"] = (cal_df["기준일자"] - min_date).dt.days // 7 + 1
    cal_df["요일코드"] = cal_df["기준일자"].dt.strftime("%a")
    cal_df["연월"] = cal_df["기준일자"].dt.strftime("%Y-%m")
    cal_df["월명"] = cal_df["기준일자"].dt.strftime("%y년 %m월")
    
    # 2. 피벗 테이블 생성 (행: 요일, 열: 연속주차, 값: 해당일관객수)
    pivot_df = cal_df.pivot(index="요일코드", columns="연속주차", values="해당일관객수")
    pivot_df = pivot_df.reindex(days_order) # 월~일 순서 정렬
    pivot_df.index = days_kor # 한글 요일로 변경
    
    # 3. 각 달이 시작하는 연속주차 위치와 월 이름을 추출하여 X축 눈금 생성
    first_days_per_month = cal_df.groupby("연월").first().reset_index()
    month_weeks = first_days_per_month["연속주차"].tolist()
    month_labels = first_days_per_month["월명"].tolist()
    
    # 4. Plotly 히트맵 구현
    fig6 = px.imshow(
        pivot_df,
        labels=dict(x="기간 (월별 구분)", y="요일", color="총 관객수 (명)"),
        x=pivot_df.columns,
        y=pivot_df.index,
        color_continuous_scale="Blues", # 값이 클수록 진한 색
        aspect="auto"
    )
    
    # 레이아웃 설정: 각 달의 시작 위치에 'YY년 MM월' 표시
    fig6.update_layout(
        title="전체 기간 일별 관객수 합계 캘린더 히트맵 (연속 주차)",
        xaxis=dict(
            tickmode="array",
            tickvals=month_weeks,
            ticktext=month_labels,
            title="월 (시작 시점)"
        ),
        yaxis=dict(autorange="reversed") # 월요일이 위로 오도록 설정
    )
    
    st.plotly_chart(fig6, use_container_width=True)
    
    # '이 그래프로 알 수 있는 것' 안내문
    st.info("💡 **이 그래프로 알 수 있는 것:** 1년 이상의 전체 데이터 기간 동안 연도 리셋 없이 일별 관객수 밀도를 달력 형태로 시각화했습니다. 주말과 평일 간의 관객수 격차는 물론, 연도별 명절, 방학, 황금연휴 시즌 등 관객 몰림 현상이 일어난 특정 주차를 연속적이고 직관적으로 비교할 수 있습니다.")
