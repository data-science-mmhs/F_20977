import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정 (웹 브라우저 탭 제목 및 레이아웃 설정)
st.set_page_config(page_title="영화 박스오피스 분석 대시보드", layout="wide")

# App 제목 설정
st.title("🎬 영화 박스오피스 데이터 분석 대시보드")
st.caption("KOBIS 1개년 박스오피스 데이터를 바탕으로 한 관객 수 추이 분석 앱입니다.")

# 2. 데이터 불러오기 및 전처리 (캐싱 적용)
# @st.cache_data는 데이터를 한 번 읽어온 뒤 메모리에 저장해두어 앱 실행 속도를 높여줍니다.
@st.cache_data
def load_and_preprocess_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    
    # CSV 데이터 불러오기
    df = pd.read_csv(url)
    
    # [전처리 1] 결측치가 포함된 행 제거
    df = df.dropna()
    
    # [전처리 2] '기준일자' 및 '개봉일' 컬럼을 datetime(날짜) 형식으로 변환
    df['기준일자'] = pd.to_datetime(df['기준일자'])
    df['개봉일'] = pd.to_datetime(df['개봉일'])
    
    # [전처리 3] 전체 데이터를 기준일자 순서대로 정렬 (오름차순)
    df = df.sort_values(by='기준일자').reset_index(drop=True)
    
    return df

# 데이터 로드
df = load_and_preprocess_data()

# ---------------------------------------------------------
# [구역 1] 영화별 관객 수 추이 분석
# ---------------------------------------------------------
st.header("1. 영화별 일관객 수 변화 추이")

# 3. 영화 선택 기능
# 중복 없는 영화 이름 목록 추출
movie_list = df['영화명'].unique()

# 사용자 선택을 위한 셀렉트박스 생성
selected_movie = st.selectbox(
    "📊 분석할 영화를 선택하세요:",
    options=movie_list
)

# 선택한 영화 데이터만 필터링
filtered_df = df[df['영화명'] == selected_movie]

# 관객 수 컬럼 자동 감지 (데이터셋 컬럼명 유연 대응: '일관객수', '일관객', '관객수' 등)
target_col = None
for col in ['일관객수', '일관객', '관객수']:
    if col in filtered_df.columns:
        target_col = col
        break

# 관객 수 컬럼이 존재하는 경우 그래프 생성
if target_col:
    # 4. Plotly 선 그래프 생성
    fig = px.line(
        filtered_df,
        x='기준일자',
        y=target_col,
        title=f"<{selected_movie}> 기준일자별 일관객 수 변화",
        labels={'기준일자': '날짜', target_col: '일일 관객 수'},
        markers=True  # 그래프 선 위에 데이터 점 표시
    )
    
    # 그래프 선 및 레이아웃 스타일 설정
    fig.update_traces(line_color="#FF4B4B")
    fig.update_layout(hovermode="x unified")
    
    # Streamlit 화면에 그래프 출력
    st.plotly_chart(fig, use_container_width=True)
    
    # 5. 그래프 설명 문구 영역
    st.info(f"💡 **이 그래프로 알 수 있는 것:** '{selected_movie}'의 개봉 이후 관객 수 증감 추이와 최고 관객 수를 기록한 시점을 확인할 수 있습니다.")

else:
    st.warning("관객 수 관련 컬럼을 찾을 수 없습니다. 데이터 컬럼명을 확인해주세요.")

# 구분선 추가
st.divider()

# ---------------------------------------------------------
# [구역 2] 추후 추가될 그래프 구역 (확장용 공간)
# ---------------------------------------------------------
st.header("2. 추가 분석 구역 (예정)")
st.write("앞으로 추가할 차트 및 분석 항목이 이 구역에 들어갈 예정입니다.")

# 향후 추가될 그래프의 예시 프레임
with st.container():
    st.subheader("📌 [예시] 주말 vs 평일 관객 비교 (준비 중)")
    # 추후 차트 코드 삽입 영역
    
    # 그래프 설명 문구 자리를 미리 확보
    st.info("💡 **이 그래프로 알 수 있는 것:** (추후 추가될 그래프에 대한 설명 문구가 들어갈 자리입니다.)")
