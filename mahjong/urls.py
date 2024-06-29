from django.urls import path
from . import views

urlpatterns = [
    path('', views.QuestionView.as_view(), name='question'),
    path('analyze-hand/', views.analyze_hand, name='analyze-hand'),
]