# Vehicle Fleet Management System

A comprehensive full-stack application for managing vehicle fleet data, equipment lifecycle tracking, and generating detailed analytics reports.

## 🏗️ Project Structure

```
vehicle-fleet-management/
├── backend/                    # Flask API Server
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── README.md             # Backend documentation
│   ├── API_DOCUMENTATION.md  # Complete API reference
│   ├── constants/            # Configuration files
│   ├── routes/              # API route definitions
│   ├── controllers/         # Request handling logic
│   ├── services/           # Business logic layer
│   ├── scripts/           # Data processing scripts
│   └── database/         # Excel file storage
├── frontend/               # React + Vite Application
│   ├── src/
│   │   ├── types/         # TypeScript type definitions
│   │   ├── services/      # API service layer
│   │   └── components/    # React components
│   ├── package.json
│   └── vite.config.js
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **npm or yarn** (package manager)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask server:**
   ```bash
   python app.py
   ```
   
   Server will run on `http://localhost:3300`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```
   
   Frontend will run on `http://localhost:5173`

## 🔧 Features

### Backend (Flask API)
- **Authentication System** - User registration/login with Excel database
- **File Management** - Upload and process Excel files
- **Data Processing** - Advanced analytics and report generation
- **REST API** - Complete RESTful API with proper error handling
- **Excel Integration** - Native Excel file reading/writing

### Frontend (React + Vite)
- **Modern React** - Latest React with Vite for fast development
- **TypeScript** - Full type safety and better developer experience
- **API Integration** - Type-safe API service layer
- **Responsive Design** - Mobile-friendly interface
- **File Upload** - Drag-and-drop file uploads

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/users` - Get all users
- `GET /api/auth/stats` - User statistics

### File Management
- `POST /api/files/vehicle-fleet/upload` - Upload vehicle data
- `GET /api/files/vehicle-fleet/data` - Get vehicle data
- `POST /api/files/equipment-lifecycle/upload` - Upload equipment data

### Data Processing
- `POST /api/scripts/excel-reader/run` - Generate comprehensive analysis
- `POST /api/scripts/lob-pivot-generator/run` - Generate LOB pivot tables
- `POST /api/scripts/ool-reader/run` - Process out-of-life data

See `backend/API_DOCUMENTATION.md` for complete API reference.

## 🗄️ Data Analysis Features

### Vehicle Replacement Analysis
- **10-Year Forecasting** (2026-2035)
- **Cost Analysis** by vehicle class (Heavy, Light, Pickup)
- **LOB Analysis** (DP&C, UOS, Customer Ops, Electric Ops, Gas Ops, Service Corp)
- **Equipment Categorization** by ObjectType

### Electric Vehicle Transition
- **EV Adoption Planning** with ICE to EV conversion ratios
- **Budget Impact Analysis** for EV transition
- **Timeline Planning** for electrification

### Radio Equipment Analysis
- **Installation Cost Tracking** by LOB
- **Annual Spend Forecasting**
- **Equipment Count Analysis**

### Generated Reports
All analyses generate Excel files with:
- Summary pivot tables
- Detailed hierarchical breakdowns
- Cost projections by year
- LOB-specific insights

## 🛠️ Development

### Backend Development
```bash
cd backend
python app.py  # Start development server
```

Key directories:
- `routes/` - Add new API endpoints
- `controllers/` - Handle HTTP requests
- `services/` - Business logic
- `constants/` - Configuration

### Frontend Development
```bash
cd frontend
npm run dev  # Start development server
```

Key directories:
- `src/components/` - React components
- `src/services/` - API integration
- `src/types/` - TypeScript definitions

### Adding New Features

1. **Backend**: Add route → controller → service
2. **Frontend**: Update types → API service → components
3. **Documentation**: Update API docs and README

## 🧪 Testing

### Backend Testing
```bash
# Health check
curl http://localhost:3300/health

# Test authentication
curl -X POST http://localhost:3300/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'
```

### Frontend Testing
```bash
cd frontend
npm run test    # Run tests
npm run build   # Build for production
```

## 📊 Sample Data

The system processes Excel files containing:
- **Vehicle Fleet Data**: Equipment details, make, model, year, cost, location
- **Equipment Lifecycle**: Replacement schedules, lifecycle tracking
- **Out-of-Life Data**: Equipment retirement planning

Sample data files are available in the `upload/` directory.

## 🔐 Security

- **Password Hashing**: SHA-256 encryption
- **Input Validation**: Comprehensive request validation
- **File Security**: Secure filename handling and type validation
- **Error Handling**: Non-revealing error messages

## 📈 Performance

- **File Upload**: Up to 100MB Excel files supported
- **Data Processing**: Handles thousands of vehicle records
- **Response Times**: Optimized for quick data retrieval
- **Caching**: Excel files cached in database directory

## 🚨 Troubleshooting

### Backend Issues
- **Port in use**: Change `FLASK_PORT` environment variable
- **Module not found**: Ensure `pip install -r requirements.txt` was run
- **Database errors**: Check `database/` directory permissions

### Frontend Issues
- **Module not found**: Run `npm install` in frontend directory
- **Build failures**: Check Node.js version (16+ required)
- **API connection**: Verify backend is running on port 3300

## 📝 Environment Variables

### Backend
```bash
export FLASK_HOST=127.0.0.1     # Server host
export FLASK_PORT=3300          # Server port
export FLASK_DEBUG=True         # Debug mode
```

### Frontend
```bash
VITE_API_BASE_URL=http://localhost:3300  # API base URL
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Follow the existing code structure
4. Add proper documentation
5. Test thoroughly
6. Submit a pull request

## 📞 Support

- **Backend Documentation**: `backend/README.md`
- **API Reference**: `backend/API_DOCUMENTATION.md`
- **Frontend Types**: `frontend/src/types/api.ts`

## 🎯 Roadmap

- [ ] User authentication tokens (JWT)
- [ ] Real-time data updates
- [ ] Advanced data visualization
- [ ] Export functionality
- [ ] Mobile app support
- [ ] Multi-tenant support

---

**Built with Flask, React, and TypeScript for modern, scalable fleet management.**