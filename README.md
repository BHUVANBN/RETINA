# Diabetic Retinopathy Detection AI

An industry-level Django application for AI-powered detection and classification of diabetic retinopathy using deep learning.

## 🚀 Features

- **AI-Powered Classification**: Advanced CNN model for 5-level diabetic retinopathy severity detection
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS
- **Real-time Analysis**: Fast image processing with confidence scores
- **Production Ready**: Docker containerization, Nginx configuration, deployment optimized
- **API Endpoints**: RESTful API for integration with other systems
- **Health Monitoring**: Built-in health checks and model status monitoring
- **Error Handling**: Comprehensive error handling with fallback demo mode
- **Security**: Production security configurations, CSRF protection, file validation

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 5.0.7 with Python 3.11
- **ML Framework**: TensorFlow 2.16.1, Keras 3.3.3
- **Frontend**: Tailwind CSS, vanilla JavaScript
- **Deployment**: Docker, Gunicorn, Nginx
- **Database**: SQLite (development), PostgreSQL (production ready)

### Model Information
- **Model Type**: Convolutional Neural Network (CNN)
- **Input**: 224×224×3 RGB images
- **Classes**: No DR, Mild, Moderate, Severe, Proliferative DR
- **Format**: Keras H5 with TensorFlow compatibility

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Git

### Quick Start (Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/Madhuanandalli/retinaAI.git
   cd retinaAI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   *Note: All required dependencies including `django-cors-headers` and `psutil` are now included in requirements.txt*

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Start development server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

8. **Access the application**
   - Web Interface: http://localhost:8000/prediction/
   - Admin Panel: http://localhost:8000/admin/
   - API Health: http://localhost:8000/prediction/health/

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - Application: http://localhost:8000/prediction/
   - Health Check: http://localhost:8000/prediction/health/

### Production Deployment

1. **Environment Setup**
   ```bash
   # Set production environment variables
   export DEBUG=False
   export SECRET_KEY=your-secure-secret-key
   export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **SSL Configuration**
   - Place SSL certificates in `ssl/` directory
   - Update `nginx.conf` with your domain
   - Uncomment HTTPS server block

3. **Database Setup**
   - Configure PostgreSQL in `settings.py`
   - Update `docker-compose.yml` with database service

4. **Deploy**
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | auto-generated |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `SECURE_SSL_REDIRECT` | HTTPS redirect | `False` (dev) |

### Model Configuration

The trained model is located at:
```
prediction/keras_model.h5
```

To update the model:
1. Replace the model file
2. Ensure compatibility with TensorFlow 2.16+
3. Test with sample images

## 📚 API Documentation

### Endpoints

#### `GET /prediction/health/`
Health check endpoint
```json
{
  "status": "healthy",
  "model_loaded": true,
  "demo_mode": false
}
```

#### `GET /prediction/model-info/`
Model information
```json
{
  "model_type": "Convolutional Neural Network",
  "input_shape": [224, 224, 3],
  "classes": [...],
  "model_loaded": true,
  "demo_mode": false
}
```

#### `POST /prediction/predict/`
Image prediction
- **Content-Type**: `multipart/form-data`
- **Body**: `image` (file)
- **Max Size**: 10MB

Response:
```json
{
  "success": true,
  "prediction": "Moderate",
  "confidence": 85.5,
  "all_probabilities": [5.2, 12.1, 85.5, 4.8, 2.4],
  "graph_url": "/media/graphs/prediction_graph.png"
}
```

## 🔒 Security Features

- **CSRF Protection**: Enabled for all forms
- **File Validation**: Type and size validation
- **Rate Limiting**: Configurable rate limits
- **Security Headers**: XSS protection, content type options
- **HTTPS Ready**: SSL/TLS configuration included
- **Environment Variables**: Sensitive data externalized

## 📊 Performance Optimization

- **Static File Serving**: Optimized with Nginx
- **Gzip Compression**: Enabled for text-based files
- **Caching**: Browser caching for static assets
- **Connection Pooling**: Gunicorn worker optimization
- **Memory Management**: Efficient image processing

## 🚨 Monitoring & Logging

### Health Checks
- Application health endpoint
- Model loading status
- Database connectivity

### Logging
- Application logs: `dr_detection.log`
- Access logs via Nginx
- Error tracking and debugging

## 🧪 Testing

### Running Tests
```bash
python manage.py test
```

### Model Testing
1. Place test images in `prediction/test_images/`
2. Use the web interface for manual testing
3. Check API responses with curl/Postman

## 📁 Project Structure

```
DR_refin/
├── dr_detection/          # Django project settings
├── prediction/            # Main Django app
│   ├── services.py        # ML processing logic
│   ├── views.py           # API views
│   ├── keras_model.h5     # Trained model
│   └── output/            # Generated graphs
├── templates/             # HTML templates
├── static/               # CSS, JS, images
├── media/                # User uploads
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-container setup
├── nginx.conf           # Web server config
├── gunicorn.conf.py    # WSGI server config
└── requirements.txt     # Python dependencies
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is for research and educational purposes only. It should not be used as a substitute for professional medical diagnosis. Always consult qualified healthcare professionals for medical decisions.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs
- Create an issue on GitHub
- Contact the development team

## 🔄 Updates & Maintenance

- Regular model updates recommended
- Monitor system health and performance
- Keep dependencies updated
- Backup database and media files regularly

## 🐛 Troubleshooting

### Common Setup Issues

#### Missing Dependencies
If you encounter import errors for `corsheaders` or `psutil`:
```bash
pip install django-cors-headers psutil
```
These are now included in requirements.txt but may need manual installation for existing setups.

#### Migration Issues
If migrations fail:
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

#### Static Files Not Loading
If CSS/JS files don't load:
```bash
python manage.py collectstatic --noinput --clear
```

#### Server Access Issues
If you can't access the application:
1. Ensure server is running on `0.0.0.0:8000` (not just `127.0.0.1:8000`)
2. Check firewall settings
3. Verify no other service is using port 8000

#### Model Loading Issues
The application runs in demo mode if TensorFlow model fails to load. This is normal and provides full UI functionality with sample predictions.

### Log Files
- Application logs: `dr_detection.log`
- Django debug output: Console when running `runserver`

### Health Check
Always verify system status:
```bash
curl http://localhost:8000/prediction/health/
```

###Model
Dowload and add the Model to the prediction/
```
https://drive.google.com/file/d/1kde76ejx99y9BRN-SU-hKb-NOzYk7kW4/view?usp=sharing
```
