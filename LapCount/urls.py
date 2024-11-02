from django.urls import path

from LapCount import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add_swimmer/", views.add_swimmer, name="add_swimmer"),
    path("add_volunteer/", views.add_volunteer, name="add_volunteer"),
    path("delete_swimmer/<str:pk>/", views.delete_swimmer, name="delete_swimmer"),
    path("edit_swimmer/<str:pk>/", views.edit_swimmer, name="edit_swimmer"),
    path("delete_volunteer/<str:pk>/", views.delete_volunteer, name="delete_volunteer"),
]
