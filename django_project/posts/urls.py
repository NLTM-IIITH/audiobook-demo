from django.urls import path

from .views import HomePageView,CreatePostView
from . import views


urlpatterns = [
    path("/home", HomePageView.as_view(), name="home"),
    path("", CreatePostView.as_view(), name="add_post"),
    path("result/<int:pk>/", views.result,name="r"),
    #path('',views.index)
]