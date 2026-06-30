from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.auth_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    path('user/<str:username>/', views.UserDetailView.as_view(), name='user_detail'),
    path('user/<str:username>/edit_inline/', views.UserEditInlineView.as_view(), name='user_edit_inline'),
    path('user/delete', views.UserDeleteView.as_view(), name='user_delete'),
    path('admin/user/<str:username>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
]
