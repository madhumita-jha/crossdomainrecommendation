import React, { useState } from 'react';

const SearchBar = ({ onSubmit }) => {
  const [movie, setMovie] = useState('');
  const [filter, setFilter] = useState('both');

  const handleSubmit = e => {
    e.preventDefault();
    if (!movie.trim()) return;
    onSubmit(movie.trim(), filter);
    setMovie('');
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Enter a movie name…"
        value={movie}
        onChange={e => setMovie(e.target.value)}
      />
      <div className="filter-group">
        <label>
          <input
            type="radio"
            name="filter"
            value="both"
            checked={filter === 'both'}
            onChange={e => setFilter(e.target.value)}
          /> Both
        </label>
        <label>
          <input
            type="radio"
            name="filter"
            value="music"
            checked={filter === 'music'}
            onChange={e => setFilter(e.target.value)}
          /> Music
        </label>
        <label>
          <input
            type="radio"
            name="filter"
            value="books"
            checked={filter === 'books'}
            onChange={e => setFilter(e.target.value)}
          /> Books
        </label>
      </div>
      <button type="submit">Get Recommendations</button>
    </form>
  );
};

export default SearchBar;