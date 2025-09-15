from django.urls import path
from . import views

urlpatterns = [
    path('', views.text_entry_view, name='text_entry'),
    path('success/', views.text_entry_success_view, name='text_entry_success'),
    path('delete/<int:entry_id>/', views.delete_text_entry_view, name='delete_text_entry'),
]
