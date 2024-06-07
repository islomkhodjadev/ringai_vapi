from django.urls import path
from .views import RegisterLoginView, Login, CustomerView, Call, RetrieveToken


urlpatterns = [
    path("register/", RegisterLoginView.as_view()),
    path("login/", Login.as_view()),
    path("newToken/", RetrieveToken.as_view()),
    path("customer/", CustomerView.as_view()),
    path("customer/<int:pk>/", CustomerView.as_view()),
    path("call/<int:customer_id>/", Call.as_view())
]

