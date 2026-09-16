
import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 장르가 여러 개라면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미상")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 총 관객 수 숫자형 변환
    df["total_audi"] = pd.to_numeric(
        df["total_audi"],
        errors="coerce"
    )

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.code(str(e))
    st.stop()


# --------------------------------------------------
# 제목
# --------------------------------------------------
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")

st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데 "
    "이 기간에 개봉한 216편의 데이터를 살펴봅니다."
)


# ==================================================
# 1. 장르별 영화 편수
# ==================================================
st.subheader("1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .reset_index()
)

genre_counts.columns = ["장르", "영화 편수"]

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.55,
    title="장르별 영화 편수"
)

fig1.update_traces(
    textinfo="percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    height=500,
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig1, use_container_width=True)

with st.container(border=True):
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.write(
        "장르별로 전체 영화에서 차지하는 편수와 비율을 비교할 수 있습니다."
    )


# ==================================================
# 2. 장르 → 영화 트리맵
# ==================================================
st.subheader("2. 장르별 영화 관객 수")

treemap_df = df[
    ["genre", "movieNm", "total_audi"]
].copy()

# 영화명이나 관객 수가 없는 행 제외
treemap_df = treemap_df.dropna(
    subset=["genre", "movieNm", "total_audi"]
)

# 총 관객 수가 0보다 큰 영화만 사용
treemap_df = treemap_df[treemap_df["total_audi"] > 0]

fig2 = px.treemap(
    treemap_df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화의 총 관객 수"
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    height=700,
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig2, use_container_width=True)

with st.container(border=True):
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.write(
        "장르 안에서 영화별 총 관객 규모를 비교하고, 어떤 영화가 많은 관객을 모았는지 살펴볼 수 있습니다."
    )
