from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from .permissions import IsAdmin, IsOwnerOrAdmin, IsStaff

# CATEGORY VIEWS (Only Admin)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdmin]

# PRODUCT VIEWS
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

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

    def perform_create(self, serializer):
        if self.request.user.role != 'agent':
            raise PermissionDenied("Only agents can create products.")
        serializer.save(created_by=self.request.user)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

# STAFF ONLY: Approve/Reject
from rest_framework.views import APIView

class ProductApproveRejectView(APIView):
    permission_classes = [IsStaff]

    def post(self, request, pk):
        action = request.data.get('action')  # "approve" or "reject"
        if action not in ['approve', 'reject']:
            return Response({"detail": "Invalid action"}, status=400)

        try:
            product = Product.objects.get(pk=pk, status='uploaded')
        except Product.DoesNotExist:
            return Response({"detail": "Product not found or already reviewed"}, status=404)

        product.status = 'approved' if action == 'approve' else 'rejected'
        product.save()
        return Response({"detail": f"Product {action}d successfully."})
