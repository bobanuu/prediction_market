import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_ENDPOINTS } from '../config';

const Portfolio = () => {
  const [shares, setShares] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const fetchPortfolioData = async () => {
    try {
      const [sharesResponse, transactionsResponse] = await Promise.all([
        axios.get(API_ENDPOINTS.ACCOUNTS.PORTFOLIO, { withCredentials: true }),
        axios.get(`${API_ENDPOINTS.ACCOUNTS.ACCOUNT}transactions/`, { withCredentials: true })
      ]);
      
      setShares(sharesResponse.data);
      setTransactions(transactionsResponse.data.slice(0, 10)); // Show last 10 transactions
    } catch (error) {
      console.error('Error fetching portfolio data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading portfolio...</div>;
  }

  return (
    <div>
      <h1>Portfolio</h1>
      
      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Your Shares</h3>
          </div>
          
          {shares.length > 0 ? (
            <div>
              {shares.map(share => (
                <div key={share.id} className="mb-2" style={{ padding: '1rem', border: '1px solid #eee', borderRadius: '4px' }}>
                  <h4>{share.market_title}</h4>
                  <div className="grid grid-2">
                    <div>
                      <span className={share.outcome === 'YES' ? 'text-success' : 'text-danger'}>
                        {share.outcome}: {share.quantity} shares
                      </span>
                    </div>
                    <div className="text-muted">
                      Avg Price: ${share.average_price}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">No shares owned</p>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Transactions</h3>
          </div>
          
          {transactions.length > 0 ? (
            <div>
              {transactions.map(transaction => (
                <div key={transaction.id} className="mb-2" style={{ padding: '1rem', border: '1px solid #eee', borderRadius: '4px' }}>
                  <div className="grid grid-2">
                    <div>
                      <strong>{transaction.transaction_type}</strong>
                      <div className="text-muted">{transaction.description}</div>
                    </div>
                    <div className="text-right">
                      <div className={transaction.amount > 0 ? 'text-success' : 'text-danger'}>
                        {transaction.amount > 0 ? '+' : ''}${transaction.amount}
                      </div>
                      <div className="text-muted">
                        {new Date(transaction.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted">No transactions</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Portfolio;
