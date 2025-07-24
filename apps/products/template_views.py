from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
import json

from .models import Product, Category, ProductVideo
from .forms import ProductForm, CategoryForm, AdminProductForm
from .permissions import IsAdmin, IsStaff


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Product.objects.all()
        elif user.role == 'staff':
            return Product.objects.filter(status='uploaded')
        elif user.role == 'agent':
            return Product.objects.filter(created_by=user)
        elif user.role == 'end_user':
            return Product.objects.filter(status='approved')
        return Product.objects.none()


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['videos'] = ProductVideo.objects.filter(product=self.object)
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    template_name = 'products/product_create.html'
    success_url = reverse_lazy('product_list')
    
    def get_form_class(self):
        if self.request.user.role == 'admin':
            return AdminProductForm
        return ProductForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = self.request.user.role == 'admin'
        return context
    
    def form_valid(self, form):
        if self.request.user.role not in ['agent', 'admin']:
            raise PermissionDenied("Only agents and admins can create products.")
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_create.html'
    success_url = reverse_lazy('category_list')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admins can create categories.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_edit.html'
    success_url = reverse_lazy('category_list')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admins can edit categories.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admins can delete categories.")
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        category_name = category.name
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Category "{category_name}" deleted successfully!')
            return response
        except Exception as e:
            messages.error(request, f'Cannot delete category "{category_name}". It may be used by existing products.')
            return redirect('category_list')


@login_required
@require_POST
def product_approve_reject(request, pk):
    if request.user.role not in ['admin', 'staff']:
        raise PermissionDenied("Only staff and admin can approve/reject products.")
    
    product = get_object_or_404(Product, pk=pk, status='uploaded')
    action = request.POST.get('action')
    
    if action == 'approve':
        product.status = 'approved'
        messages.success(request, f'Product "{product.title}" approved successfully!')
    elif action == 'reject':
        product.status = 'rejected'
        messages.success(request, f'Product "{product.title}" rejected.')
    else:
        messages.error(request, 'Invalid action.')
        return redirect('product_detail', pk=pk)
    
    product.save()
    return redirect('product_detail', pk=pk)


@login_required
def upload_video(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    
    if request.method == 'POST':
        videos = request.FILES.getlist('videos')
        
        if not videos:
            messages.error(request, 'No videos provided')
            return redirect('product_detail', pk=product_id)
        
        if len(videos) > 5:
            messages.error(request, 'Maximum 5 videos allowed')
            return redirect('product_detail', pk=product_id)
        
        total_size = sum(v.size for v in videos)
        if total_size > 20 * 1024 * 1024:
            messages.error(request, 'Total video size exceeds 20MB')
            return redirect('product_detail', pk=product_id)
        
        uploaded_count = 0
        for video in videos:
            ProductVideo.objects.create(
                product=product, 
                video_file=video, 
                status='pending'
            )
            uploaded_count += 1
        
        messages.success(request, f'{uploaded_count} videos uploaded successfully!')
        return redirect('product_detail', pk=product_id)
    
    return render(request, 'products/upload_video.html', {'product': product})


@login_required  
def video_status(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    videos = ProductVideo.objects.filter(product=product)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        video_data = [
            {
                'id': v.id, 
                'status': v.status, 
                'file': v.video_file.url if v.video_file else None
            } 
            for v in videos
        ]
        return JsonResponse({'videos': video_data})
    
    return render(request, 'products/video_status.html', {
        'product': product, 
        'videos': videos
    })
