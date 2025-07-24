from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from faker import Faker
import random
import threading
import time

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate dummy products and categories with threading support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--products',
            type=int,
            default=10,
            help='Number of products to generate (default: 10)'
        )
        parser.add_argument(
            '--categories',
            type=int,
            default=5,
            help='Number of categories to generate (default: 5)'
        )
        parser.add_argument(
            '--threads',
            type=int,
            default=4,
            help='Number of threads to use (default: 4)'
        )

    def handle(self, *args, **options):
        fake = Faker()
        products_count = options['products']
        categories_count = options['categories']
        threads_count = options['threads']

        self.stdout.write(
            self.style.SUCCESS(f'Starting to generate {products_count} products and {categories_count} categories using {threads_count} threads...')
        )

        # Create categories first
        self.create_categories(fake, categories_count)
        
        # Create users if needed (agents to own products)
        self.create_users(fake)
        
        # Create products using threading
        self.create_products_with_threading(fake, products_count, threads_count)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated {products_count} products and {categories_count} categories!')
        )

    def create_categories(self, fake, count):
        """Create categories"""
        self.stdout.write('Creating categories...')
        
        category_names = set()
        while len(category_names) < count:
            category_names.add(fake.word().capitalize() + ' Category')
        
        for name in category_names:
            Category.objects.get_or_create(name=name)
        
        self.stdout.write(self.style.SUCCESS(f'Created {count} categories'))

    def create_users(self, fake):
        """Create agent users if they don't exist"""
        if User.objects.filter(role='agent').count() < 3:
            for i in range(3):
                username = f'agent_{i+1}'
                if not User.objects.filter(username=username).exists():
                    User.objects.create_user(
                        username=username,
                        email=fake.email(),
                        password='password123',
                        role='agent'
                    )
        
        self.stdout.write(self.style.SUCCESS('Created agent users'))

    def create_products_with_threading(self, fake, total_products, thread_count):
        """Create products using multiple threads"""
        categories = list(Category.objects.all())
        agents = list(User.objects.filter(role='agent'))
        
        if not categories:
            self.stdout.write(self.style.ERROR('No categories found. Please create categories first.'))
            return
        
        if not agents:
            self.stdout.write(self.style.ERROR('No agent users found. Creating default agent...'))
            agent = User.objects.create_user(
                username='default_agent',
                email=fake.email(),
                password='password123',
                role='agent'
            )
            agents = [agent]

        # Calculate products per thread
        products_per_thread = total_products // thread_count
        remaining_products = total_products % thread_count

        threads = []
        start_index = 0

        for i in range(thread_count):
            # Last thread gets remaining products
            count = products_per_thread + (remaining_products if i == thread_count - 1 else 0)
            
            thread = threading.Thread(
                target=self.create_products_batch,
                args=(fake, categories, agents, count, start_index + 1)
            )
            threads.append(thread)
            start_index += count

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    def create_products_batch(self, fake, categories, agents, count, start_index):
        """Create a batch of products (thread worker)"""
        thread_id = threading.current_thread().name
        self.stdout.write(f'Thread {thread_id}: Creating {count} products starting from index {start_index}')
        
        statuses = ['uploaded', 'approved', 'rejected', 'cancelled']
        
        for i in range(count):
            try:
                # Simulate some processing time
                time.sleep(0.1)
                
                product = Product.objects.create(
                    category=random.choice(categories),
                    title=fake.catch_phrase(),
                    description=fake.text(max_nb_chars=500),
                    price=round(random.uniform(10.00, 999.99), 2),
                    status=random.choice(statuses),
                    created_by=random.choice(agents)
                )
                
                if i % 50 == 0:  # Progress indicator
                    self.stdout.write(f'Thread {thread_id}: Created {i+1}/{count} products')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Thread {thread_id}: Error creating product {i+1}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Thread {thread_id}: Completed creating {count} products')
        )
