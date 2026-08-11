from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(
    'hello-viewset',
    views.HelloViewSet,
    basename='hello-viewset'
)
router.register('profile', views.UserProfileViewset)
router.register(
    'login',
    views.LoginViewSet,
    basename='login'
)
router.register('feed', views.UserProfileFeedViewset)

urlpatterns = [
    path('hello-view/', views.HelloApiView.as_view()),
    path('', include(router.urls)),
]
