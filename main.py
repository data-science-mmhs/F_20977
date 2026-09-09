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
# 1탭: 선택 영화 관객수 추이 (선그래프)
# 2탭: 선택 영화 누적 관객수 변화 (영역차트)
# 3탭: TOP 10 전체 관객수 및 7일 이동평균 (선그래프)
# 4탭: 월별 전체 관객수 합계 (막대그래프)
# 5탭: TOP 5 영화 누적관객수 비교 (다중 선그래프)
# 6탭: 추가 분석 구역 (예정)
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 선택 영화 관객수 추이", 
    "🌊 누적 관객수 변화 (영역차트)", 
    "📊 TOP10 관객수 7일 이동평균", 
    "📅 월별 전체 관객수 (막대그래프)",
    "🏆 TOP5 영화 누적관객수 비교 (다중 선그래프)",
    "➕ 추가 분석 구역 (예정)"
])

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
# 세 번째 그래프: [이동평균선 - TOP10 전체 관객수]
# -----------------------------------------------------------------------------
# 1. 기준일자별로 전체 TOP 10 영화의 해당일관객수 합계를 구합니다.
daily_top10_sum = df.groupby("기준일자")["해당일관객수"].sum().reset_index()
daily_top10_sum = daily_top10_sum.sort_values(by="기준일자")

with tab3:
    st.subheader("🎬 TOP 10 전체 관객수 합계 및 7일 이동평균 추이")
    
    # 2. 7일 이동평균(7-day Moving Average)을 계산합니다.
    daily_top10_sum["7일_이동평균"] = daily_top10_sum["해당일관객수"].rolling(window=7, min_periods=1).mean()
    
    # 3. plotly.graph_objects를 사용하여 원본 선과 이동평균 선을 겹쳐서 그립니다.
    fig3 = go.Figure()
    
    # 원본 관객수 합계 선 (연하게 표시)
    fig3.add_trace(go.Scatter(
        x=daily_top10_sum["기준일자"],
        y=daily_top10_sum["해당일관객수"],
        mode="lines",
        name="일별 총 관객수 (일일 원본)",
        line=dict(color="rgba(100, 149, 237, 0.35)", width=1.5), # 연한 파란색
        hovertemplate="일별 관객수: %{y:,.0f}명<extra></extra>"
    ))
    
    # 7일 이동평균 선 (진하게 표시)
    fig3.add_trace(go.Scatter(
        x=daily_top10_sum["기준일자"],
        y=daily_top10_sum["7일_이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#1f77b4", width=3), # 진한 파란색
        hovertemplate="7일 이동평균: %{y:,.0f}명<extra></extra>"
    ))
    
    # 레이아웃 설정
    fig3.update_layout(
        title="기준일자별 TOP 10 전체 관객수 합계 및 7일 이동평균",
        xaxis_title="기준일자",
        yaxis_title="관객수 합계 (명)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Streamlit에 표시
    st.plotly_chart(fig3, use_container_width=True)
    
    # '이 그래프로 알 수 있는 것' 안내문
    st.info("💡 **이 그래프로 알 수 있는 것:** 요일이나 일별 변동성이 큰 단기 관객수 변동(연한 선)을 7일 이동평균선(진한 선)으로 평활화하여 극장가 전체의 중장기적인 시장 관객 수 흐름과 성수기/비수기 트렌드를 명확하게 파악할 수 있습니다.")

# -----------------------------------------------------------------------------
# 네 번째 그래프: [월별 막대그래프 - 월 단위 전체 관객수 합계]
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("📅 월별(연-월) 전체 관객수 합계")
    
    # 기준일자별 관객수 합계(daily_top10_sum) 데이터에서 연-월(YYYY-MM) 컬럼을 생성합니다.
    daily_top10_sum_copy = daily_top10_sum.copy()
    daily_top10_sum_copy["연월"] = daily_top10_sum_copy["기준일자"].dt.strftime("%Y-%m")
    
    # 월(연-월) 단위로 그룹화하여 관객수를 합산합니다.
    monthly_sum = daily_top10_sum_copy.groupby("연월")["해당일관객수"].sum().reset_index()
    monthly_sum = monthly_sum.rename(columns={"해당일관객수": "월별관객수합계"})
    
    # Plotly 막대그래프 그리기
    fig4 = px.bar(
        monthly_sum,
        x="연월",
        y="월별관객수합계",
        title="월별 전체 관객수 합계 추이",
        labels={"연월": "연-월", "월별관객수합계": "총 관객수 (명)"},
        text_auto=",.0f"  # 막대 위에 숫자를 세천단위 콤마 형식으로 표시
    )
    
    # 막대 색상 및 레이아웃 설정
    fig4.update_traces(marker_color="#2b5c8f")
    fig4.update_layout(
        xaxis_title="연-월",
        yaxis_title="월별 관객수 합계 (명)",
        xaxis=dict(type="category")  # 연-월 축을 카테고리 형태로 고정
    )
    
    # Streamlit에 표시
    st.plotly_chart(fig4, use_container_width=True)
    
    # '이 그래프로 알 수 있는 것' 안내문
    st.info("💡 **이 그래프로 알 수 있는 것:** 월별 총 관객수 규모를 집계하여 어느 달(예: 방학 시즌, 연말, 명절 등)에 극장 방문객 수가 가장 많은지 계절성 및 월별 시장 성과를 한눈에 비교할 수 있습니다.")

# -----------------------------------------------------------------------------
# 다섯 번째 그래프: [다중 선그래프 - 최고 누적관객수 TOP 5 영화 비교]
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("🏆 누적관객수 TOP 5 영화의 기준일자별 누적관객수 추이 비교")
    
    # 1. 영화별 최고 누적관객수를 구하여 상위 5개 영화 선택
    top5_movies = (
        df.groupby("영화명")["누적관객수"]
        .max()
        .nlargest(5)
        .index
        .tolist()
    )
    
    # 2. TOP 5 영화의 데이터만 추출
    top5_df = df[df["영화명"].isin(top5_movies)].copy()
    
    # 3. Plotly 다중 선그래프 그리기 (color='영화명'으로 범례 및 영화별 컬러 자동 구분)
    fig5 = px.line(
        top5_df,
        x="기준일자",
        y="누적관객수",
        color="영화명",
        title="TOP 5 흥행 영화별 누적관객수 성장 추이",
        labels={"기준일자": "날짜", "누적관객수": "누적 관객수 (명)", "영화명": "영화 제목"},
        markers=True
    )
    
    # 레이아웃 설정
    fig5.update_layout(
        hovermode="x unified",
        xaxis_title="기준일자",
        yaxis_title="누적관객수 (명)",
        legend_title_text="영화명"
    )
    
    # Streamlit에 표시
    st.plotly_chart(fig5, use_container_width=True)
    
    # TOP 5 영화 목록 텍스트 생성
    top5_str = ", ".join([f"'{m}'" for m in top5_movies])
    
    # '이 그래프로 알 수 있는 것' 안내문
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 최고 누적 관객수를 기록한 상위 5개 영화({top5_str})의 흥행 속도와 누적 관객수 역전 현상, 상영 기간 동안의 누적 관객수 증가세를 한눈에 비교할 수 있습니다.")

# -----------------------------------------------------------------------------
# 여섯 번째 탭: [추가 예정 구역]
# -----------------------------------------------------------------------------
with tab6:
    st.subheader("📊 추가 그래프 영역")
    st.write("앞으로 이 구역에 추가적인 분석 그래프나 통계 정보를 확장할 수 있습니다.")
    st.info("💡 **이 그래프로 알 수 있는 것:** (추가 예정 그래프에 대한 설명이 들어갈 자리입니다.)")
