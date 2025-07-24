from django.urls import path
from .views import (
    CategoryListCreateView, CategoryDetailView,
    ProductListCreateView, ProductDetailView,
    ProductApproveRejectView
)

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view()),
    path('categories/<int:pk>/', CategoryDetailView.as_view()),

    path('products/', ProductListCreateView.as_view()),
    path('products/<int:pk>/', ProductDetailView.as_view()),
    path('products/<int:pk>/review/', ProductApproveRejectView.as_view()),  # POST with action: approve/reject
]
