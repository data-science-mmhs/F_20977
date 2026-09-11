import datetime
import zoneinfo
import requests
import pandas as pd
import streamlit as st

# 페이지 기본 설정 (타이틀, 레이아웃)
st.set_page_config(page_title="어제 박스오피스 순위", layout="wide")


# 1시간 동안 API 응답 결과를 기억(캐싱)하는 함수
# 같은 날짜로 다시 요청할 때 API를 중복 호출하지 않습니다.
@st.cache_data(ttl=3600)
def fetch_box_office(target_dt, api_key):
    """KOBIS API를 호출하여 해당 날짜의 박스오피스 데이터를 가져오는 함수"""
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_dt}

    try:
        # API 요청 보내기 (타임아웃 10초 설정)
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
        return response.json()
    except requests.exceptions.RequestException as e:
        # 네트워크 오류 등 요청 실패 시 None 반환
        return None


def main():
    st.title("🎬 어제 일별 박스오피스 순위")

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

    # 2. 배포 서버의 시계와 무관하게 '한국 시간(Asia/Seoul)' 기준 어제 날짜 계산
    korea_tz = zoneinfo.ZoneInfo("Asia/Seoul")
    yesterday = datetime.datetime.now(korea_tz) - datetime.timedelta(days=1)
    target_dt = yesterday.strftime("%Y%m%d")
    formatted_date = yesterday.strftime("%Y년 %m월 %d일")

    st.caption(f"📅 기준 날짜: {formatted_date} (한국 시간 기준)")

    # 3. API 데이터 호출
    data = fetch_box_office(target_dt, api_key)

    # 4. 예외 및 에러 처리 안내
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
        st.warning(
            "⚠️ 검색된 박스오피스 영화 목록이 없습니다.\n\n"
            "**확인 사항:**\n"
            "1. KOBIS 서비스에 해당 날짜의 데이터가 아직 집계되지 않았을 수 있습니다.\n"
            "2. 일일 조회 한도를 초과했는지 확인해 주세요."
        )
        return

    # 5. 데이터 처리 (문자열 -> 숫자 변환)
    df = pd.DataFrame(daily_list)

    # 정렬 및 그래프에 활용할 수 있도록 숫자형 데이터 타입으로 변환
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

    # 6. 1위 영화 하이라이트 지표 카드 표시
    top_movie = df.iloc[0]
    st.subheader(f"🥇 1위 영화: {top_movie['movieNm']}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="어제 관객수", value=f"{int(top_movie['audiCnt']):,} 명"
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

    # 7. 관객수 상위 5편 막대그래프 표시
    st.subheader("📊 관객수 상위 5개 영화")
    top5_df = df.head(5).sort_values(by="audiCnt", ascending=True)

    # Streamlit 기본 막대그래프 생성
    st.bar_chart(data=top5_df, x="movieNm", y="audiCnt", color="#FF4B4B")

    st.markdown("---")

    # 8. 박스오피스 전체 순위 표 표시
    st.subheader("📋 박스오피스 전체 순위")

    # 표시할 컬럼 선택 및 이름 변경
    display_df = df[
        ["rank", "movieNm", "openDt", "audiCnt", "audiAcc", "scrnCnt"]
    ].copy()
    display_df.columns = [
        "순위",
        "영화명",
        "개봉일",
        "어제 관객수",
        "누적 관객수",
        "스크린수",
    ]

    # 표 출력 (숫자 세파레이터 포맷 지정)
    st.dataframe(
        display_df,
        column_config={
            "순위": st.column_config.NumberColumn(format="%d위"),
            "어제 관객수": st.column_config.NumberColumn(format="%d명"),
            "누적 관객수": st.column_config.NumberColumn(format="%d명"),
            "스크린수": st.column_config.NumberColumn(format="%d개"),
        },
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
