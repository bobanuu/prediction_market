import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { API_ENDPOINTS } from '../config';

const MarketDetail = () => {
  const { id } = useParams();
  const { checkAuthStatus } = useAuth();
  const [market, setMarket] = useState(null);
  const [shares, setShares] = useState({ YES: 0, NO: 0 });
  const [loading, setLoading] = useState(true);
  const [orderForm, setOrderForm] = useState({
    order_type: 'BUY',
    order_class: 'LIMIT',
    outcome: 'YES',
    quantity: 1,
    price: 0.50
  });
  const [orderBook, setOrderBook] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchMarketData();
  }, [id]);

  const fetchMarketData = async () => {
    try {
      const [marketResponse, sharesResponse, orderBookResponse] = await Promise.all([
        axios.get(API_ENDPOINTS.MARKETS.DETAIL(id), { withCredentials: true }),
        axios.get(API_ENDPOINTS.ACCOUNTS.PORTFOLIO, { withCredentials: true }),
        axios.get(API_ENDPOINTS.MARKETS.ORDER_BOOK(id), { withCredentials: true })
      ]);
      
      setMarket(marketResponse.data);
      setOrderBook(orderBookResponse.data);
      
      // Find user's shares for this market
      const userShares = sharesResponse.data.find(share => share.market === parseInt(id));
      if (userShares) {
        setShares({
          YES: userShares.outcome === 'YES' ? userShares.quantity : 0,
          NO: userShares.outcome === 'NO' ? userShares.quantity : 0
        });
      }
      
      // Set default price to mid-price or current market price
      const defaultPrice = orderBookResponse.data.mid_price || marketResponse.data.current_yes_price;
      setOrderForm(prev => ({
        ...prev,
        price: defaultPrice
      }));
    } catch (error) {
      console.error('Error fetching market data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrderChange = (e) => {
    const { name, value } = e.target;
    setOrderForm(prev => ({
      ...prev,
      [name]: name === 'quantity' ? parseInt(value) || 0 : value
    }));
  };

  const handleSubmitOrder = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setMessage('');

    try {
      const orderData = {
        ...orderForm,
        market: parseInt(id)
      };
      
      // For market orders, don't send price
      if (orderForm.order_class === 'MARKET') {
        delete orderData.price;
      }

      const response = await axios.post(API_ENDPOINTS.MARKETS.PLACE_ORDER, 
        orderData, 
        { withCredentials: true }
      );

      if (response.data.fills && response.data.fills.length > 0) {
        setMessage(`Order filled! ${response.data.fills.length} fills executed.`);
      } else {
        setMessage(response.data.message || 'Order placed successfully!');
      }
      
      fetchMarketData(); // Refresh market data
      checkAuthStatus(); // Refresh user balance
    } catch (error) {
      setMessage(error.response?.data?.error || 'Error placing order');
    } finally {
      setSubmitting(false);
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
        <div className="pulse">Loading market...</div>
      </div>
    );
  }

  if (!market) {
    return (
      <div className="error">
        <div className="text-center">
          <svg className="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <h3 className="text-xl font-semibold text-red-700 mb-2">Market Not Found</h3>
          <p className="text-red-600">The market you're looking for doesn't exist or has been removed.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fade-in">
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <span className={`status-indicator ${getStatusColor(market.status)}`}>
            {market.status}
          </span>
          <div className="text-sm text-gray-500">
            Resolves {new Date(market.resolution_date).toLocaleDateString()}
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{market.title}</h1>
        <p className="text-gray-600 text-lg">{market.description}</p>
      </div>
      
      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Current Prices</h3>
            <div className="text-sm text-gray-500">Live market data</div>
          </div>
          
          <div className="grid grid-2 gap-6">
            <div className="text-center p-6 bg-green-50 rounded-xl border border-green-200">
              <div className="text-green-600 text-4xl font-bold font-mono mb-2">
                {formatPrice(market.current_yes_price)}¢
              </div>
              <div className="text-green-700 font-semibold">{market.outcome_yes}</div>
            </div>
            <div className="text-center p-6 bg-red-50 rounded-xl border border-red-200">
              <div className="text-red-600 text-4xl font-bold font-mono mb-2">
                {formatPrice(market.current_no_price)}¢
              </div>
              <div className="text-red-700 font-semibold">{market.outcome_no}</div>
            </div>
          </div>
          
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Created by:</span>
                <div className="font-semibold">{market.created_by_username}</div>
              </div>
              <div>
                <span className="text-gray-500">Resolution:</span>
                <div className="font-semibold">{new Date(market.resolution_date).toLocaleDateString()}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Your Position</h3>
            <div className="text-sm text-gray-500">Current holdings</div>
          </div>
          
          <div className="grid grid-2 gap-6">
            <div className="text-center p-6 bg-green-50 rounded-xl border border-green-200">
              <div className="text-green-600 text-3xl font-bold font-mono mb-2">
                {shares.YES}
              </div>
              <div className="text-green-700 font-semibold">{market.outcome_yes} Shares</div>
            </div>
            <div className="text-center p-6 bg-red-50 rounded-xl border border-red-200">
              <div className="text-red-600 text-3xl font-bold font-mono mb-2">
                {shares.NO}
              </div>
              <div className="text-red-700 font-semibold">{market.outcome_no} Shares</div>
            </div>
          </div>
          
          {shares.YES === 0 && shares.NO === 0 && (
            <div className="mt-6 text-center text-gray-500">
              <svg className="w-12 h-12 mx-auto mb-2 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              <p>No position in this market</p>
            </div>
          )}
        </div>
      </div>

      {/* Order Book */}
      {orderBook && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Order Book - {orderForm.outcome}</h3>
            <div className="text-sm text-gray-500">Live bid/ask prices</div>
          </div>
          
          <div className="grid grid-2 gap-6">
            <div>
              <h4 className="font-semibold text-green-600 mb-3">Bids (Buy Orders)</h4>
              <div className="space-y-1">
                {orderBook.bids.length > 0 ? (
                  orderBook.bids.slice(0, 5).map((bid, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                      <span className="font-mono text-green-700">{formatPrice(bid.price)}¢</span>
                      <span className="text-sm text-gray-600">{bid.quantity}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500 text-sm">No bids</div>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-red-600 mb-3">Asks (Sell Orders)</h4>
              <div className="space-y-1">
                {orderBook.asks.length > 0 ? (
                  orderBook.asks.slice(0, 5).map((ask, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-red-50 rounded">
                      <span className="font-mono text-red-700">{formatPrice(ask.price)}¢</span>
                      <span className="text-sm text-gray-600">{ask.quantity}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-gray-500 text-sm">No asks</div>
                )}
              </div>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Best Bid:</span>
                <div className="font-mono font-semibold text-green-600">
                  {orderBook.best_bid ? `${formatPrice(orderBook.best_bid)}¢` : 'N/A'}
                </div>
              </div>
              <div>
                <span className="text-gray-500">Best Ask:</span>
                <div className="font-mono font-semibold text-red-600">
                  {orderBook.best_ask ? `${formatPrice(orderBook.best_ask)}¢` : 'N/A'}
                </div>
              </div>
              <div>
                <span className="text-gray-500">Spread:</span>
                <div className="font-mono font-semibold">
                  {orderBook.spread ? `${formatPrice(orderBook.spread)}¢` : 'N/A'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Place Order</h3>
          <div className="text-sm text-gray-500">Trade on this market outcome</div>
        </div>
        
        {message && (
          <div className={message.includes('successfully') || message.includes('Order filled') || message.includes('filled') ? 'success' : 'error'}>
            <div className="flex items-center gap-2">
              {message.includes('successfully') || message.includes('Order filled') || message.includes('filled') ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
              {message}
            </div>
          </div>
        )}
        
        <form onSubmit={handleSubmitOrder} className="space-y-6">
          <div className="grid grid-3 gap-6">
            <div className="form-group">
              <label className="form-label">Order Type</label>
              <select
                name="order_type"
                value={orderForm.order_type}
                onChange={handleOrderChange}
                className="form-select"
              >
                <option value="BUY">Buy Shares</option>
                <option value="SELL">Sell Shares</option>
              </select>
            </div>
            
            <div className="form-group">
              <label className="form-label">Order Class</label>
              <select
                name="order_class"
                value={orderForm.order_class}
                onChange={handleOrderChange}
                className="form-select"
              >
                <option value="LIMIT">Limit Order</option>
                <option value="MARKET">Market Order</option>
              </select>
            </div>
            
            <div className="form-group">
              <label className="form-label">Outcome</label>
              <select
                name="outcome"
                value={orderForm.outcome}
                onChange={handleOrderChange}
                className="form-select"
              >
                <option value="YES">{market.outcome_yes}</option>
                <option value="NO">{market.outcome_no}</option>
              </select>
            </div>
          </div>
          
          <div className="grid grid-2 gap-6">
            <div className="form-group">
              <label className="form-label">Quantity</label>
              <input
                type="number"
                name="quantity"
                value={orderForm.quantity}
                onChange={handleOrderChange}
                className="form-input"
                min="1"
                placeholder="Number of shares"
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">
                {orderForm.order_class === 'MARKET' ? 'Market Price' : 'Price per Share'}
              </label>
              {orderForm.order_class === 'MARKET' ? (
                <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
                  <div className="text-sm text-gray-600 mb-1">Market orders execute at best available price</div>
                  <div className="font-mono text-lg">
                    {orderForm.order_type === 'BUY' && orderBook?.best_ask ? 
                      `~${formatPrice(orderBook.best_ask)}¢` :
                      orderForm.order_type === 'SELL' && orderBook?.best_bid ?
                      `~${formatPrice(orderBook.best_bid)}¢` :
                      'Market Price'
                    }
                  </div>
                </div>
              ) : (
                <div className="relative">
                  <input
                    type="number"
                    name="price"
                    value={orderForm.price}
                    onChange={handleOrderChange}
                    className="form-input pr-8"
                    min="0"
                    max="1"
                    step="0.0001"
                    placeholder="0.5000"
                    required
                  />
                  <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-mono text-sm">
                    {formatPrice(orderForm.price)}¢
                  </div>
                </div>
              )}
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Order Summary</div>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold">
                  {orderForm.order_type} {orderForm.quantity} shares of {orderForm.outcome}
                </span>
                <span className="text-sm text-gray-500">
                  {orderForm.order_class === 'MARKET' ? 'Market Order' : 'Limit Order'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">
                  {orderForm.order_class === 'MARKET' ? 'Est. Total:' : 'Total Cost:'}
                </span>
                <span className="font-mono text-lg">
                  {orderForm.order_class === 'MARKET' ? 
                    (orderForm.order_type === 'BUY' && orderBook?.best_ask ? 
                      `~$${(orderForm.quantity * orderBook.best_ask).toFixed(2)}` :
                      orderForm.order_type === 'SELL' && orderBook?.best_bid ?
                      `~$${(orderForm.quantity * orderBook.best_bid).toFixed(2)}` :
                      'Market Price'
                    ) :
                    `$${(orderForm.quantity * orderForm.price).toFixed(2)}`
                  }
                </span>
              </div>
            </div>
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary w-full py-4 text-lg font-semibold"
            disabled={submitting}
          >
            {submitting ? (
              <div className="flex items-center justify-center gap-2">
                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Placing Order...
              </div>
            ) : (
              'Place Order'
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default MarketDetail;
