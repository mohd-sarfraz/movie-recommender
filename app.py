import streamlit as st
import pickle
import pandas as pd
import requests

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="WatchNext | AI Movie Discovery",
    page_icon="🎬",
    layout="wide"
)

# ================= CUSTOM CSS =================

st.markdown("""
<style>

/* ================= BACKGROUND ================= */

.stApp {
    background: linear-gradient(
        135deg,
        #020617 0%,
        #0f172a 50%,
        #1e293b 100%
    );
    color: white;
}

/* ================= MAIN CONTAINER ================= */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1250px;
}

/* ================= TITLE ================= */

h1 {
    text-align: center;
    color: #FFD60A;
    font-size: 4.5rem !important;
    font-weight: 900;
    text-shadow: 0 0 25px rgba(255,214,10,0.4);
}

/* ================= MOVIE CARD ================= */

.movie-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px;
    padding: 12px;
    margin-top: 10px;
    margin-bottom: 10px;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

/* ================= MOVIE TEXT ================= */

.movie-title {
    text-align: center;
    font-size: 18px;
    font-weight: 700;
    color: white;
}

.rating {
    text-align: center;
    color: #FFD60A;
    font-weight: bold;
    font-size: 16px;
}

.release {
    text-align: center;
    color: #CBD5E1;
}

/* ================= SELECT BOX ================= */

div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 15px;
}

/* ================= SEARCH BOX ================= */

.stTextInput input {
    background: rgba(255,255,255,0.08);
    color: white;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.15);
}

/* ================= METRIC CARDS ================= */

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid rgba(255,214,10,0.15);
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    text-align: center;
}

/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ================= BUTTON ================= */

.stButton > button {
    background: linear-gradient(
        90deg,
        #FFD60A,
        #FFC300
    );
    color: black;
    border: none;
    border-radius: 15px;
    width: 100%;
    height: 3.4em;
    font-size: 18px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0 0 25px #FFD60A;
}

/* ================= IMAGES ================= */

img {
    border-radius: 18px;
    transition: all 0.3s ease;
}

img:hover {
    transform: scale(1.04);
    box-shadow: 0 0 25px rgba(255,214,10,0.5);
}

/* ================= ALERT ================= */

[data-testid="stAlert"] {
    border-radius: 15px;
}

/* ================= SCROLLBAR ================= */

::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-thumb {
    background: #FFD60A;
    border-radius: 10px;
}

/* ================= HIDE STREAMLIT ================= */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================

st.sidebar.title("🎬 WatchNext")

st.sidebar.markdown("""
### About Project

This Movie Recommendation System suggests movies based on content similarity.

### Technologies Used

- Python
- Pandas
- Scikit-Learn
- Streamlit
- TMDB API

### Recommendation Type

Content-Based Filtering
""")

# ================= LOAD FILES =================

movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))

# ================= TMDB API =================

API_KEY = st.secrets["TMDB_API_KEY"]

# ================= FETCH MOVIE DATA =================

@st.cache_data
def fetch_movie_data(movie_id):

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

        response = requests.get(url, timeout=10)
        data = response.json()

        poster_path = data.get("poster_path")

        if poster_path:
            poster = "https://image.tmdb.org/t/p/w500" + poster_path
        else:
            poster = None

        return {
            "poster": poster,
            "rating": data.get("vote_average", "N/A"),
            "release": data.get("release_date", "N/A"),
            "overview": data.get("overview", "No description available.")
        }

    except:
        return {
            "poster": None,
            "rating": "N/A",
            "release": "N/A",
            "overview": "No description available."
        }

# ================= FETCH TRAILER =================

@st.cache_data
def fetch_trailer(movie_id):

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

        data = requests.get(url, timeout=10).json()

        for video in data.get("results", []):

            if (
                video.get("site") == "YouTube"
                and video.get("type") == "Trailer"
            ):
                return f"https://www.youtube.com/watch?v={video['key']}"

        return None

    except:
        return None

# ================= RECOMMEND FUNCTION =================

def recommend(movie):

    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommendations = []

    for i in movies_list:

        movie_id = movies.iloc[i[0]].movie_id

        movie_data = fetch_movie_data(movie_id)

        recommendations.append({
            "movie_id": movie_id,
            "title": movies.iloc[i[0]].title,
            "poster": movie_data["poster"],
            "rating": movie_data["rating"],
            "release": movie_data["release"],
            "similarity": round(float(i[1]) * 100, 2)
        })

    st.write("Total Recommendations:", len(recommendations))

    return recommendations

# ================= TITLE =================

# ================= TITLE =================

st.markdown("""
<h1 style='text-align:center;color:#FFD60A;font-size:72px;font-weight:900;'>
🎬 WatchNext
</h1>

<h3 style='text-align:center;color:white;font-size:32px;'>
Your Personal AI Movie Discovery Engine
</h3>

<p style='text-align:center;font-size:20px;color:#CBD5E1;'>
Explore blockbuster hits, hidden gems, ratings, trailers and personalized recommendations instantly.
</p>
""", unsafe_allow_html=True)

st.write("")

# ================= DASHBOARD STATS =================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Movies Available", len(movies))

with col2:
    st.metric("Algorithm", "Content-Based")

with col3:
    st.metric("Recommendations", "Top 5")

st.write("")

# ================= MOVIE SELECTION =================
selected_movie = st.selectbox(
    "🎬 Select a Movie",
    movies['title'].values,
    index=None,
    placeholder="Search or select a movie..."
)
# ================= SELECTED MOVIE DETAILS =================

try:

    selected_movie_id = movies[
        movies['title'] == selected_movie
    ].iloc[0].movie_id

    selected_movie_data = fetch_movie_data(selected_movie_id)

    col_left, col_right = st.columns([1, 2])

    with col_left:

        if selected_movie_data["poster"]:
            st.image(
                selected_movie_data["poster"],
                width=300
            )

    with col_right:

        st.subheader(selected_movie)

        st.write(
            f"⭐ Rating: {selected_movie_data['rating']}"
        )

        st.write(
            f"📅 Release Date: {selected_movie_data['release']}"
        )

        st.write("### Overview")

        st.write(
            selected_movie_data["overview"]
        )

        trailer_url = fetch_trailer(selected_movie_id)

        if trailer_url:
            st.link_button(
                "▶️ Watch Trailer",
                trailer_url
            )

except Exception:
    pass

st.write("")

# ================= RECOMMEND BUTTON =================

if st.button("🍿 Find My Next Movie"):

    if selected_movie is None:
        st.warning("⚠️ Please select a movie first.")
        st.stop()

    with st.spinner("🔍 Finding the best movies for you..."):
        recommendations = recommend(selected_movie)

    st.subheader(
        f"✨ Movies You May Love Based On '{selected_movie}'"
    )

    st.write(f"🎬 Found {len(recommendations)} recommendations")

    col1, col2, col3, col4, col5 = st.columns(5)

    cols = [col1, col2, col3, col4, col5]

    for idx, movie in enumerate(recommendations):

        with cols[idx]:

            if idx == 0:
                st.success("🏆 TOP PICK")

            if movie["poster"]:
                st.image(movie["poster"])

            st.markdown(
                f"""
                <div class='movie-card'>
                    <div class='movie-title'>{movie['title']}</div>
                    <div class='rating'>⭐ Rating: {movie['rating']}</div>
                    <div class='rating'>🎯 Match: {movie['similarity']}%</div>
                    <div class='release'>📅 {movie['release']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            trailer_url = fetch_trailer(movie["movie_id"])

            if trailer_url:
                st.link_button(
                    "▶️ Trailer",
                    trailer_url,
                    use_container_width=True
                )

            st.link_button(
                "🎬 Details",
                f"https://www.themoviedb.org/movie/{movie['movie_id']}",
                use_container_width=True
          )
# ================= FOOTER =================

st.markdown("""
<hr>

<center>

<h3>🎬 WatchNext</h3>

Discover • Watch • Repeat

<br><br>

Built with ❤️ by Mohammad Sarfraz Alam

<br>

Python • Streamlit • Scikit-Learn • TMDB API

</center>
""", unsafe_allow_html=True)