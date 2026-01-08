import json
import os
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .services import dr_service, analysis_storage
# from .mongodb_models import mongodb_manager

logger = logging.getLogger(__name__)

def landing_view(request):
    """Landing page view"""
    # Add model accuracy information for landing page
    model_stats = {
        'accuracy': 74.01,
        'model_type': 'Simple CNN',
        'training_date': 'December 3, 2025'
    }
    
    return render(request, 'prediction/landing.html', {
        'model_stats': model_stats
    })

@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required
def home_view(request):
    """Main application view"""
    if request.method == 'GET':
        
        # Get user's recent analyses from database
        from .models import UserAnalysis, CustomUser
        user_analyses = UserAnalysis.objects.filter(user=request.user).order_by('-date')[:10]
        
        # Calculate stats based on user's data
        total_analyses = UserAnalysis.objects.filter(user=request.user).count()
        unique_users = CustomUser.objects.count()
        
        stats = {
            'total_analyses': total_analyses,
            'completed_analyses': total_analyses,  # All stored analyses are completed
            'pending_analyses': 0,
            'unique_users': unique_users,
            'accuracy': 74.01
        }
        
        # Add model accuracy information
        model_stats = {
            'accuracy': 74.01,
            'model_type': 'Simple CNN',
            'training_date': 'December 3, 2025'
        }
        
        return render(request, 'prediction/home.html', {
            'user': request.user,
            'recent_analyses': user_analyses,
            'stats': stats,
            'model_stats': model_stats
        })
    return JsonResponse({'message': 'DR Detection API', 'version': '1.0'})

@csrf_exempt
@require_http_methods(["POST"])
def predict_image(request):
    """Handle image upload and prediction"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No image file provided',
                'demo_mode': False
            }, status=400)
        
        image_file = request.FILES['image']
        
        # Validate file type
        if not image_file.content_type.startswith('image/'):
            return JsonResponse({
                'success': False,
                'error': 'Invalid file type. Please upload an image.',
                'demo_mode': False
            }, status=400)
        
        # Validate file size (max 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'File too large. Maximum size is 10MB.',
                'demo_mode': False
            }, status=400)
        
        # Process the image
        result = dr_service.process_image(image_file)
        
        # Add demo mode flag to response
        result['demo_mode'] = dr_service.demo_mode
        
        if result.get('success', False):
            # Store analysis result for recent results display and database
            try:
                analysis_storage.add_analysis(
                    prediction_result=result.get('prediction', 'Unknown'),
                    confidence_scores=result.get('confidence', 0),
                    image_name=image_file.name
                )
                logger.info(f"Analysis result stored: {result.get('prediction')}")
                
                # Also save to database for reports
                from .models import UserAnalysis
                UserAnalysis.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    prediction_result=result.get('prediction', 'Unknown'),
                    confidence_scores=result.get('confidence', 0),
                    session_id=request.session.session_key or 'anonymous'
                )
                logger.info(f"Analysis saved to database: {result.get('prediction')}")
            except Exception as e:
                logger.warning(f"Failed to store analysis result: {e}")
            
            # Generate graph for visualization
            if 'all_probabilities' in result:
                graph_path = dr_service._generate_graph(
                    [p/100 for p in result['all_probabilities']]
                )
                if graph_path:
                    result['graph_url'] = f'/media/{os.path.basename(graph_path)}'
            
            return JsonResponse(result)
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Prediction failed'),
                'demo_mode': result.get('demo_mode', False)
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error in predict_image: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'demo_mode': True
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'model_loaded': dr_service.model is not None,
        'demo_mode': dr_service.model is None
    })

@csrf_exempt
@require_http_methods(["GET"])
def model_info(request):
    """Get model information"""
    class_info = [
        {'name': label, 'description': get_class_description(label)}
        for label in dr_service.class_labels
    ]
    
    return JsonResponse({
        'model_type': 'Convolutional Neural Network',
        'input_shape': [224, 224, 3],
        'classes': class_info,
        'model_loaded': dr_service.model is not None,
        'demo_mode': dr_service.model is None
    })

def get_class_description(class_name):
    """Get description for each class"""
    descriptions = {
        'No DR': 'No signs of diabetic retinopathy detected',
        'Mild': 'Mild non-proliferative diabetic retinopathy',
        'Moderate': 'Moderate non-proliferative diabetic retinopathy',
        'Severe': 'Severe non-proliferative diabetic retinopathy',
        'Proliferative': 'Proliferative diabetic retinopathy'
    }
    return descriptions.get(class_name, 'Diabetic retinopathy classification')

def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        
        # Validate input
        if not username or not email or not password:
            messages.error(request, 'All required fields must be filled.')
            return render(request, 'prediction/register.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'prediction/register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'prediction/register.html')
        
        # Validate age if provided
        if age and (int(age) < 1 or int(age) > 120):
            messages.error(request, 'Please enter a valid age between 1 and 120.')
            return render(request, 'prediction/register.html')
        
        # Create user with Django CustomUser model
        from .models import CustomUser
        
        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                age=int(age) if age else None,
                gender=gender if gender else None
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('prediction:login')
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
    
    return render(request, 'prediction/register.html')

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        from django.contrib.auth import authenticate, login
        
        # Authenticate with Django
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('prediction:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'prediction/login.html')

def logout_view(request):
    """Handle user logout"""
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('prediction:login')

@login_required
def dataset_view(request):
    """Display static dataset information page"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('prediction:login')
    
    return render(request, 'prediction/dataset.html', {
        'user': request.user,
        'request': request
    })

@login_required
def performance_view(request):
    """Display model performance analysis"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('prediction:login')
    
    # Load real performance data from existing model
    try:
        # Read the detailed performance report
        performance_data = {
            'model_type': 'Simple CNN',
            'validation_accuracy': 0.7401,
            'validation_accuracy_percent': 74.01,
            'total_validation_samples': 731,
            'per_class_performance': {
                'No_DR': {'accuracy': 0.975, 'accuracy_percent': 97.5, 'samples': 361},
                'Mild': {'accuracy': 0.216, 'accuracy_percent': 21.6, 'samples': 74},
                'Moderate': {'accuracy': 0.854, 'accuracy_percent': 85.4, 'samples': 199},
                'Severe': {'accuracy': 0.079, 'accuracy_percent': 7.9, 'samples': 38},
                'Proliferate_DR': {'accuracy': 0.000, 'accuracy_percent': 0.0, 'samples': 59}
            },
            'confidence_stats': {
                'mean_confidence': 0.756,
                'mean_confidence_percent': 75.6,
                'median_confidence': 0.784,
                'median_confidence_percent': 78.4,
                'min_confidence': 0.304,
                'max_confidence': 1.000,
                'high_confidence_count': 277,
                'low_confidence_count': 206
            },
            'classification_report': {
                'precision': {'No_DR': 0.91, 'Mild': 0.64, 'Moderate': 0.54, 'Severe': 0.60, 'Proliferate_DR': 0.00},
                'recall': {'No_DR': 0.98, 'Mild': 0.22, 'Moderate': 0.85, 'Severe': 0.08, 'Proliferate_DR': 0.00},
                'f1_score': {'No_DR': 0.94, 'Mild': 0.32, 'Moderate': 0.66, 'Severe': 0.14, 'Proliferate_DR': 0.00}
            },
            'training_params': {
                'batch_size': 32,
                'epochs': 30,
                'learning_rate': 0.001
            },
            'training_date': '2025-12-03T08:57:17.163717'
        }
        
        return render(request, 'prediction/performance.html', {
            'performance_data': performance_data,
            'user': request.user,
            'request': request
        })
        
    except Exception as e:
        # Fallback to basic performance data if file reading fails
        basic_performance = {
            'model_type': 'Simple CNN',
            'validation_accuracy': 0.74,
            'validation_accuracy_percent': 74.0,
            'training_status': 'Completed'
        }
        
        return render(request, 'prediction/performance.html', {
            'performance_data': basic_performance,
            'user': request.user,
            'request': request
        })

@login_required
def report_view(request):
    """Display query/report page"""
    from .models import UserAnalysis
    
    # Get user's analysis reports - user must be authenticated
    if not request.user.is_authenticated:
        return redirect('prediction:login')
    
    user_analyses = UserAnalysis.objects.filter(user=request.user).order_by('-date')[:50]
    
    # Calculate statistics
    total_reports = user_analyses.count()
    completed_reports = total_reports  # All are completed in this simple version
    pending_reports = 0
    
    return render(request, 'prediction/report.html', {
        'user': request.user,
        'user_analyses': user_analyses,
        'total_reports': total_reports,
        'completed_reports': completed_reports,
        'pending_reports': pending_reports,
        'request': request
    })

@login_required
def parameters_view(request):
    """Display retinal image parameters"""
    # Check if user is authenticated
    if not request.user.is_authenticated:
        return redirect('prediction:login')
    
    return render(request, 'prediction/parameters.html', {
        'user': request.user,
        'request': request
    })
