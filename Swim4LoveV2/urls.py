from django.urls import path

from Swim4LoveV2 import views

urlpatterns = [
    path("", views.index, name="home"),
    path("index/", views.index, name="index"),
    path("add_swimmer/", views.add_swimmer, name="add_swimmer"),
    path("add_volunteer/", views.add_volunteer, name="add_volunteer"),
    path("delete_swimmer/<uuid:pk>/", views.delete_swimmer, name="delete_swimmer"),
    path("edit_swimmer/<uuid:pk>/", views.edit_swimmer, name="edit_swimmer"),
    path("delete_volunteer/<str:pk>/", views.delete_volunteer, name="delete_volunteer"),
    path("logout/", views.logout_view, name="logout"),
    path("increment_laps/<uuid:pk>/", views.increment_laps, name="increment_laps"),
    path("decrement_laps/<uuid:pk>/", views.decrement_laps, name="decrement_laps"),
    path("toggle_favorite/<uuid:pk>/", views.toggle_favorite, name="toggle_favorite"),
]
