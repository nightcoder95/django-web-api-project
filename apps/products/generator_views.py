from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, View
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.core.management import call_command
from django.contrib.auth import get_user_model
import threading
import time

User = get_user_model()

class DummyDataGeneratorView(LoginRequiredMixin, TemplateView):
    """Web interface for generating dummy data"""
    template_name = 'products/dummy_generator.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Only admin can generate dummy data
        if request.user.role != 'admin':
            raise PermissionDenied("Only admin users can generate dummy data.")
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .models import Product, Category
        
        context.update({
            'current_products_count': Product.objects.count(),
            'current_categories_count': Category.objects.count(),
            'agent_users_count': User.objects.filter(role='agent').count(),
        })
        return context


class GenerateDummyDataView(LoginRequiredMixin, View):
    """Handle dummy data generation via web interface"""
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admin users can generate dummy data.")
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            products_count = int(request.POST.get('products', 10))
            categories_count = int(request.POST.get('categories', 5))
            threads_count = int(request.POST.get('threads', 4))
            
            # Validate inputs
            if products_count > 10000:
                messages.error(request, 'Maximum 10,000 products allowed.')
                return redirect('dummy_generator')
            
            if categories_count > 100:
                messages.error(request, 'Maximum 100 categories allowed.')
                return redirect('dummy_generator')
                
            if threads_count > 10:
                messages.error(request, 'Maximum 10 threads allowed.')
                return redirect('dummy_generator')
            
            # Run generation in background thread
            generation_thread = threading.Thread(
                target=self._generate_data_background,
                args=(products_count, categories_count, threads_count, request.user.id)
            )
            generation_thread.daemon = True
            generation_thread.start()
            
            messages.success(
                request, 
                f'Started generating {products_count} products and {categories_count} categories in background. '
                f'This may take a few minutes to complete.'
            )
            
            # For AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Generation started with {products_count} products and {categories_count} categories'
                })
            
            return redirect('dummy_generator')
            
        except ValueError:
            messages.error(request, 'Please enter valid numbers.')
            return redirect('dummy_generator')
        except Exception as e:
            messages.error(request, f'Error starting generation: {str(e)}')
            return redirect('dummy_generator')
    
    def _generate_data_background(self, products_count, categories_count, threads_count, user_id):
        """Run dummy data generation in background"""
        try:
            call_command(
                'generate_dummy_data',
                products=products_count,
                categories=categories_count,
                threads=threads_count
            )
        except Exception as e:
            print(f"Error generating dummy data: {str(e)}")


class DummyDataProgressView(LoginRequiredMixin, View):
    """AJAX endpoint to check generation progress"""
    
    def get(self, request):
        if request.user.role != 'admin':
            return JsonResponse({'error': 'Permission denied'}, status=403)
        
        from .models import Product, Category
        
        # Simple progress tracking based on current counts
        current_products = Product.objects.count()
        current_categories = Category.objects.count()
        
        return JsonResponse({
            'products_count': current_products,
            'categories_count': current_categories,
            'timestamp': time.time()
        })
