from django.contrib import admin
from django.urls import path, include
from accounts.views import LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(), name='login'),
    path('accounts/', include('accounts.urls')),
    path('accounts/profile/', include('bookreviews.urls')),

]
