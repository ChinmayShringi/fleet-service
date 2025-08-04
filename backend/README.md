# Vehicle Fleet Management API - Backend

A comprehensive Flask-based REST API for managing vehicle fleet data, equipment lifecycle tracking, and user authentication.

## 🏗️ Architecture

- **Framework**: Flask (Python)
- **Database**: Excel files (.xlsx) as data storage
- **Authentication**: SHA-256 password hashing
- **Structure**: Clean MVC architecture with routes, controllers, and services

## 📁 Project Structure

```
backend/
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── constants/
│   └── file_constants.py     # Configuration and file paths
├── routes/                   # API route definitions
│   ├── auth_routes.py       # Authentication endpoints
│   ├── file_routes.py       # File management endpoints
│   ├── script_routes.py     # Script execution endpoints
│   └── health_routes.py     # Health check endpoints
├── controllers/             # Request handling logic
│   ├── auth_controller.py   # Authentication logic
│   ├── file_controller.py   # File management logic
│   └── script_controller.py # Script execution logic
├── services/               # Business logic layer
│   ├── user_service.py     # User management
│   ├── file_service.py     # File operations
│   └── script_service.py   # Script execution
├── scripts/               # Data processing scripts
│   ├── excel_reader.py    # Main data analysis script
│   ├── lob_pivot_generator.py # LOB pivot tables
│   ├── ool_reader.py      # Out-of-life data processing
│   └── equipment_updater.py # Equipment updates
└── database/             # Excel file storage (auto-created)
    ├── user.xlsx                              # User authentication data
    ├── vehicle_fleet_master_data.xlsx         # Main vehicle data
    ├── equipment_lifecycle_reference.xlsx     # Equipment lifecycle data
    ├── electric_vehicle_budget_analysis.xlsx  # EV analysis results
    ├── radio_equipment_cost_analysis.xlsx     # Radio cost analysis
    ├── vehicle_replacement_detailed_forecast.xlsx # Replacement forecasts
    ├── vehicle_replacement_by_category.xlsx   # Category-based analysis
    └── equipment_lifecycle_by_business_unit.xlsx # LOB analysis
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**:
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:3300`

### Environment Variables

You can customize the server configuration using environment variables:

```bash
export FLASK_HOST=127.0.0.1    # Server host (default: 127.0.0.1)
export FLASK_PORT=3300         # Server port (default: 3300)  
export FLASK_DEBUG=True        # Debug mode (default: True)
```

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/users` - Get all users
- `GET /api/auth/stats` - Get user statistics

### File Management
- `POST /api/files/vehicle-fleet/upload` - Upload vehicle fleet data
- `GET /api/files/vehicle-fleet/data` - Get vehicle fleet data
- `POST /api/files/equipment-lifecycle/upload` - Upload equipment lifecycle data

### Script Execution
- `POST /api/scripts/excel-reader/run` - Generate comprehensive analysis
- `POST /api/scripts/lob-pivot-generator/run` - Generate LOB pivot tables
- `POST /api/scripts/ool-reader/run` - Process out-of-life data

### Health & Info
- `GET /health` - Health check
- `GET /` - API information and endpoint list

## 🗄️ Database Schema

### Users Table (user.xlsx)
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Unique user identifier |
| username | String | Login username |
| email | String | User email address |
| password_hash | String | SHA-256 hashed password |
| full_name | String | Display name |
| role | String | User role (user, admin) |
| created_at | DateTime | Registration timestamp |
| last_login | DateTime | Last successful login |
| is_active | Boolean | Account status |

### Vehicle Fleet Data
- Comprehensive vehicle information including make, model, year, cost, location
- Equipment lifecycle tracking
- Replacement forecasting data
- LOB (Line of Business) categorization

## 🔧 Features

### Data Processing
- **Excel File Processing**: Advanced pandas-based data analysis
- **Pivot Table Generation**: Automated pivot table creation
- **Cost Analysis**: Vehicle replacement cost calculations
- **EV Transition Analysis**: Electric vehicle transition planning
- **LOB Analysis**: Line of business equipment analysis

### Security
- **Password Hashing**: SHA-256 encryption
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Proper HTTP status codes and messages
- **File Security**: Secure filename handling for uploads

### File Management
- **Auto-Creation**: Database files created automatically if missing
- **Excel Integration**: Native Excel file reading/writing
- **Large File Support**: Up to 100MB file uploads
- **Data Validation**: File format and content validation

## 🧪 Testing

### Manual Testing
```bash
# Health check
curl http://localhost:3300/health

# Register user
curl -X POST http://localhost:3300/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login user
curl -X POST http://localhost:3300/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Upload file
curl -X POST http://localhost:3300/api/files/vehicle-fleet/upload \
  -F "file=@your_data_file.xlsx"
```

## 📊 Data Analysis Features

### Vehicle Replacement Analysis
- 10-year replacement forecasting (2026-2035)
- Cost analysis by vehicle class (Heavy, Light, Pickup)
- LOB-specific analysis (DP&C, UOS, Customer Ops, etc.)
- Equipment type categorization

### EV Transition Planning
- Electric vehicle adoption analysis
- ICE vs EV cost comparisons
- Transition timeline planning
- Budget impact analysis

### Radio Equipment Analysis
- Installation cost tracking
- LOB-based radio deployment
- Annual spend forecasting
- Equipment count analysis

## 🛠️ Development

### Adding New Endpoints

1. **Create route** in appropriate `routes/` file
2. **Add controller method** in `controllers/`
3. **Implement business logic** in `services/`
4. **Update documentation**

### Configuration Management

All configuration is centralized in `constants/file_constants.py`:
- File paths
- Database configuration  
- Script paths
- Server settings

## 🚨 Error Handling

The API returns standardized error responses:

```json
{
  "success": false,
  "message": "Error description"
}
```

Common HTTP status codes:
- `200` - Success
- `201` - Created (registration)
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication failed)
- `404` - Not Found
- `500` - Internal Server Error

## 📝 Logging

- Server startup information
- File processing status
- Error tracking
- User activity logging

## 🔄 Version History

- **v1.0.0** - Initial release with full functionality
  - Authentication system
  - File management
  - Data processing scripts
  - Comprehensive analysis features

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Update documentation
4. Test all endpoints before committing

## 📞 Support

For issues or questions regarding the Vehicle Fleet Management API backend, please refer to the API documentation files or contact the development team.