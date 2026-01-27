from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class Apartment(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Maintenance'),
    ]
    
    APARTMENT_TYPES = [
        ('studio', 'Studio'),
        ('1br', '1 Bedroom'),
        ('2br', '2 Bedrooms'),
        ('3br', '3 Bedrooms'),
        ('penthouse', 'Penthouse'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Compound Name")
    apartment_type = models.CharField(max_length=20, choices=APARTMENT_TYPES)
    floor = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(50)])
    unit_number = models.CharField(max_length=10, unique=True, verbose_name="Unit/House Number")
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    size_sqm = models.DecimalField(max_digits=6, decimal_places=2)
    bedrooms = models.IntegerField(validators=[MinValueValidator(0)])
    bathrooms = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    description = models.TextField()
    amenities = models.TextField(help_text='Comma-separated amenities')
    image = models.ImageField(upload_to='apartments/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['floor', 'unit_number']
    
    def __str__(self):
        return f"{self.name} - Unit {self.unit_number}"
    
    def get_amenities_list(self):
        return [a.strip() for a in self.amenities.split(',') if a.strip()]

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='reservations')
    check_in = models.DateField()
    # REMOVED: check_out = models.DateField()
    # REMOVED: months = models.IntegerField(validators=[MinValueValidator(1)], default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # Make nullable since no months to calculate
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_reservations')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - Unit {self.apartment.unit_number}"

    def save(self, *args, **kwargs):
        # REMOVED: self.total_price = self.apartment.price_per_month * self.months
        # Set monthly price as default
        if not self.total_price:
            self.total_price = self.apartment.price_per_month
        
        if self.status == 'approved':
            self.apartment.status = 'occupied'
            self.apartment.save()
        super().save(*args, **kwargs)

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('reservation_approved', 'Reservation Approved'),
        ('reservation_denied', 'Reservation Denied'),
        ('reservation_cancelled', 'Reservation Cancelled'),
        ('new_message', 'New Message Received'),
        ('new_reservation', 'New Reservation Request'), 
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.notification_type}"

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    phone = models.CharField(max_length=20)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=100)
    emergency_phone = models.CharField(max_length=20)
    id_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

# NEW: Conversation model for threading messages
class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    subject = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.subject[:50]}"
    
    def get_other_participant(self, user):
        """Get the other participant in the conversation"""
        return self.participants.exclude(id=user.id).first()
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by('-created_at').first()
    
    def unread_count_for_user(self, user):
        """Count unread messages for a specific user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

# UPDATED: Message model now links to Conversation
class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}..."