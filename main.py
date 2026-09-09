import streamlit as st
import pandas as pd

# 앱의 메인 제목을 설정합니다.
st.title("🎬 영화 관객수 추이 대시보드")

# [1. 데이터 불러오기 & 2. 날짜 전처리]
# @st.cache_data 데코레이터: 데이터를 한 번만 불러오고 메모리에 저장(캐싱)합니다.
# 앱을 새로고침하거나 옵션을 변경할 때마다 대용량 데이터를 다시 다운로드하지 않도록 막아주어 앱 속도를 빠르게 유지합니다.
@st.cache_data
def load_data():
    # URL에서 CSV 데이터를 pandas 데이터프레임으로 불러옵니다.
    url = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"
    df = pd.read_csv(url)
    
    # "기준일자"와 "개봉일" 컬럼의 데이터를 텍스트(문자열)에서 날짜(datetime) 형식으로 변환합니다.
    df['기준일자'] = pd.to_datetime(df['기준일자'])
    df['개봉일'] = pd.to_datetime(df['개봉일'])
    
    # "기준일자"를 기준으로 전체 데이터를 오름차순 정렬(과거 -> 최신)합니다.
    df = df.sort_values(by='기준일자')
    
    return df

# 위에서 만든 함수를 실행하여 전처리가 끝난 데이터를 가져옵니다.
df = load_data()


# [3. 영화 선택 기능]
st.subheader("1️⃣ 영화 선택")

# "영화명" 컬럼에서 중복을 제거(unique)하여 영화 이름들의 목록을 만듭니다.
movie_list = df['영화명'].unique()

# 사용자가 영화를 선택할 수 있도록 드롭다운(selectbox) 메뉴를 만듭니다.
selected_movie = st.selectbox("데이터를 확인할 영화를 선택해 주세요:", movie_list)

# 전체 데이터에서 사용자가 선택한 영화의 데이터만 골라냅니다(필터링).
filtered_df = df[df['영화명'] == selected_movie]


# [4. 선그래프 그리기]
st.divider() # 화면을 시각적으로 나누기 위한 가로 구분선을 추가합니다.
st.subheader(f"2️⃣ 『{selected_movie}』 일일 관객수 추이")

# 스트림릿에 기본 내장된 선그래프(line_chart)를 그립니다.
# x축은 '기준일자'(날짜), y축은 '해당관객수'(일일 관객수)로 설정합니다.
st.line_chart(data=filtered_df, x='기준일자', y='해당관객수')


# [5. 기타 - 향후 그래프 추가 영역]
st.divider() # 가로 구분선 추가
st.subheader("3️⃣ 추가 분석 영역 (예정)")

# 안내 메시지 박스를 띄워 차후 업데이트될 영역임을 표시합니다.
st.info("💡 이곳에 누적 관객수 추이나 다른 영화와의 비교 그래프 등 추가 데이터를 배치할 수 있습니다.")
