from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
import threading
import time

from .models import Category, Product, ProductVideo
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


# threading function to process video uploads
def process_video(video_id):
    def run():
        try:
            video = ProductVideo.objects.get(id=video_id)
            video.status = 'processing'
            video.save()
            
            # Simulate heavy processing
            time.sleep(3)

            video.status = 'done'
            video.save()
        except Exception as e:
            video.status = 'failed'
            video.save()

    thread = threading.Thread(target=run)
    thread.start()


# View to handle video uploads for products
class ProductVideoUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        videos = request.FILES.getlist('videos')

        if not videos:
            return Response({'detail': 'No videos provided'}, status=400)

        if len(videos) > 5:
            return Response({'detail': 'Max 5 videos allowed'}, status=400)

        total_size = sum(v.size for v in videos)
        if total_size > 20 * 1024 * 1024:
            return Response({'detail': 'Total video size exceeds 20MB'}, status=400)

        uploaded_video_ids = []

        for video in videos:
            pv = ProductVideo.objects.create(product=product, video_file=video, status='pending')
            uploaded_video_ids.append(pv.id)
            process_video(pv.id)

        return Response({'detail': 'Videos uploaded & processing started', 'video_ids': uploaded_video_ids})

class ProductVideoStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        videos = ProductVideo.objects.filter(product_id=product_id)
        return Response([
            {'id': v.id, 'status': v.status, 'file': v.video_file.url} for v in videos
        ])
