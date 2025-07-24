from django.urls import path
from .template_views import (
    ProductListView, ProductDetailView, ProductCreateView,
    CategoryListView, CategoryCreateView,
    product_approve_reject, upload_video, video_status
)
from .export_views import (
    ExportView, ExportProductsCSVView, ExportProductsExcelView, ExportCategoriesCSVView
)
from .generator_views import (
    DummyDataGeneratorView, GenerateDummyDataView, DummyDataProgressView
)

urlpatterns = [
    # Product URLs
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/create/', ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/review/', product_approve_reject, name='product_approve_reject'),
    
    # Category URLs  
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    
    # Video URLs
    path('products/<int:product_id>/upload-video/', upload_video, name='upload_video'),
    path('products/<int:product_id>/video-status/', video_status, name='video_status'),
    
    # Export URLs
    path('export/', ExportView.as_view(), name='export_data'),
    path('export/products/csv/', ExportProductsCSVView.as_view(), name='export_products_csv'),
    path('export/products/excel/', ExportProductsExcelView.as_view(), name='export_products_excel'),
    path('export/categories/csv/', ExportCategoriesCSVView.as_view(), name='export_categories_csv'),
    
    # Dummy Data Generator URLs
    path('generator/', DummyDataGeneratorView.as_view(), name='dummy_generator'),
    path('generator/generate/', GenerateDummyDataView.as_view(), name='generate_dummy_data'),
    path('generator/progress/', DummyDataProgressView.as_view(), name='dummy_data_progress'),
]
