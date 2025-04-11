# management/urls.py
from django.urls import path
from .views import UserListView, UserCreateView, UserUpdateView, UserDeleteView

app_name = 'management'

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/add/', UserCreateView.as_view(), name='user_add'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_update'),
    path('users/<int:pk>/delete/', UserDeleteView.as_view(), name='user_delete'),
]