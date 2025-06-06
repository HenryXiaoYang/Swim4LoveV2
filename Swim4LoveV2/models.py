from django.db import models
import uuid


class Swimmer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_id = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=100)
    house = models.CharField(max_length=6, choices=[("Spring", "Spring"), ("Summer", "Summer"), ("Autumn", "Autumn"),
                                                    ("Winter", "Winter")], default="Spring")
    lap_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.student_id or '无学号'})"

    @staticmethod
    def exist_student_id(student_id):
        if not student_id:
            return False
        return Swimmer.objects.filter(student_id=student_id).exists()


class Volunteer(models.Model):
    student_id = models.CharField(max_length=10, help_text="Please enter your student ID.", primary_key=True)
    name = models.CharField(max_length=100, help_text="Please enter your name.", unique=True)
    favorites = models.ManyToManyField(Swimmer, related_name='favorited_by', blank=True)

    def __str__(self):
        return self.name

    @staticmethod
    def exist_student_id(student_id):
        return Volunteer.objects.filter(student_id=student_id).exists()
