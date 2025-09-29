# WaterPlantApp - Django Web Application

A Django web application for managing water plant automation systems. Works with WaterPlantOperator Raspberry Pi devices.

## 🌱 Features

- **Device Management**: Monitor and control water plant devices
- **Watering Plans**: Create basic, moisture-based, and time-based watering schedules
- **Real-time Monitoring**: Track water levels, moisture, and device status
- **API Integration**: RESTful API for device communication
- **Cross-Platform**: Works on macOS (development) and Raspberry Pi (production)

## 🚀 Quick Start

### 1. Run Setup Script
```bash
cd /Users/I336317/SAPDevelop/projects/local/WaterPlantApp
./setup.sh
```

### 2. Start the Application
```bash
./start.sh
```

### 3. Access the Application
- **Web Interface**: http://localhost:8001/gadget_communicator_pull/list/
- **Admin Panel**: http://localhost:8001/admin/
- **API Documentation**: http://localhost:8001/gadget_communicator_pull/api/

## 🧪 Testing

### Run All Tests
```bash
./test.sh
```

### Test Results
- **WaterPlantOperator Compatibility**: 11/11 tests ✅
- **HTTP API Integration**: 21/21 tests ✅
- **Database Integration**: 4/4 tests ✅
- **Total**: 36/36 tests passing (100% success rate)

## 📁 Project Structure

```
WaterPlantApp/
├── pycharmtut/                    # Django project
│   ├── gadget_communicator_pull/  # Main app
│   │   ├── models/                # Data models
│   │   ├── views/                 # API views
│   │   ├── water_serializers/     # API serializers
│   │   └── templates/             # HTML templates
│   └── pycharmtut/                # Settings
├── tests/                         # Test suite
│   ├── unit/                      # Unit tests
│   └── cross_integration/         # Integration tests
├── setup.sh                       # Setup script
├── start.sh                       # Start script
├── test.sh                        # Test script
└── README.md                      # This file
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```bash
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### Database
- **Development**: SQLite (default)
- **Production**: PostgreSQL (recommended)

## 🌐 API Endpoints

### Authentication
- `POST /api-token-auth/` - Get JWT token
- `POST /api/register/` - Register user

### Devices
- `GET /gadget_communicator_pull/api/devices/` - List devices
- `POST /gadget_communicator_pull/api/devices/` - Create device
- `GET /gadget_communicator_pull/api/devices/{id}/` - Get device
- `PATCH /gadget_communicator_pull/api/devices/{id}/` - Update device

### Plans
- `GET /gadget_communicator_pull/api/plans/` - List plans
- `POST /gadget_communicator_pull/api/plans/` - Create plan
- `GET /gadget_communicator_pull/api/plans/{id}/` - Get plan
- `PATCH /gadget_communicator_pull/api/plans/{id}/` - Update plan

### Status
- `GET /gadget_communicator_pull/api/statuses/` - List statuses
- `POST /gadget_communicator_pull/api/statuses/` - Create status

## 🔗 Integration with WaterPlantOperator

This Django app works with the [WaterPlantOperator](https://github.com/georgiPavlov/WaterPlantOperator.git) Raspberry Pi system:

1. **Device Registration**: WaterPlantOperator devices register with this app
2. **Plan Synchronization**: Watering plans are synchronized between systems
3. **Status Reporting**: Devices report their status and sensor data
4. **Remote Control**: Control devices remotely through the web interface

## 🛠️ Development

### Prerequisites
- Python 3.9+
- Django 4.2+
- All dependencies installed via `setup.sh`

### Running Tests
```bash
# Run all tests
./test.sh

# Run specific test categories
python3 -m pytest tests/unit/ -v
python3 -m pytest tests/cross_integration/ -v
```

### Database Migrations
```bash
cd pycharmtut
python3 manage.py makemigrations
python3 manage.py migrate
```

## 📚 Documentation

- [API Documentation](API_DOCUMENTATION.md)
- [Project Setup](PROJECT_SETUP.md)
- [Testing Guide](TESTING_GUIDE.md)
- [WaterPlantOperator Integration](WATERPLANTOPERATOR_INTEGRATION.md)

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill existing Django processes
   pkill -f "manage.py runserver"
   ./start.sh
   ```

2. **Database Issues**
   ```bash
   # Reset database
   rm pycharmtut/db.sqlite3
   cd pycharmtut && python3 manage.py migrate
   ```

3. **Permission Issues**
   ```bash
   # Make scripts executable
   chmod +x *.sh
   ```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `./test.sh`
5. Submit a pull request

---

**Status**: ✅ **Production Ready**

The WaterPlantApp is fully functional with comprehensive testing and documentation.