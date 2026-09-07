import datetime
import os
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="KOBIS 일별 박스오피스",
    page_icon="🎬",
    layout="wide"
)

# ---------------------------------------------------------
# [한글 폰트 설정] 로컬 및 Streamlit Cloud 지원
# ---------------------------------------------------------
@st.cache_resource
def set_korean_font():
    """OS별 한글 폰트를 설정하고, 폰트가 없을 경우 나눔고딕을 다운로드하여 적용합니다."""
    import platform
    system_name = platform.system()

    if system_name == 'Windows':
        font_name = 'Malgun Gothic'
        plt.rc('font', family=font_name)
    elif system_name == 'Darwin':  # Mac
        font_name = 'AppleGothic'
        plt.rc('font', family=font_name)
    else:  # Linux (Streamlit Community Cloud)
        font_dir = os.path.join(os.getcwd(), ".fonts")
        os.makedirs(font_dir, exist_ok=True)
        font_path = os.path.join(font_dir, "NanumGothic.ttf")

        if not os.path.exists(font_path):
            url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
            res = requests.get(url, timeout=10)
            with open(font_path, "wb") as f:
                f.write(res.content)

        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        plt.rc('font', family=font_prop.get_name())

    # 마이너스 기호 깨짐 방지 및 글로벌 스타일 테마 설정
    plt.rcParams['axes.unicode_minus'] = False
    plt.style.use('seaborn-v0_8-whitegrid')

# 한글 폰트 설정 실행
set_korean_font()


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

    # 날짜 선택 (어제 날짜를 기본값으로 설정)
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

        # ---------------------------------------------------------
        # 2. 매출액 기준 막대그래프 출력 (디자인 개선)
        # ---------------------------------------------------------
        st.subheader("📊 매출액 기준 Top 10 그래프")
        
        chart_df = display_df.sort_values("순위", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 6))
        
        sales_in_hundred_millions = chart_df["당일 매출액(원)"] / 100_000_000
        
        # 세련된 블루 톤 적용 및 테두리 정제
        bars = ax.barh(
            chart_df["영화명"], 
            sales_in_hundred_millions, 
            color="#4C72B0", 
            edgecolor="none",
            height=0.65
        )
        
        ax.set_xlabel("당일 매출액 (억 원)", fontsize=11, fontweight='bold', labelpad=10)
        ax.set_ylabel("영화명", fontsize=11, fontweight='bold', labelpad=10)
        ax.set_title(f"일별 매출액 현황 ({selected_date.strftime('%Y-%m-%d')})", fontsize=14, fontweight='bold', pad=15)
        
        # 테두리 가공 및 격자 스타일 설정
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cccccc')
        ax.spines['bottom'].set_color('#cccccc')
        ax.grid(axis='x', linestyle=':', alpha=0.6)

        # 수치 레이블 표시
        max_sales = max(sales_in_hundred_millions)
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (max_sales * 0.015), 
                bar.get_y() + bar.get_height() / 2, 
                f"{width:.1f}억", 
                va='center', 
                fontsize=9.5,
                color="#333333",
                fontweight='bold'
            )

        plt.tight_layout()
        st.pyplot(fig)

        st.markdown("---")

        # ---------------------------------------------------------
        # 3. 관객수 vs 매출액 관계 산점도 출력 (디자인 개선)
        # ---------------------------------------------------------
        st.subheader("📈 관객수 vs 매출액 관계 (산점도)")

        fig2, ax2 = plt.subplots(figsize=(10, 6))

        audi_in_thousands = display_df["당일 관객수(명)"] / 10_000  # 만 명 단위
        sales_in_hundred_millions_sc = display_df["당일 매출액(원)"] / 100_000_000  # 억 원 단위

        ax2.scatter(
            audi_in_thousands, 
            sales_in_hundred_millions_sc, 
            color="#DD8452", 
            s=120, 
            alpha=0.85, 
            edgecolors="white",
            linewidth=1.5,
            zorder=3
        )

        # 각 점 옆에 영화명 주석 표시 (가독성 향상)
        for idx, row in display_df.iterrows():
            x_val = row["당일 관객수(명)"] / 10_000
            y_val = row["당일 매출액(원)"] / 100_000_000
            ax2.annotate(
                row["영화명"], 
                (x_val, y_val), 
                xytext=(7, 4), 
                textcoords="offset points", 
                fontsize=9,
                color="#222222"
            )

        ax2.set_xlabel("당일 관객수 (만 명)", fontsize=11, fontweight='bold', labelpad=10)
        ax2.set_ylabel("당일 매출액 (억 원)", fontsize=11, fontweight='bold', labelpad=10)
        ax2.set_title(f"관객수와 매출액의 상관관계 ({selected_date.strftime('%Y-%m-%d')})", fontsize=14, fontweight='bold', pad=15)
        
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(True, linestyle=':', alpha=0.6)

        plt.tight_layout()
        st.pyplot(fig2)

        st.markdown("---")

        # ---------------------------------------------------------
        # 4. 영화별 매출 점유율 파이 차트 출력 (디자인 개선)
        # ---------------------------------------------------------
        st.subheader("🥧 영화별 매출 점유율 (파이 차트)")

        fig3, ax3 = plt.subplots(figsize=(8, 8))

        sales_share = df["salesShare"].astype(float)
        labels = df["movieNm"]

        # 세련된 파스텔 톤 팔레트 사용
        colors = plt.cm.Set3(range(len(labels)))

        wedges, texts, autotexts = ax3.pie(
            sales_share,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            pctdistance=0.78,
            colors=colors,
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)  # 도넛 형태 및 경계선
        )

        # 수치 및 레이블 텍스트 스타일 조정
        for text in texts:
            text.set_fontsize(9.5)
            text.set_color("#333333")
        for autotext in autotexts:
            autotext.set_fontsize(8.5)
            autotext.set_weight("bold")
            autotext.set_color("#222222")

        ax3.set_title(f"영화별 매출 점유율 ({selected_date.strftime('%Y-%m-%d')})", fontsize=14, fontweight='bold', pad=15)
        
        plt.tight_layout()
        st.pyplot(fig3)

        st.markdown("---")

        # ---------------------------------------------------------
        # 5. 관객수 기준 상위 5개 영화 막대그래프 출력 (디자인 개선)
        # ---------------------------------------------------------
        st.subheader("🔥 당일 관객수 Top 5 영화")

        top5_audi_df = display_df.sort_values("당일 관객수(명)", ascending=False).head(5)

        fig4, ax4 = plt.subplots(figsize=(10, 5))

        top5_audi_in_thousands = top5_audi_df["당일 관객수(명)"] / 10_000
        
        # 그린 톤 컬러 적용
        bars4 = ax4.bar(
            top5_audi_df["영화명"], 
            top5_audi_in_thousands, 
            color="#55A868", 
            width=0.5,
            edgecolor="none"
        )

        ax4.set_xlabel("영화명", fontsize=11, fontweight='bold', labelpad=10)
        ax4.set_ylabel("당일 관객수 (만 명)", fontsize=11, fontweight='bold', labelpad=10)
        ax4.set_title(f"관객수 Top 5 영화 현황 ({selected_date.strftime('%Y-%m-%d')})", fontsize=14, fontweight='bold', pad=15)
        
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.spines['left'].set_color('#cccccc')
        ax4.spines['bottom'].set_color('#cccccc')
        ax4.grid(axis='y', linestyle=':', alpha=0.6)

        # 막대 위에 수치 레이블 추가
        max_audi = max(top5_audi_in_thousands)
        for bar in bars4:
            height = bar.get_height()
            ax4.text(
                bar.get_x() + bar.get_width() / 2,
                height + (max_audi * 0.02),
                f"{height:.1f}만 명",
                ha='center',
                va='bottom',
                fontsize=9.5,
                color="#333333",
                fontweight='bold'
            )

        plt.xticks(rotation=0, ha='center', fontsize=9.5)
        plt.tight_layout()
        st.pyplot(fig4)

    except requests.exceptions.HTTPError as err:
        st.error(f"API 요청에 실패했습니다: {err}")
    except Exception as e:
        st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    main()
