# 🎯 Cross-Domain Recommendation Using Transfer Learning

This project is a **Cross-Domain Recommendation System** built using **Transfer Learning**, designed to recommend **books** and **music** based on a user's favorite **movie**. It intelligently transfers knowledge from the source domain (movies) to the target domains (books and music) to overcome data sparsity and improve recommendation quality.

---

## 🚀 Features

- Input a **movie name** and get recommendations for:
  - 📚 Books
  - 🎵 Music tracks
- Uses **Transfer Learning** to bridge domains.
- Clean UI built with **React.js**
- Backend powered by **Flask** and external APIs
- Recommendation logic powered by deep learning and content-based filtering
- Works without a traditional database — all data is loaded from CSV files and APIs

---

## 🧠 Tech Stack

**Frontend:**
- React.js
- Axios
- Tailwind CSS (optional)

**Backend:**
- Python (Flask)
- Pandas, NumPy
- Pretrained models (via Hugging Face)
- APIs: TMDB, OpenLibrary, Spotify

**APIs Used:**
- 🎬 [TMDB API](https://www.themoviedb.org/)
- 📚 [OpenLibrary API](https://openlibrary.org/developers/api)
- 🎧 [Spotify API](https://developer.spotify.com/)
- 🤗 [Hugging Face Transformers](https://huggingface.co/)

## 📊 Datasets Used

- `movie_data.csv` — Movie details (title, genre, etc.)
- `music_data.csv` — Spotify track info (popularity, danceability, energy, etc.)
- `books_data.csv` — Book metadata (title, author, genre, etc.)

---
