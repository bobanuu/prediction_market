import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';

const Dashboard = () => {
  const [markets, setMarkets] = useState([]);
  const [shares, setShares] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [marketsResponse, sharesResponse] = await Promise.all([
        axios.get(API_ENDPOINTS.MARKETS.LIST, { withCredentials: true }),
        axios.get(API_ENDPOINTS.ACCOUNTS.PORTFOLIO, { withCredentials: true })
      ]);
      
      setMarkets(marketsResponse.data.slice(0, 5)); // Show only first 5 markets
      setShares(sharesResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return (parseFloat(price) * 100).toFixed(1);
  };

  const getTotalValue = () => {
    return shares.reduce((total, share) => {
      return total + (share.quantity * share.average_price);
    }, 0);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="pulse">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's your trading overview</p>
      </div>
      
      {/* Stats Cards */}
      <div className="grid grid-4 mb-8">
        <div className="card text-center">
          <div className="text-2xl font-bold text-red-600 mb-1">{markets.length}</div>
          <div className="text-sm text-gray-500">Active Markets</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600 mb-1">{shares.length}</div>
          <div className="text-sm text-gray-500">Positions</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-blue-600 mb-1 font-mono">
            ${getTotalValue().toFixed(2)}
          </div>
          <div className="text-sm text-gray-500">Portfolio Value</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-amber-600 mb-1">
            {shares.filter(s => s.quantity > 0).length}
          </div>
          <div className="text-sm text-gray-500">Active Positions</div>
        </div>
      </div>
      
      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Markets</h3>
            <div className="text-sm text-gray-500">Latest prediction markets</div>
          </div>
          {markets.length > 0 ? (
            <div className="space-y-3">
              {markets.map(market => (
                <Link key={market.id} to={`/markets/${market.id}`} className="block p-4 border border-gray-200 rounded-lg hover:border-red-200 hover:bg-red-50 transition-all duration-200">
                  <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2">{market.title}</h4>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{market.description}</p>
                  <div className="flex justify-between items-center">
                    <div className="flex gap-4">
                      <div className="text-center">
                        <div className="text-green-600 font-bold font-mono">{formatPrice(market.current_yes_price)}¢</div>
                        <div className="text-xs text-gray-500">YES</div>
                      </div>
                      <div className="text-center">
                        <div className="text-red-600 font-bold font-mono">{formatPrice(market.current_no_price)}¢</div>
                        <div className="text-xs text-gray-500">NO</div>
                      </div>
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(market.resolution_date).toLocaleDateString()}
                    </div>
                  </div>
                </Link>
              ))}
              <div className="text-center pt-4">
                <Link to="/markets" className="btn btn-outline">
                  View All Markets
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
              <p className="text-gray-500">No markets available</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Your Portfolio</h3>
            <div className="text-sm text-gray-500">Current holdings</div>
          </div>
          {shares.length > 0 ? (
            <div className="space-y-3">
              {shares.slice(0, 5).map(share => (
                <div key={share.id} className="p-4 border border-gray-200 rounded-lg">
                  <h4 className="font-semibold text-gray-900 mb-2">{share.market_title}</h4>
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        share.outcome === 'YES' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {share.outcome}
                      </span>
                      <span className="font-mono text-sm">
                        {share.quantity} shares
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="font-mono text-sm font-semibold">
                        ${share.average_price}
                      </div>
                      <div className="text-xs text-gray-500">avg price</div>
                    </div>
                  </div>
                </div>
              ))}
              <div className="text-center pt-4">
                <Link to="/portfolio" className="btn btn-outline">
                  View Full Portfolio
                  <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <svg className="w-12 h-12 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              <p className="text-gray-500 mb-4">No shares owned</p>
              <Link to="/markets" className="btn btn-primary">
                Start Trading
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
