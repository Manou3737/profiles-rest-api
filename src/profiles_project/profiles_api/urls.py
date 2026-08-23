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
router.register(
    'logout',
    views.LogoutViewSet,
    basename='logout'
)
router.register(
    'password-change',
    views.PasswordChangeViewSet,
    basename='password-change'
)

router.register(
    'password-reset',
    views.PasswordResetRequestViewSet,
    basename='password-reset'
)

router.register(
    'password-reset-confirm',
    views.PasswordResetConfirmViewSet,
    basename='password-reset-confirm'
)

router.register(
    'register',
    views.RegisterViewSet,
    basename='register'
)

router.register(
    'verify-email',
    views.EmailVerificationViewSet,
    basename='verify-email'
)

router.register('feed', views.UserProfileFeedViewset)

urlpatterns = [
    path('hello-view/', views.HelloApiView.as_view()),
    path('', include(router.urls)),
]
