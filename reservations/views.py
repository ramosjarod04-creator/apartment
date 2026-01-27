from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from .forms import RegisterForm, TenantProfileForm, ApartmentForm, ReservationForm
from django.contrib.auth.models import User
from .models import Apartment, Reservation, Tenant, Notification, Message, Conversation


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        profile_form = TenantProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            tenant = profile_form.save(commit=False)
            tenant.user = user
            tenant.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
        profile_form = TenantProfileForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'profile_form': profile_form
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            role = "Admin" if user.is_staff else "User"
            messages.success(request, f'Welcome back, {user.first_name or user.username}! ({role})')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    # Statistics
    total_apartments = Apartment.objects.count()
    available_apartments = Apartment.objects.filter(status='available').count()
    
    # Get unread notifications count
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False).count()
    
    # Show different stats based on role
    if request.user.is_staff:
        # ADMIN: See all reservations statistics
        all_reservations = Reservation.objects.all()
        pending_reservations = all_reservations.filter(status='pending').count()
        approved_reservations = all_reservations.filter(status='approved').count()
        
        # FIXED: Admin sees ALL recent reservations, not just their own
        recent_reservations = Reservation.objects.all().order_by('-created_at')[:5]
        
        # Recent reservations to review (from all users)
        reservations_to_review = Reservation.objects.filter(status='pending').order_by('-created_at')[:5]
    else:
        # REGULAR USER: See only their reservations
        user_reservations = Reservation.objects.filter(user=request.user)
        pending_reservations = user_reservations.filter(status='pending').count()
        approved_reservations = user_reservations.filter(status='approved').count()
        recent_reservations = user_reservations[:5]
        reservations_to_review = None
    
    # Featured apartments
    featured_apartments = Apartment.objects.filter(status='available')[:6]
    
    context = {
        'total_apartments': total_apartments,
        'available_apartments': available_apartments,
        'pending_reservations': pending_reservations,
        'approved_reservations': approved_reservations,
        'recent_reservations': recent_reservations,
        'featured_apartments': featured_apartments,
        'unread_notifications': unread_notifications,
        'reservations_to_review': reservations_to_review,  # Only for admin
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'reservations/dashboard.html', context)


@login_required
def apartment_list_view(request):
    apartments = Apartment.objects.all()
    
    # Search and filter
    search = request.GET.get('search', '')
    apartment_type = request.GET.get('type', '')
    status = request.GET.get('status', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    # Debug: Print to console
    print(f"Search: {search}")
    print(f"Type: {apartment_type}")
    print(f"Status: {status}")
    print(f"Total apartments before filter: {apartments.count()}")
    
    if search:
        apartments = apartments.filter(
            Q(name__icontains=search) | 
            Q(unit_number__icontains=search) |
            Q(description__icontains=search)
        )
        print(f"After search filter: {apartments.count()}")
    
    if apartment_type:
        apartments = apartments.filter(apartment_type=apartment_type)
        print(f"After type filter: {apartments.count()}")
    
    if status:
        apartments = apartments.filter(status=status)
        print(f"After status filter: {apartments.count()}")
    
    if min_price:
        apartments = apartments.filter(price_per_month__gte=min_price)
        print(f"After min_price filter: {apartments.count()}")
    
    if max_price:
        apartments = apartments.filter(price_per_month__lte=max_price)
        print(f"After max_price filter: {apartments.count()}")
    
    print(f"Final count: {apartments.count()}")
    
    context = {
        'apartments': apartments,
        'search': search,
        'apartment_type': apartment_type,
        'status': status,
        'min_price': min_price,
        'max_price': max_price,
    }
    
    return render(request, 'reservations/apartment_list.html', context)

@login_required
def apartment_detail_view(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    return render(request, 'reservations/apartment_detail.html', {'apartment': apartment})


@login_required
def apartment_create_view(request):
    if not request.user.is_staff:
        messages.error(request, 'Only admins can add apartments.')
        return redirect('apartment_list')
    
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Apartment added successfully!')
            return redirect('apartment_list')
    else:
        form = ApartmentForm()
    
    return render(request, 'reservations/apartment_form.html', {'form': form, 'action': 'Create'})


@login_required
def apartment_update_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Only admins can edit apartments.')
        return redirect('apartment_list')
    
    apartment = get_object_or_404(Apartment, pk=pk)
    
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES, instance=apartment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Apartment updated successfully!')
            return redirect('apartment_detail', pk=pk)
    else:
        form = ApartmentForm(instance=apartment)
    
    return render(request, 'reservations/apartment_form.html', {'form': form, 'action': 'Update'})


@login_required
def apartment_delete_view(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Only admins can delete apartments.')
        return redirect('apartment_list')
    
    apartment = get_object_or_404(Apartment, pk=pk)
    
    if request.method == 'POST':
        apartment.delete()
        messages.success(request, 'Apartment deleted successfully!')
        return redirect('apartment_list')
    
    return render(request, 'reservations/apartment_confirm_delete.html', {'apartment': apartment})


@login_required
def reservation_list_view(request):
    # ADMIN: Can toggle between "All Reservations" and "My Reservations"
    view_mode = request.GET.get('view', 'all' if request.user.is_staff else 'my')
    
    if request.user.is_staff:
        if view_mode == 'my':
            # Admin viewing their own reservations
            reservations = Reservation.objects.filter(user=request.user)
            title = "My Reservations"
        else:
            # Admin viewing all reservations
            reservations = Reservation.objects.all()
            title = "All Reservations (Admin View)"
    else:
        # Regular user: only see their own
        reservations = Reservation.objects.filter(user=request.user)
        title = "My Reservations"
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        reservations = reservations.filter(status=status)
    
    context = {
        'reservations': reservations,
        'status': status,
        'view_mode': view_mode,
        'title': title,
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'reservations/reservation_list.html', context)

@login_required
def reservation_create_view(request):
    """
    Create a new reservation with move-in date only.
    Tenant decides when to move out later (typical PH apartment rental).
    """
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            
            # If Admin chooses "Auto-approve"
            if request.user.is_staff and request.POST.get('auto_approve'):
                reservation.status = 'approved'
                reservation.reviewed_by = request.user
                reservation.reviewed_at = timezone.now()
                
                # SAVE FIRST before changing apartment status
                reservation.save()
                
                # Mark apartment as occupied immediately
                apartment = reservation.apartment
                apartment.status = 'occupied'
                apartment.save()
                
                messages.success(request, f'Reservation for Unit {apartment.unit_number} auto-approved!')
            else:
                reservation.status = 'pending'
                
                # SAVE FIRST before creating notifications
                reservation.save()
                
                messages.success(request, 'Move-in request submitted! Waiting for admin review.')
                
                # NOW create notifications after reservation is saved
                admins = User.objects.filter(is_staff=True)
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        notification_type='new_reservation',
                        reservation=reservation,
                        message=f"New reservation request from {request.user.username} for Unit {reservation.apartment.unit_number}"
                    )
            
            return redirect('reservation_list')
    else:
        # Pre-select apartment if ID is passed in URL (from "Book Now" buttons)
        apartment_id = request.GET.get('apartment')
        initial_data = {}
        if apartment_id:
            initial_data['apartment'] = apartment_id
        form = ReservationForm(initial=initial_data)
    
    context = {
        'form': form,
        'action': 'Create',
        'is_admin': request.user.is_staff,
    }
    return render(request, 'reservations/reservation_form.html', context)

@login_required
def reservation_update_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and reservation.user != request.user:
        messages.error(request, 'You can only edit your own reservations.')
        return redirect('reservation_list')
    
    # Regular users can only edit pending
    if reservation.status != 'pending' and not request.user.is_staff:
        messages.error(request, 'You can only edit pending reservations.')
        return redirect('reservation_list')
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reservation updated successfully!')
            return redirect('reservation_list')
    else:
        form = ReservationForm(instance=reservation)
    
    context = {
        'form': form,
        'action': 'Update',
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'reservations/reservation_form.html', context)


@login_required
def reservation_delete_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and reservation.user != request.user:
        messages.error(request, 'You can only cancel your own reservations.')
        return redirect('reservation_list')
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        
        # Create notification for user (if admin cancelled someone else's reservation)
        if request.user.is_staff and reservation.user != request.user:
            Notification.objects.create(
                user=reservation.user,
                notification_type='reservation_cancelled',
                reservation=reservation,
                message=f'Your reservation for {reservation.apartment.name} has been cancelled by admin.'
            )
        
        messages.success(request, 'Reservation cancelled successfully!')
        return redirect('reservation_list')
    
    return render(request, 'reservations/reservation_confirm_delete.html', {'reservation': reservation})


# ============================================
# ADMIN APPROVAL FUNCTIONS
# ============================================

@login_required
def reservation_approve_view(request, pk):
    """Admin approves the move-in request"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    reservation = get_object_or_404(Reservation, pk=pk)
    reservation.status = 'approved'
    reservation.reviewed_by = request.user
    reservation.reviewed_at = timezone.now()
    reservation.save()
    
    # Logic: Once approved, the apartment is no longer available
    apartment = reservation.apartment
    apartment.status = 'occupied'
    apartment.save()
    
    Notification.objects.create(
        user=reservation.user,
        notification_type='reservation_approved',
        reservation=reservation,
        message=f"Your move-in request for Unit {apartment.unit_number} has been approved!"
    )
    
    messages.success(request, f"Reservation approved. Unit {apartment.unit_number} is now Occupied.")
    return redirect('admin_dashboard')
    
@login_required
def reservation_deny_view(request, pk):
    """Admin denies a reservation"""
    if not request.user.is_staff:
        messages.error(request, 'Only admins can deny reservations.')
        return redirect('reservation_list')
    
    reservation = get_object_or_404(Reservation, pk=pk)
    
    if not reservation.can_be_denied():
        messages.error(request, 'This reservation cannot be denied.')
        return redirect('reservation_list')
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        
        if not admin_notes:
            messages.error(request, 'Please provide a reason for denial.')
            return render(request, 'reservations/reservation_deny.html', {'reservation': reservation})
        
        reservation.status = 'denied'
        reservation.reviewed_by = request.user
        reservation.reviewed_at = timezone.now()
        reservation.admin_notes = admin_notes
        reservation.save()
        
        # Create notification for user
        Notification.objects.create(
            user=reservation.user,
            notification_type='reservation_denied',
            reservation=reservation,
            message=f'Your reservation for {reservation.apartment.name} has been denied. Reason: {admin_notes}'
        )
        
        messages.success(request, 'Reservation denied and user notified.')
        return redirect('reservation_list')
    
    return render(request, 'reservations/reservation_deny.html', {'reservation': reservation})


@login_required
def notifications_view(request):
    """View all user notifications"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark as read
    if request.GET.get('mark_read'):
        notifications.update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications')
    
    context = {
        'notifications': notifications,
        'unread_notifications_count': notifications.filter(is_read=False).count(),
    }
    
    return render(request, 'reservations/notifications.html', context)


@login_required
def notification_read_view(request, pk):
    """Mark a single notification as read"""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    
    return redirect('notifications')


@login_required
def notification_delete_view(request, pk):
    """Delete a single notification"""
    if request.method == 'POST':
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.delete()
        messages.success(request, 'Notification deleted successfully!')
    return redirect('notifications')


@login_required
def notification_clear_all_view(request):
    """Delete all notifications for current user"""
    if request.method == 'POST':
        deleted_count = Notification.objects.filter(user=request.user).count()
        Notification.objects.filter(user=request.user).delete()
        messages.success(request, f'{deleted_count} notification(s) cleared!')
    return redirect('notifications')


# ============================================
# NEW VIEW: Admin Management Dashboard
# ============================================

@login_required
def admin_dashboard_view(request):
    """Special dashboard for admins with management tools"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('dashboard')
    
    # Pending reservations that need review
    pending_reservations = Reservation.objects.filter(status='pending').order_by('-created_at')
    
    # Statistics
    total_users = User.objects.filter(is_staff=False).count()
    total_reservations = Reservation.objects.count()
    approved_today = Reservation.objects.filter(
        status='approved',
        reviewed_at__date=timezone.now().date()
    ).count()
    
    context = {
        'pending_reservations': pending_reservations,
        'total_users': total_users,
        'total_reservations': total_reservations,
        'approved_today': approved_today,
    }
    
    return render(request, 'reservations/admin_dashboard.html', context)

@login_required
def inbox_view(request):
    """Show all conversations for the current user"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).prefetch_related('messages', 'participants').order_by('-updated_at')
    
    # Prepare conversation data with last message and unread count
    conversation_data = []
    for conv in conversations:
        last_msg = conv.get_last_message()
        other_user = conv.get_other_participant(request.user)
        unread = conv.unread_count_for_user(request.user)
        
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_msg,
            'unread_count': unread,
        })
    
    context = {
        'conversation_data': conversation_data,
        'total_unread': sum(c['unread_count'] for c in conversation_data)
    }
    return render(request, 'reservations/inbox.html', context)

@login_required
def message_detail_view(request, pk):
    """View a conversation thread and send replies"""
    conversation = get_object_or_404(Conversation, pk=pk, participants=request.user)
    
    # Mark all messages in this conversation as read for current user
    conversation.messages.exclude(sender=request.user).update(is_read=True)
    
    # Get other participant
    other_user = conversation.get_other_participant(request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Create new message in this conversation
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()
            
            # Create notification
            Notification.objects.create(
                user=other_user,
                notification_type='new_message',
                message=f"New message from {request.user.username}"
            )
            
            messages.success(request, f"Message sent to {other_user.username}!")
            return redirect('message_detail', pk=pk)
    
    # Get all messages in chronological order
    message_list = conversation.messages.all()
    
    return render(request, 'reservations/message_detail.html', {
        'conversation': conversation,
        'messages': message_list,
        'other_user': other_user
    })

@login_required
def send_message_view(request):
    """Start a new conversation"""
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject', 'General Inquiry')
        content = request.POST.get('content')
        recipient = get_object_or_404(User, id=recipient_id)
        
        # Check if conversation already exists between these users
        existing_conv = Conversation.objects.filter(
            participants=request.user
        ).filter(
            participants=recipient
        ).first()
        
        if existing_conv:
            # Add message to existing conversation
            Message.objects.create(
                conversation=existing_conv,
                sender=request.user,
                content=content
            )
            existing_conv.updated_at = timezone.now()
            existing_conv.save()
            conversation = existing_conv
        else:
            # Create new conversation
            conversation = Conversation.objects.create(subject=subject)
            conversation.participants.add(request.user, recipient)
            
            # Create first message
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
        
        # Create notification
        Notification.objects.create(
            user=recipient,
            notification_type='new_message',
            message=f"New message from {request.user.username}"
        )
        
        messages.success(request, 'Message sent successfully!')
        return redirect('message_detail', pk=conversation.pk)
    
    # Get available recipients
    users = User.objects.all() if request.user.is_staff else User.objects.filter(is_staff=True)
    
    return render(request, 'reservations/send_message.html', {'users': users})

@login_required
def my_apartment_view(request):
    """Display current tenant's apartment details and payment info"""
    from datetime import date
    
    # Get user's active approved reservation
    active_reservation = Reservation.objects.filter(
        user=request.user,
        status='approved'
    ).first()
    
    if not active_reservation:
        # User doesn't have an active apartment
        context = {
            'has_apartment': False,
            'pending_reservations': Reservation.objects.filter(
                user=request.user,
                status='pending'
            )
        }
        return render(request, 'reservations/my_apartment.html', context)
    
    # User has active apartment
    apartment = active_reservation.apartment
    
    # Calculate stay duration
    stay_duration = (date.today() - active_reservation.check_in).days
    months_stayed = stay_duration // 30
    
    # Calculate days until payment (for display purposes)
    days_until_payment = None
    is_overdue = False
    days_overdue = 0
    
    if hasattr(active_reservation, 'next_payment_due') and active_reservation.next_payment_due:
        delta = active_reservation.next_payment_due - date.today()
        days_until_payment = delta.days
        
        if days_until_payment < 0:
            is_overdue = True
            days_overdue = abs(days_until_payment)
    
    context = {
        'has_apartment': True,
        'reservation': active_reservation,
        'apartment': apartment,
        'stay_duration_days': stay_duration,
        'months_stayed': months_stayed,
        'days_until_payment': days_until_payment,
        'is_overdue': is_overdue,
        'days_overdue': days_overdue,  # Add this for template
    }
    
    return render(request, 'reservations/my_apartment.html', context)