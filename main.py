import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================================================================
# [페이지 기본 설정]
# 웹 브라우저 탭에 표시될 제목과 레이아웃을 설정합니다.
# ==============================================================================
st.set_page_config(
    page_title="KOBIS 박스오피스 데이터 분석",
    page_icon="🎬",
    layout="wide"
)

# ==============================================================================
# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 데이터를 매번 다시 불러오지 않고
# 한 번 불러온 데이터를 캐시(저장)해두어 앱 실행 속도를 향상시킵니다.
# ==============================================================================
@st.cache_data
def load_data():
    # 데이터셋 URL 주소
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    
    # pandas로 CSV 파일 읽어오기
    df = pd.read_csv(url)
    
    # --------------------------------------------------------------------------
    # [2. 날짜 전처리]
    # "기준일자"와 "개봉일" 컬럼을 datetime 형식으로 변환합니다.
    # errors='coerce' 옵션을 통해 개봉일 정보가 없는 빈 칸(7개 행)은
    # 행 전체를 삭제하지 않고 NaT(날짜 없음) 상태로 보존합니다.
    # --------------------------------------------------------------------------
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    df["개봉일"] = pd.to_datetime(df["개봉일"], errors="coerce")
    
    # 전체 데이터를 "기준일자" 순서대로 정렬합니다.
    df = df.sort_values(by="기준일자").reset_index(drop=True)
    
    return df

# 데이터 로딩 실행
df = load_data()

# 일관객 컬럼명 자동 감지 (일관객수, 일관객, 관객수 등 대처)
audience_col = None
for col in ["일관객수", "일관객", "관객수", "당일관객수"]:
    if col in df.columns:
        audience_col = col
        break

if audience_col is None:
    # 관객 관련 컬럼을 찾지 못한 경우 기본값 지정
    audience_col = "일관객수"

# ==============================================================================
# [메인 타이틀 및 소개]
# ==============================================================================
st.title("🎬 KOBIS 영화 박스오피스 데이터 분석 웹앱")
st.markdown("최근 1년간의 영화 박스오피스 데이터를 바탕으로 영화별 관객수 추이 등을 시각화합니다.")
st.divider()

# ==============================================================================
# [3. 영화 선택 기능 (사이드바)]
# "영화명" 컬럼에서 중복을 제거한 목록을 생성하고 사용자가 선택하도록 합니다.
# ==============================================================================
st.sidebar.header("🔍 검색 및 필터")

# 중복 없는 영화 목록 생성 (오름차순 정렬)
movie_list = sorted(df["영화명"].dropna().unique())

# 영화 선택 드롭다운 (기본값: 첫 번째 영화)
selected_movie = st.sidebar.selectbox(
    "분석할 영화를 선택하세요:",
    options=movie_list,
    index=0
)

# 선택된 영화의 데이터만 필터링
movie_data = df[df["영화명"] == selected_movie].copy()

# 개봉일 정보 추출 (첫 번째 행 기준)
first_release_date = movie_data["개봉일"].iloc[0]
if pd.isna(first_release_date):
    release_date_str = "날짜 없음 (특별 상영/콘서트 필름 등)"
else:
    release_date_str = first_release_date.strftime("%Y-%m-%d")

# ==============================================================================
# [4. 구역 분할 - 섹션 1: 일별 관객 수 변화 선 그래프]
# 앞으로 그래프가 더 추가될 수 있으므로 st.container()를 사용하여 구역을 분할합니다.
# ==============================================================================
with st.container():
    st.subheader(f"📈 [구역 1] '{selected_movie}' 일별 관객 수 추이")
    
    # 영화 주요 요약 정보 카드
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🎬 선택된 영화", value=selected_movie)
    with col2:
        st.metric(label="📅 개봉일", value=release_date_str)
    with col3:
        total_audience = movie_data[audience_col].sum() if audience_col in movie_data.columns else 0
        st.metric(label="👥 기간 내 총 관객 수", value=f"{total_audience:,} 명")

    st.write("") # 여백 조절

    # Plotly 선 그래프(Line Chart) 생성
    fig = px.line(
        movie_data,
        x="기준일자",
        y=audience_col,
        title=f"'{selected_movie}' 날짜별 일관객 수 변화",
        labels={
            "기준일자": "날짜 (기준일자)",
            audience_col: "일일 관객 수 (명)"
        },
        markers=True,  # 데이터 포인트에 점 표시
        template="plotly_white"
    )

    # 그래프 디자인 커스텀
    fig.update_traces(
        line_color="#1f77b4",
        line_width=2.5,
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객수:</b> %{y:,}명<extra></extra>"
    )

    fig.update_layout(
        hovermode="x unified",
        xaxis_title="기준일자",
        yaxis_title="일관객 수 (명)",
        margin=dict(l=20, r=20, t=50, b=20)
    )

    # Streamlit 화면에 Plotly 그래프 출력
    st.plotly_chart(fig, use_container_width=True)

    # 💡 '이 그래프로 알 수 있는 것' 안내 문구 박스
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** "
        f"'{selected_movie}'의 개봉/상영 기간 동안 일별 관객 수가 시간에 따라 어떻게 변하는지, "
        f"그리고 언제 가장 많은 관객(최고 흥행일)이 몰렸는지 관객 수 추이를 한눈에 파악할 수 있습니다."
    )

st.divider()

# ==============================================================================
# [5. 구역 분할 - 섹션 2: 향후 추가 그래프를 위한 예시 구역]
# 요청사항에 따라 차후 그래프 추가에 대비하여 구역을 미리 생성해 두었습니다.
# ==============================================================================
with st.container():
    st.subheader("📊 [구역 2] 추가 분석 그래프 (예정)")
    st.caption("※ 이 구역은 추후 다른 분석 그래프(예: 주말/평일 관객 비교, 상위 영화 비교 등)를 추가할 수 있는 공간입니다.")
    
    # 자리를 비워두는 안내 플레이스홀더
    st.warning("추가 그래프가 준비 중입니다. 원하는 분석 항목이 있다면 코드를 추가해 보세요!")
    
    # 💡 '이 그래프로 알 수 있는 것' 안내 문구 자리 예시
    st.info("💡 **이 그래프로 알 수 있는 것:** (추가 예정 그래프에 대한 설명 한 문장이 여기에 들어갑니다.)")
