# Vehicle Fleet Management API - Complete Documentation

## Base URL
```
http://localhost:3300
```

## Authentication

All authentication endpoints use JSON requests and responses.

### Register User
**POST** `/api/auth/register`

Register a new user account.

**Request Body:**
```json
{
  "username": "string (required, min 3 chars)",
  "email": "string (required, valid email)",
  "password": "string (required, min 6 chars)",
  "full_name": "string (optional)",
  "role": "string (optional, default: 'user')"
}
```

**Success Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "role": "user"
  }
}
```

**Error Responses:**
- `400` - Username already exists, Email already exists, Validation errors
- `500` - Internal server error

---

### Login User
**POST** `/api/auth/login`

Authenticate user credentials.

**Request Body:**
```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "role": "user"
  }
}
```

**Error Responses:**
- `401` - Invalid credentials, Account disabled
- `500` - Internal server error

---

### Get All Users
**GET** `/api/auth/users`

Retrieve all registered users (passwords excluded).

**Success Response (200):**
```json
{
  "success": true,
  "count": 2,
  "users": [
    {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "full_name": "Test User",
      "role": "user",
      "created_at": "2025-08-03 21:09:28",
      "last_login": "2025-08-03 21:09:31",
      "is_active": true
    }
  ]
}
```

---

### Get User Statistics
**GET** `/api/auth/stats`

Get user account statistics.

**Success Response (200):**
```json
{
  "success": true,
  "stats": {
    "total_users": 2,
    "active_users": 2,
    "inactive_users": 0
  }
}
```

---

## File Management

### Upload Vehicle Fleet Data
**POST** `/api/files/vehicle-fleet/upload`

Upload Excel file containing vehicle fleet master data.

**Request:**
- Content-Type: `multipart/form-data`
- File field: `file`
- Accepted formats: `.xlsx`
- Max file size: 100MB

**Success Response (200):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file_path": "database/vehicle_fleet_master_data.xlsx"
}
```

**Error Responses:**
- `400` - No file provided, Invalid file format
- `500` - Upload failed

---

### Get Vehicle Fleet Data
**GET** `/api/files/vehicle-fleet/data`

Retrieve all vehicle fleet data.

**Success Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "Equipment": "Vehicle123",
      "Make": "Ford",
      "Model": "Transit",
      "Year": 2022,
      "Cost": 45000,
      "Location": "DP&C"
    }
  ],
  "columns": ["Equipment", "Make", "Model", "Year", "Cost", "Location"],
  "row_count": 6408
}
```

**Error Responses:**
- `404` - File not found
- `500` - Failed to read data

---

### Upload Equipment Lifecycle Data
**POST** `/api/files/equipment-lifecycle/upload`

Upload Excel file containing equipment lifecycle reference data.

**Request:**
- Content-Type: `multipart/form-data`
- File field: `file`
- Accepted formats: `.xlsx`
- Max file size: 100MB

**Success Response (200):**
```json
{
  "success": true,
  "message": "File uploaded successfully",
  "file_path": "database/equipment_lifecycle_reference.xlsx"
}
```

---

## Script Execution

### Run Excel Reader Analysis
**POST** `/api/scripts/excel-reader/run`

Execute comprehensive data analysis and generate multiple report files.

**Success Response (200):**
```json
{
  "success": true,
  "message": "Excel reader completed successfully",
  "output": "=== Vehicle Data Calculation for 10-Year Plan (2026-2035) ===\n\n2026 - Vehicle Counts..."
}
```

**Generated Files:**
- `electric_vehicle_budget_analysis.xlsx`
- `radio_equipment_cost_analysis.xlsx`
- `vehicle_replacement_detailed_forecast.xlsx`
- `vehicle_replacement_by_category.xlsx`

**Error Responses:**
- `500` - Script execution failed (with detailed error message)

---

### Run LOB Pivot Generator
**POST** `/api/scripts/lob-pivot-generator/run`

Generate Line of Business equipment lifecycle pivot tables.

**Success Response (200):**
```json
{
  "success": true,
  "message": "LOB pivot generator completed successfully",
  "output": "Processing LOB data..."
}
```

**Generated Files:**
- `equipment_lifecycle_by_business_unit.xlsx`

---

### Run OOL Reader
**POST** `/api/scripts/ool-reader/run`

Process Out-of-Life equipment data and update schedules.

**Success Response (200):**
```json
{
  "success": true,
  "message": "OOL reader completed successfully",
  "output": "Processing OOL data..."
}
```

---

## Health & Information

### Health Check
**GET** `/health`

Check API server health status.

**Response (200):**
```json
{
  "status": "healthy",
  "database": true
}
```

---

### API Information
**GET** `/`

Get API service information and available endpoints.

**Response (200):**
```json
{
  "service": "Vehicle Fleet Management API",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "upload_vehicle_fleet": "POST /api/files/vehicle-fleet/upload",
    "get_vehicle_fleet": "GET /api/files/vehicle-fleet/data",
    "upload_equipment_lifecycle": "POST /api/files/equipment-lifecycle/upload",
    "run_excel_reader": "POST /api/scripts/excel-reader/run",
    "run_lob_pivot_generator": "POST /api/scripts/lob-pivot-generator/run",
    "run_ool_reader": "POST /api/scripts/ool-reader/run"
  }
}
```

---

## Error Handling

All API endpoints return consistent error response format:

```json
{
  "success": false,
  "message": "Detailed error description"
}
```

### Common HTTP Status Codes

- **200** - OK (Success)
- **201** - Created (Successful registration)
- **400** - Bad Request (Validation errors, missing data)
- **401** - Unauthorized (Authentication failed)
- **404** - Not Found (Resource not found)
- **500** - Internal Server Error (Server-side errors)

---

## Request Examples

### cURL Examples

**Register User:**
```bash
curl -X POST http://localhost:3300/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com", 
    "password": "securepass123",
    "full_name": "New User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:3300/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepass123"
  }'
```

**Upload File:**
```bash
curl -X POST http://localhost:3300/api/files/vehicle-fleet/upload \
  -F "file=@vehicle_data.xlsx"
```

**Run Analysis:**
```bash
curl -X POST http://localhost:3300/api/scripts/excel-reader/run
```

### JavaScript Examples

**Using Fetch API:**

```javascript
// Register user
const registerResponse = await fetch('http://localhost:3300/api/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'newuser',
    email: 'newuser@example.com',
    password: 'securepass123'
  })
});

// Upload file
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:3300/api/files/vehicle-fleet/upload', {
  method: 'POST',
  body: formData
});

// Get data
const dataResponse = await fetch('http://localhost:3300/api/files/vehicle-fleet/data');
const vehicleData = await dataResponse.json();
```

---

## Data Processing Features

### Vehicle Analysis Capabilities

1. **10-Year Replacement Forecasting** (2026-2035)
   - Vehicle count projections by year
   - Replacement cost calculations
   - Heavy, Light, and Pickup vehicle categories

2. **Electric Vehicle Transition Analysis**
   - ICE to EV conversion ratios
   - Budget impact analysis
   - Timeline planning for EV adoption

3. **Radio Equipment Cost Analysis**
   - Installation expense tracking
   - LOB-based deployment analysis
   - Annual spend forecasting

4. **Line of Business Analysis**
   - DP&C, UOS, Customer Ops breakdowns
   - Equipment lifecycle by business unit
   - Hierarchical cost analysis

### Generated Reports

All script executions generate Excel files with multiple sheets containing:
- Summary pivot tables
- Detailed hierarchical analysis
- Cost breakdowns by category
- Year-over-year projections
- LOB-specific insights

---

## Rate Limiting & Performance

- **File Upload Limit**: 100MB per request
- **Concurrent Requests**: No explicit limit (Flask default)
- **Script Execution Timeout**: 5 minutes for excel-reader, 2 minutes for others
- **Database**: Excel files provide adequate performance for current data volumes

---

## Security Considerations

- **Password Security**: SHA-256 hashing (consider upgrading to bcrypt for production)
- **File Uploads**: Secure filename handling, type validation
- **Input Validation**: Comprehensive request data validation
- **Error Messages**: Non-revealing error messages for security

---

## Development & Testing

### Testing All Endpoints

Use the provided cURL examples or create automated tests using your preferred testing framework. All endpoints return JSON responses with consistent structure for easy parsing and error handling.