from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Admin Dashboard
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    
    # Apartments
    path('apartments/', views.apartment_list_view, name='apartment_list'),
    path('apartments/<int:pk>/', views.apartment_detail_view, name='apartment_detail'),
    path('apartments/create/', views.apartment_create_view, name='apartment_create'),
    path('apartments/<int:pk>/update/', views.apartment_update_view, name='apartment_update'),
    path('apartments/<int:pk>/delete/', views.apartment_delete_view, name='apartment_delete'),
    
    # Reservations
    path('reservations/', views.reservation_list_view, name='reservation_list'),
    path('reservations/create/', views.reservation_create_view, name='reservation_create'),
    path('reservations/<int:pk>/update/', views.reservation_update_view, name='reservation_update'),
    path('reservations/<int:pk>/delete/', views.reservation_delete_view, name='reservation_delete'),
    
    # Admin approval system
    path('reservations/<int:pk>/approve/', views.reservation_approve_view, name='reservation_approve'),
    path('reservations/<int:pk>/deny/', views.reservation_deny_view, name='reservation_deny'),
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.notification_read_view, name='notification_read'),
    path('notifications/<int:pk>/delete/', views.notification_delete_view, name='notification_delete'),
    path('notifications/clear-all/', views.notification_clear_all_view, name='notification_clear_all'),  # NEW

    path('inbox/', views.inbox_view, name='inbox'),
    path('messages/send/', views.send_message_view, name='send_message'),
    path('messages/<int:pk>/', views.message_detail_view, name='message_detail'),
    path('my-apartment/', views.my_apartment_view, name='my_apartment'),
]