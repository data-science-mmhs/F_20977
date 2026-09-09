import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# [페이지 기본 설정]
# 웹 브라우저 탭의 제목, 아이콘, 레이아웃(wide: 넓은 화면 사용)을 설정합니다.
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="KOBIS 박스오피스 데이터 분석",
    page_icon="🎬",
    layout="wide"
)

# -----------------------------------------------------------------------------
# [1. 데이터 불러오기 및 캐싱]
# @st.cache_data 데코레이터를 사용하여 데이터를 메모리에 저장(캐싱)합니다.
# 이렇게 하면 사용자가 영화를 변경하거나 조작할 때마다 CSV를 다시 읽지 않아 속도가 빠릅니다.
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # KOBIS 박스오피스 CSV 파일 URL
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    
    # pandas로 CSV 데이터 불러오기
    df = pd.read_csv(url)
    
    # -------------------------------------------------------------------------
    # [2. 날짜 전처리]
    # '기준일자'와 '개봉일' 컬럼을 문자열에서 datetime(날짜) 객체로 변환합니다.
    # -------------------------------------------------------------------------
    df['기준일자'] = pd.to_datetime(df['기준일자'])
    df['개봉일'] = pd.to_datetime(df['개봉일'])
    
    # 전체 데이터를 '기준일자' 오름차순(과거 -> 최신)으로 정렬합니다.
    df = df.sort_values(by='기준일자').reset_index(drop=True)
    
    return df

# 데이터 로드 실행
df = load_data()

# -----------------------------------------------------------------------------
# [메인 화면 상단 헤더]
# -----------------------------------------------------------------------------
st.title("🎬 KOBIS 박스오피스 데이터 분석 앱")
st.markdown("1년간의 박스오피스 데이터를 바탕으로 영화별 일관객 수 변화 및 다양한 흥행 지표를 분석합니다.")
st.divider()

# -----------------------------------------------------------------------------
# [3. 영화 선택 기능 (사이드바)]
# 사용자가 조작하는 필터 메뉴를 좌측 사이드바에 배치합니다.
# -----------------------------------------------------------------------------
st.sidebar.header("🔍 영화 검색 및 선택")

# '영화명' 컬럼에서 중복 요소를 제거(unique)하고 가나다순으로 정렬합니다.
movie_list = sorted(df['영화명'].unique())

# 목록에서 영화를 고를 수 있는 드롭다운 메뉴(selectbox) 생성
selected_movie = st.sidebar.selectbox(
    "조회할 영화를 선택하세요:",
    options=movie_list
)

# -----------------------------------------------------------------------------
# [4. 구역 1: 선 그래프 (일관객수 변화)]
# 앞으로 새로운 그래프를 계속 추가할 수 있도록 구역(Section)으로 분리합니다.
# -----------------------------------------------------------------------------
st.header(f"📊 [{selected_movie}] 날짜별 일관객수 변화")

# 사용자가 선택한 영화 데이터만 추출 (필터링)
movie_df = df[df['영화명'] == selected_movie]

# 일관객수 컬럼명 확인 ('일관객' 또는 '관객수')
target_col = '일관객' if '일관객' in movie_df.columns else '관객수'

if not movie_df.empty:
    # Plotly 라인(선) 그래프 생성
    fig = px.line(
        movie_df,
        x='기준일자',
        y=target_col,
        title=f"'{selected_movie}' 기준일자별 일관객수 추이",
        labels={'기준일자': '기준일자', target_col: '일관객수(명)'},
        markers=True  # 각 데이터 지점에 점(Marker) 표시
    )
    
    # 그래프 시각적 스타일 설정
    fig.update_traces(line_color='#E50914', line_width=2.5)  # 선 색상(포인트 레드) 및 두께
    fig.update_layout(
        hovermode="x unified",  # 마우스 호버 시 날짜별 데이터 일괄 표시
        xaxis_title="기준일자",
        yaxis_title="일관객수 (명)",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)
    
    # [그래프 하단 설명 문구 구역]
    st.info(f"💡 **이 그래프로 알 수 있는 것:** 개봉일({movie_df['개봉일'].iloc[0].strftime('%Y-%m-%d')}) 이후 상영 기간에 따른 '{selected_movie}'의 일일 관객수 변동 패턴과 정점(최고 흥행 시점)을 파악할 수 있습니다.")

else:
    st.warning("선택하신 영화의 데이터가 존재하지 않습니다.")

st.divider()

# -----------------------------------------------------------------------------
# [5. 확장용 추가 구역 예시]
# 앞으로 새로운 차트나 통계를 쉽게 덧붙일 수 있도록 예시 구역을 조성했습니다.
# -----------------------------------------------------------------------------
st.header("📈 주요 흥행 지표 요약 (추가 구역 예시)")

with st.container():
    st.subheader("📌 관객 수 핵심 요약")
    
    # 카드 형태의 지표(Metric) 3개 배치
    if not movie_df.empty:
        col1, col2, col3 = st.columns(3)
        
        total_days = len(movie_df)
        max_audience = movie_df[target_col].max()
        avg_audience = int(movie_df[target_col].mean())
        
        col1.metric("총 차트인 일수", f"{total_days} 일")
        col2.metric("최대 일관객수", f"{max_audience:,} 명")
        col3.metric("평균 일관객수", f"{avg_audience:,} 명")
    
    # 추가 구역의 하단 설명 문구 자리
    st.info("💡 **이 그래프로 알 수 있는 것:** 해당 영화의 상영 기간 동안의 평균 관객수와 최고 관객수를 한눈에 비교하여 전반적인 흥행 규모를 파악할 수 있습니다.")
