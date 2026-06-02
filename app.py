import streamlit as st
import pickle
import pandas as pd
import requests

# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ================= CUSTOM CSS =================

st.markdown("""
<style>

.main {
    background-color: #0e1117;
}

.block-container {
    padding-top: 2rem;
}

h1 {
    text-align: center;
    color: #E50914;
}

.movie-title {
    text-align: center;
    font-size: 16px;
    font-weight: bold;
    color: white;
    margin-top: 10px;
}

.rating {
    text-align: center;
    color: gold;
    font-weight: bold;
}

.release {
    text-align: center;
    color: lightgray;
}

.stButton > button {
    background-color: #E50914;
    color: white;
    border-radius: 10px;
    width: 100%;
    height: 3em;
    font-size: 18px;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #b20710;
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================

st.sidebar.title("🎬 Movie Recommender")

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

st.title("🍿 Netflix Style Movie Recommendation System")

st.markdown(
    "<h4 style='text-align:center;'>AI Powered Content-Based Recommendation Engine</h4>",
    unsafe_allow_html=True
)

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

# ================= MOVIE SELECTION =================

# ================= MOVIE SELECTION =================

search_movie = st.text_input(
    "🔍 Search Movie",
    placeholder="Type movie name..."
)

movie_list = movies['title'].tolist()

if search_movie:
    filtered_movies = [
        movie for movie in movie_list
        if search_movie.lower() in movie.lower()
    ]
else:
    filtered_movies = []

if len(filtered_movies) > 0:

    selected_movie = st.selectbox(
        "🎬 Select a Movie",
        filtered_movies
    )

else:

    selected_movie = None

    st.info("💡 Search and select a movie to get recommendations")

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

if st.button("🔥 Recommend Similar Movies"):

    with st.spinner("Finding Similar Movies..."):

        recommendations = recommend(selected_movie)

    st.subheader(
        f"🎬 Recommended Movies for '{selected_movie}'"
    )

    st.write("Total Recommendations:", len(recommendations))

    col1, col2, col3, col4, col5 = st.columns(5)

    cols = [col1, col2, col3, col4, col5]

    for idx, movie in enumerate(recommendations):

        with cols[idx]:

            if movie["poster"]:
                st.image(movie["poster"])

            st.markdown(
                f"<div class='movie-title'>{movie['title']}</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='rating'>🎯 Match {movie['similarity']}%</div>",
                unsafe_allow_html=True
            )

            st.markdown(
                f"<div class='release'>📅 {movie['release']}</div>",
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

st.write("")
st.write("")

st.markdown(
    """
    <hr>
    <center>
    Built with ❤️ by Mohammad Sarfraz Alam |
    Python • Streamlit • Scikit-Learn • TMDB API
    </center>
    """,
    unsafe_allow_html=True
)