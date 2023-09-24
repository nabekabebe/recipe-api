"""
User enpoint urls
"""

from django.urls import path
from user.views import UserCreateView, AuthTokenView

app_name = 'user'

urlpatterns = [
    path('create/', UserCreateView.as_view(), name='create'),
    path('token/', AuthTokenView.as_view(), name='token')
]
