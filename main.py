import datetime
import zoneinfo
import requests
import pandas as pd
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(page_title="일별 박스오피스 조회", layout="wide")


# 1시간 동안 API 응답 결과를 기억(캐싱)하는 함수
@st.cache_data(ttl=3600)
def fetch_box_office(target_dt, api_key):
    """KOBIS API를 호출하여 해당 날짜의 박스오피스 데이터를 가져오는 함수"""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_dt}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def main():
    st.title("🎬 일별 박스오피스 순위")

    # 1. secrets.toml 파일에서 KOBIS API 키 불러오기
    if "KOBIS_KEY" not in st.secrets:
        st.error(
            "🔑 Secrets 설정에서 'KOBIS_KEY'를 찾을 수 없습니다.\n\n"
            "**조치 방법:**\n"
            "1. Streamlit Cloud 앱 설정의 Secrets 항목으로 이동하세요.\n"
            '2. `KOBIS_KEY = "발급받은_키_문자열"` 형태로 등록해 주세요.'
        )
        return

    api_key = st.secrets["KOBIS_KEY"]

    # 2. 한국 시간(Asia/Seoul) 기준 계산 및 최대 선택 가능 날짜(어제) 설정
    korea_tz = zoneinfo.ZoneInfo("Asia/Seoul")
    today = datetime.datetime.now(korea_tz).date()
    max_selectable_date = today - datetime.timedelta(days=1)  # 어제까지 선택 가능

    # 3. 달력(date_input)으로 날짜 선택 기능 추가
    selected_date = st.date_input(
        "📅 조회할 날짜를 선택하세요",
        value=max_selectable_date,
        max_value=max_selectable_date,  # 오늘 이후 날짜 선택 불가
        min_value=datetime.date(2004, 1, 1),  # KOBIS 제공 최소 연도
    )

    # API 호출용 YYYYMMDD 포맷으로 변환
    target_dt = selected_date.strftime("%Y%m%d")
    formatted_date = selected_date.strftime("%Y년 %m월 %d일")

    st.caption(f"기준 날짜: {formatted_date}")

    # 4. API 데이터 호출
    data = fetch_box_office(target_dt, api_key)

    # 5. 예외 및 에러 처리 안내
    if data is None:
        st.error(
            "📡 KOBIS 서버와 통신하는 중 네트워크 오류가 발생했습니다.\n\n"
            "잠시 후 다시 시도해 주세요."
        )
        return

    # API 인증 키 오류 등으로 faultInfo가 전달된 경우
    if "faultInfo" in data:
        fault = data["faultInfo"]
        st.error(
            "⚠️ KOBIS API 응답 에러가 발생했습니다.\n\n"
            f"- **오류 코드:** {fault.get('errorCode', 'N/A')}\n"
            f"- **오류 메시지:** {fault.get('message', 'N/A')}\n\n"
            "**조치 방법:** Secrets에 등록한 KOBIS_KEY가 올바른지 확인해 주세요."
        )
        return

    box_office_result = data.get("boxOfficeResult", {})
    daily_list = box_office_result.get("dailyBoxOfficeList", [])

    # 영화 목록이 비어 있는 경우
    if not daily_list:
        st.warning("⚠️ 그날은 아직 집계 전입니다.")
        return

    # 6. 데이터 처리 (문자열 -> 숫자 변환)
    df = pd.DataFrame(daily_list)

    numeric_cols = [
        "rank",
        "rankInten",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
        "showCnt",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 7. 요구사항 가공 처리

    # 7-1. rankInten(순위 증감)을 기반으로 화살표와 변동 폭 기호 생성
    def format_rank_inten(val):
        val = int(val)
        if val > 0:
            return f"🔺 {val}"  # 상승 (빨간 위 화살표)
        elif val < 0:
            return f"🔹 {abs(val)}"  # 하강 (파란 아래 화살표)
        else:
            return "-"  # 변동 없음

    df["순위변동"] = df["rankInten"].apply(format_rank_inten)

    # 7-2. 누적관객 100만 명 이상 영화명 옆에 🏆 이모지 추가
    def format_movie_title(row):
        title = row["movieNm"]
        if row["audiAcc"] >= 1_000_000:
            return f"{title} 🏆"
        return title

    df["표시_영화명"] = df.apply(format_movie_title, axis=1)

    # 8. 1위 영화 하이라이트 지표 카드 표시
    top_movie = df.iloc[0]
    st.subheader(f"🥇 1위 영화: {top_movie['표시_영화명']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="당일 관객수", value=f"{int(top_movie['audiCnt']):,} 명"
        )
    with col2:
        st.metric(
            label="누적 관객수", value=f"{int(top_movie['audiAcc']):,} 명"
        )
    with col3:
        st.metric(
            label="스크린수", value=f"{int(top_movie['scrnCnt']):,} 개"
        )

    st.markdown("---")

    # 9. 관객수 상위 5편 막대그래프 표시 (원본 영화명 사용)
    st.subheader("📊 관객수 상위 5개 영화")
    top5_df = df.head(5).sort_values(by="audiCnt", ascending=True)

    st.bar_chart(data=top5_df, x="movieNm", y="audiCnt", color="#FF4B4B")

    st.markdown("---")

    # 10. 박스오피스 전체 순위 표 표시
    st.subheader("📋 박스오피스 전체 순위")

    display_df = df[
        [
            "rank",
            "순위변동",
            "표시_영화명",
            "openDt",
            "audiCnt",
            "audiAcc",
            "scrnCnt",
        ]
    ].copy()
    display_df.columns = [
        "순위",
        "전날 대비",
        "영화명",
        "개봉일",
        "당일 관객수",
        "누적 관객수",
        "스크린수",
    ]

    st.dataframe(
        display_df,
        column_config={
            "순위": st.column_config.NumberColumn(format="%d위"),
            "당일 관객수": st.column_config.NumberColumn(format="%d명"),
            "누적 관객수": st.column_config.NumberColumn(format="%d명"),
            "스크린수": st.column_config.NumberColumn(format="%d개"),
        },
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
