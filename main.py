
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
        "드라마와 애니메이션의 비율이 다른 종류보다 높다는 것을 알 수 있다."
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
        "어떤 장르에서 한 영화를 많이 본 관객들의 수를 알 수 있다."
    )
# ==================================================
# 3. 총 관객 수 히스토그램
# ==================================================
st.subheader("3. 영화별 총 관객 수 분포")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    title="총 관객 수 분포",
    labels={"total_audi": "총 관객 수", "count": "영화 편수"}
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    height=500,
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 관객이 많은 영화
max_movie = df.loc[df["total_audi"].idxmax(), "movieNm"]
max_audi = df["total_audi"].max()

# 가장 많이 몰린 구간
counts, bins = pd.cut(
    df["total_audi"],
    bins=20,
    retbins=True
)
most_common_bin = counts.value_counts().idxmax()

with st.container(border=True):
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.write(
        f"대부분의 영화는 **{most_common_bin.left:,.0f}명~{most_common_bin.right:,.0f}명** "
        f"구간에 몰려 있으며, 가장 관객이 많은 영화는 **{max_movie}** "
        f"({max_audi:,.0f}명)이다."
    )
# ==================================================
# 4. 개봉일 스크린 수와 총 관객 수의 관계
# ==================================================
st.subheader("4. 개봉일 스크린 수와 총 관객 수의 관계")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,.0f",
        "total_audi": ":,.0f",
        "genre": True
    },
    title="개봉일 스크린 수와 총 관객 수",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "genre": "장르"
    }
)

fig4.update_traces(
    marker=dict(size=9, opacity=0.75)
)

fig4.update_layout(
    height=550,
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig4, use_container_width=True)

with st.container(border=True):
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.write(
        "점에 마우스를 올리면 영화의 이름과 그 영화의 장르를 확인할 수 있다."
    )
# ==================================================
# 5. 장르별 총 관객 수 상자 그림
# ==================================================
st.subheader("5. 장르별 총 관객 수 분포")

# 영화가 10편 이상인 장르만 선택
genre_counts = df["genre"].value_counts()
selected_genres = genre_counts[genre_counts >= 10].index

boxplot_df = df[df["genre"].isin(selected_genres)].copy()

fig5 = px.box(
    boxplot_df,
    x="genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    hover_data={
        "genre": True,
        "total_audi": ":,.0f"
    },
    title="영화가 10편 이상인 장르의 총 관객 수 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객 수"
    }
)

fig5.update_traces(
    marker=dict(size=8)
)

fig5.update_layout(
    height=550,
    xaxis_title="장르",
    yaxis_title="총 관객 수",
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig5, use_container_width=True)

with st.container(border=True):
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.write(
        "상자 밖으로 표시되는 점에 마우스를 올리면 해당 영화명을 확인할 수 있습니다."
    )
# ==================================================
# 6. 첫 주 관객을 크기로 표현한 버블 그래프
# ==================================================
st.subheader("6. 개봉일 스크린 수와 총 관객 수의 관계 — 첫 주 관객 버블")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    hover_data={
        "first_scrn": ":,.0f",
        "first_week_audi": ":,.0f",
        "total_audi": ":,.0f",
        "genre": True
    },
    size_max=50,
    title="개봉일 스크린 수 × 총 관객 수 × 첫 주 관객",
    labels={
        "first_scrn": "개봉일 스크린 수",
        "total_audi": "총 관객 수",
        "first_week_audi": "첫 주 관객",
        "genre": "장르"
    }
)

fig6.update_traces(
    marker=dict(
        opacity=0.7,
        line=dict(width=1)
    )
)

fig6.update_layout(
    height=550,
    xaxis_title="개봉일 스크린 수",
    yaxis_title="총 관객 수",
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig6, use_container_width=True)

with st.container(border=True):
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.write(
        "버블 크기를 통해 첫 주 관객 규모까지 함께 비교할 수 있다."
    )
# ==================================================
# 7. 제작 국가 → 장르 선버스트 그래프
# ==================================================
st.subheader("7. 제작 국가와 장르별 영화 구성")

sunburst_df = (
    df.groupby(["nation", "genre"])
    .size()
    .reset_index(name="movie_count")
)

fig7 = px.sunburst(
    sunburst_df,
    path=["nation", "genre"],
    values="movie_count",
    title="제작 국가 → 장르별 영화 편수",
    labels={
        "nation": "제작 국가",
        "genre": "장르",
        "movie_count": "영화 편수"
    }
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    height=600,
    margin=dict(t=60, b=20, l=20, r=20)
)

st.plotly_chart(fig7, use_container_width=True)

with st.container(border=True):
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.write(
        "제작 국가별로 어떤 장르의 영화가 많이 만들어졌는지 "
        "영화 편수를 기준으로 한눈에 비교할 수 있다. "
    )
