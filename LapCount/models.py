from django.db import models

class Swimmer(models.Model):
    student_id = models.CharField( max_length=5 ,primary_key=True)
    name = models.CharField(max_length=100)
    house = models.CharField(max_length=6,choices=[("Spring", "Spring"), ("Summer", "Summer"), ("Autumn", "Autumn"), ("Winter", "Winter")], default="Spring")
    lap_count = models.IntegerField(default=0)
    minutes = models.IntegerField(default=0)
    seconds = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def exist_student_id(student_id):
        return Swimmer.objects.filter(student_id=student_id).exists()


class Volunteer(models.Model):
    student_id = models.CharField(max_length=10, help_text="Please enter your student ID.",primary_key=True)
    name = models.CharField(max_length=100, help_text="Please enter your name.",unique=True)

    def __str__(self):
        return self.name

    def exist_student_id(student_id):
        return Volunteer.objects.filter(student_id=student_id).exists()