# PrediX Markets - Prediction Marketplace

A modern prediction marketplace built with Django REST API and React frontend, featuring a professional trading interface with order books, market/limit orders, and real-time trading.

## 🚀 Features

- **Modern Trading Interface**: Professional red-themed UI inspired by leading prediction markets
- **Order Book System**: Full bid/ask spreads with market and limit orders
- **Real-time Trading**: Instant order matching and execution
- **User Authentication**: Secure login/registration with session management
- **Portfolio Management**: Track positions and trading history
- **Market Creation**: Admin can create new prediction markets
- **Liquidity Seeding**: Automatic initial liquidity for new markets

## 🛠 Tech Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API development
- **SQLite** - Database (development)
- **Custom Authentication** - Session-based with CSRF exemption for API

### Frontend
- **React 18** - User interface
- **Axios** - HTTP client
- **React Router** - Client-side routing
- **Custom CSS** - Modern glassmorphism design

## 📦 Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/bobanuu/prediction_market.git
cd prediction_market

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create sample data
python manage.py shell -c "exec(open('create_sample_data.py').read())"

# Start Django server
python manage.py runserver
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## 🎯 Usage

### Sample Accounts
- **Admin**: `admin` / `admin123`
- **Trader**: `trader1` / `trader123`

### Trading Features
1. **Browse Markets**: View available prediction markets
2. **Place Orders**: Use market or limit orders to trade
3. **Monitor Portfolio**: Track your positions and balance
4. **Order Book**: See real-time bid/ask spreads

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - User registration

### Markets
- `GET /api/markets/` - List all markets
- `GET /api/markets/{id}/` - Market details
- `GET /api/markets/{id}/order-book/` - Order book data
- `POST /api/markets/place-order/` - Place trading order
- `POST /api/markets/cancel-order/` - Cancel order

### Account
- `GET /api/accounts/account/` - User account info
- `GET /api/accounts/portfolio/` - User portfolio

## 🚀 Deployment

This project is designed to be deployed on Vercel with the following structure:

### Vercel Configuration
- Frontend builds automatically from `/frontend` directory
- Backend API can be deployed separately or as serverless functions
- Database migrations run automatically on deployment

### Environment Variables
```bash
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.vercel.app

# Database (for production)
DATABASE_URL=your-production-database-url
```

## 📁 Project Structure

```
prediction_marketplace/
├── accounts/                 # User authentication app
├── markets/                  # Trading and markets app
├── prediction_marketplace/   # Django project settings
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── contexts/         # React contexts
│   │   └── App.css          # Main styles
│   └── package.json
├── requirements.txt          # Python dependencies
├── create_sample_data.py     # Sample data script
└── manage.py                # Django management
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by modern prediction markets like Kalshi
- Built with Django and React best practices
- Professional UI/UX design with glassmorphism effects