from django.urls import path
from .views import UserListView

app_name = 'management' 

urlpatterns = [
    path('users/', UserListView.as_view(), name='user_list'),
]

