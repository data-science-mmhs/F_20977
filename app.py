import datetime
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="KOBIS 일별 박스오피스",
    page_icon="🎬",
    layout="wide"
)

# Matplotlib 한글 폰트 설정 (OS별)
import platform
if platform.system() == 'Darwin': # Mac
    plt.rc('font', family='AppleGothic')
elif platform.system() == 'Windows': # Windows
    plt.rc('font', family='Malgun Gothic')
else: # Linux / Streamlit Community Cloud
    plt.rc('font', family='NanumGothic')

# 마이너스 폰트 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False


@st.cache_data(ttl=3600)
def fetch_box_office_data(api_key: str, target_date: str) -> list:
    """KOBIS API를 통해 지정된 날짜의 일별 박스오피스 데이터를 가져옵니다."""
    url = "http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {
        "key": api_key,
        "targetDt": target_date
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    return data.get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])


def main():
    st.title("🎬 일별 박스오피스 조회")
    st.write("영화진흥위원회(KOBIS) API를 활용한 데이터 시각화")

    # API 키 확인
    if "KOBIS_KEY" not in st.secrets:
        st.error("🔑 `st.secrets`에 `KOBIS_KEY`가 설정되어 있지 않습니다.")
        st.info("`.streamlit/secrets.toml` 파일에 `KOBIS_KEY = '발급받은_키'`를 추가해주세요.")
        return

    api_key = st.secrets["KOBIS_KEY"]

    # 날짜 선택 (어제 날짜를 기본값으로 설정 - 당일 데이터는 집계 전일 수 있음)
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    selected_date = st.date_input("조회할 날짜를 선택하세요", value=yesterday, max_value=yesterday)

    target_date_str = selected_date.strftime("%Y%m%d")

    # 데이터 로드
    try:
        raw_data = fetch_box_office_data(api_key, target_date_str)
        
        if not raw_data:
            st.warning("해당 날짜의 박스오피스 데이터가 존재하지 않습니다.")
            return

        # DataFrame 가공
        df = pd.DataFrame(raw_data)
        
        # 주요 컬럼 추출 및 타입 변환
        display_df = pd.DataFrame({
            "순위": df["rank"].astype(int),
            "영화명": df["movieNm"],
            "개봉일": df["openDt"],
            "당일 매출액(원)": df["salesAmt"].astype(int),
            "당일 관객수(명)": df["audiCnt"].astype(int),
            "누적 관객수(명)": df["audiAcc"].astype(int),
            "스크린수": df["scrnCnt"].astype(int)
        }).sort_values("순위")

        # 1. 데이터 표 출력
        st.subheader(f"📌 {selected_date.strftime('%Y년 %m월 %d일')} 박스오피스 Top 10")
        
        st.dataframe(
            display_df,
            column_config={
                "당일 매출액(원)": st.column_config.NumberColumn(format="%d 원"),
                "당일 관객수(명)": st.column_config.NumberColumn(format="%d 명"),
                "누적 관객수(명)": st.column_config.NumberColumn(format="%d 명"),
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # 2. 매출액 기준 막대그래프 출력
        st.subheader("📊 매출액 기준 Top 10 그래프")
        
        # 가로 막대그래프 생성을 위해 순위 역순 정렬
        chart_df = display_df.sort_values("순위", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 매출액 단위를 '억 원'으로 변환하여 시각화 가독성 개선
        sales_in_hundred_millions = chart_df["당일 매출액(원)"] / 100_000_000
        
        bars = ax.barh(chart_df["영화명"], sales_in_hundred_millions, color="#1f77b4")
        
        ax.set_xlabel("당일 매출액 (억 원)", fontsize=11)
        ax.set_ylabel("영화명", fontsize=11)
        ax.set_title(f"일별 매출액 현황 ({selected_date.strftime('%Y-%m-%d')})", fontsize=14, pad=15)
        ax.grid(axis='x', linestyle='--', alpha=0.5)

        # 막대 끝에 수치 표시
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (max(sales_in_hundred_millions) * 0.01), 
                bar.get_y() + bar.get_height() / 2, 
                f"{width:.1f}억", 
                va='center', 
                fontsize=9
            )

        plt.tight_layout()
        st.pyplot(fig)

    except requests.exceptions.HTTPError as err:
        st.error(f"API 요청에 실패했습니다: {err}")
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
