import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const Markets = () => {
  const [markets, setMarkets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMarkets();
  }, []);

  const fetchMarkets = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/markets/markets/', { withCredentials: true });
      setMarkets(response.data);
    } catch (error) {
      console.error('Error fetching markets:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return (parseFloat(price) * 100).toFixed(1);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE':
        return 'status-active';
      case 'PENDING':
        return 'status-pending';
      case 'CLOSED':
        return 'status-closed';
      default:
        return 'status-pending';
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="pulse">Loading markets...</div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Prediction Markets</h1>
        <p className="text-gray-600">Trade on the outcomes of future events</p>
      </div>
      
      {markets.length > 0 ? (
        <div className="grid grid-2">
          {markets.map(market => (
            <Link key={market.id} to={`/markets/${market.id}`} className="market-card">
              <div className="flex justify-between items-start mb-4">
                <h3 className="market-title">{market.title}</h3>
                <span className={`status-indicator ${getStatusColor(market.status)}`}>
                  {market.status}
                </span>
              </div>
              
              <p className="market-description">{market.description}</p>
              
              <div className="market-prices">
                <div className="price-display price-yes">
                  <div className="price-value">{formatPrice(market.current_yes_price)}¢</div>
                  <div className="price-label">{market.outcome_yes}</div>
                </div>
                <div className="price-display price-no">
                  <div className="price-value">{formatPrice(market.current_no_price)}¢</div>
                  <div className="price-label">{market.outcome_no}</div>
                </div>
              </div>
              
              <div className="market-meta">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>Resolves {new Date(market.resolution_date).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                  <span>{market.created_by_username}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <div className="card text-center">
          <div className="mb-4">
            <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Markets Available</h3>
            <p className="text-gray-600">Check back later for new prediction markets</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Markets;
