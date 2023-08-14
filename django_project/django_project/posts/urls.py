from django.urls import path

from .views import HomePageView,CreatePostView
from . import views


urlpatterns = [
    path("home/", HomePageView.as_view(), name="home"),
    path("", CreatePostView.as_view(), name="add_post"),
    path("result/<int:pk>/", views.result,name="r"),
    path('result/<int:pk>/delete/', views.delete_item, name='delete_item'),
    # path("result/<int:pk>/delete/",views.DeletePostView.as_view(),name='del')
    #path('',views.index)
]