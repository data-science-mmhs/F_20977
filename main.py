import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 기본 설정 (넓은 화면 레이아웃)
st.set_page_config(page_title="영화 박스오피스 대시보드", layout="wide")

# App 제목
st.title("🎬 KOBIS 영화 박스오피스 데이터 분석")

# [1. 데이터 불러오기 및 재사용 설정]
# @st.cache_data를 사용하면 데이터를 매번 새로 불러오지 않고 저장해둔 캐시를 사용합니다.
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)
    
    # [2. 데이터 전처리]
    # 결측치(빈 값)가 하나라도 포함된 행 삭제
    df = df.dropna()
    
    # "기준일자"와 "개봉일" 컬럼을 날짜(datetime) 형식으로 변환
    df['기준일자'] = pd.to_datetime(df['기준일자'].astype(str))
    df['개봉일'] = pd.to_datetime(df['개봉일'].astype(str))
    
    # 기준일자 오름차순으로 전체 데이터 정렬
    df = df.sort_values(by='기준일자')
    
    return df

# 데이터 로드 실행
df = load_data()

# [3. 영화 선택 기능]
# 중복 없이 영화명 목록을 가져오기
movie_list = df['영화명'].unique()

# 사이드바에 영화 선택 드롭다운 생성
st.sidebar.header("🎯 조건 선택")
selected_movie = st.sidebar.selectbox("분석할 영화를 선택하세요:", movie_list)

# 선택한 영화의 데이터만 필터링
filtered_df = df[df['영화명'] == selected_movie]

# 메인 화면 영역 나누기
st.markdown("---")

# [4. 선그래프 구역]
st.subheader(f"📊 '{selected_movie}' 날짜별 일관객수 변화")

# Plotly 선그래프 그리기 (X축: 기준일자, Y축: 일관객수)
fig = px.line(
    filtered_df,
    x='기준일자',
    y='일관객수',
    title=f"<{selected_movie}> 일관객수 추이",
    labels={'기준일자': '날짜', '일관객수': '일일 관객수(명)'},
    markers=True  # 데이터 지점에 점 표시
)

# 그래프 화면 출력
st.plotly_chart(fig, use_container_width=True)

# [5. 기타 - 그래프 설명 문구 영역]
st.info("💡 **이 그래프로 알 수 있는 것:** 선택한 영화의 개봉 이후 날짜별 관객수 증감 추이와 흥행 유지 기간을 한눈에 파악할 수 있습니다.")

st.markdown("---")

# [추후 그래프 추가 구역 예시]
st.subheader("📌 2번 그래프 구역 (추후 추가 예정)")
st.write("새로운 그래프가 추가될 영역입니다.")

# 추가될 그래프 아래 문구 영역 예시
st.caption("💡 **이 그래프로 알 수 있는 것:** (추후 추가되는 분석 내용 설명 작성 위치)")
