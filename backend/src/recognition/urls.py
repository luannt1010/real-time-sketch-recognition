from django.urls import path
from . import views

urlpatterns = [
    path('recognize/', views.recognize_drawing, name='recognize_drawing'),
    path('feedback/', views.save_feedback, name='save_feedback'),
]


