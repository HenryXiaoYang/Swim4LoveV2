from django.urls import path

from Swim4LoveV2 import views

urlpatterns = [
    path("", views.index, name="home"),
    path("index/", views.index, name="index"),
    path("passkey_login/", views.passkey_login, name="passkey_login"),
    path("passkey_logout/", views.passkey_logout, name="passkey_logout"),
    path("add_swimmer/", views.add_swimmer, name="add_swimmer"),
    path("delete_swimmer/<uuid:pk>/", views.delete_swimmer, name="delete_swimmer"),
    path("edit_swimmer/<uuid:pk>/", views.edit_swimmer, name="edit_swimmer"),
    path("increment_laps/<uuid:pk>/", views.increment_laps, name="increment_laps"),
    path("decrement_laps/<uuid:pk>/", views.decrement_laps, name="decrement_laps"),
]
