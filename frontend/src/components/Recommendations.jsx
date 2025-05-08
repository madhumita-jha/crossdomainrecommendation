import React from 'react';

const Recommendations = ({ musicRecommendations, bookRecommendations }) => (
  <div className="recommendations">
    {musicRecommendations.length > 0 && (
      <div className="card">
        <div className="card-header">🎵 Music</div>
        <div className="card-body">
          <ul>
            {musicRecommendations.map((track, idx) => (
              <li key={idx}>{track}</li>
            ))}
          </ul>
        </div>
      </div>
    )}

    {bookRecommendations.length > 0 && (
      <div className="card">
        <div className="card-header">📚 Books</div>
        <div className="card-body">
          <ul>
            {bookRecommendations.map((book, idx) => (
              <li key={idx}>{book}</li>
            ))}
          </ul>
        </div>
      </div>
    )}

    {musicRecommendations.length === 0 && bookRecommendations.length === 0 && (
      <p className="no-results">No recommendations yet. Search above!</p>
    )}
  </div>
);

export default Recommendations;