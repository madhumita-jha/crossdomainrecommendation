import React, { useState } from 'react';
import axios from 'axios';
import SearchBar from './components/SearchBar';
import Recommendations from './components/Recommendations';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL;

function App() {
  const [musicRecommendations, setMusicRecommendations] = useState([]);
  const [bookRecommendations, setBookRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);

  const getRecommendations = async (movie, filter) => {
    setLoading(true);
    setMusicRecommendations([]);
    setBookRecommendations([]);
    try {
      const response = await axios.get(
        `${API_URL}/recommend?movie=${encodeURIComponent(movie)}`
      );
      const { music_recommendations = [], book_recommendations = [] } = response.data;

      // Filter according to user choice
      if (filter === 'music' || filter === 'both') {
        setMusicRecommendations(music_recommendations);
      }
      if (filter === 'books' || filter === 'both') {
        setBookRecommendations(book_recommendations);
      }
    } catch (err) {
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-wrapper">
    <h1 className="main-title">Cross-Domain Recommender</h1>

    <div className="app-container">
      <h2 className="card-prompt">What’s your favorite movie?</h2>

      <SearchBar onSubmit={getRecommendations} />

      {loading ? (
        <div className="loader" />
      ) : (
        <Recommendations
          musicRecommendations={musicRecommendations}
          bookRecommendations={bookRecommendations}
        />
      )}
    </div>
  </div>
  );
}

export default App;