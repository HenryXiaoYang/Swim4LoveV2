import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from LapCount.models import Volunteer


def ValidateStudentID(value):
    if len(str(value)) != 5 and not str(value).isdigit():
        raise ValidationError("Please enter a valid student ID")


def ValidateUsername(value):
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError("Username can only contain alphanumeric characters and _, @, +, ., -")


class AddSwimmerForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Ethan Zhao", "class": "form-field"}),
                           max_length=100)
    student_id = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "12345", "class": "form-field"}),
                                 validators=[ValidateStudentID],
                                 error_messages={"required": "Please enter a valid student ID"})
    house = forms.ChoiceField(
        choices=[("Spring", "Spring"), ("Summer", "Summer"), ("Autumn", "Autumn"), ("Winter", "Winter")],
        widget=forms.Select(attrs={"class": "form-field"}))
    lap_count = forms.IntegerField(initial=0, widget=forms.NumberInput(attrs={"class": "form-field"}),
                                   validators=[MinValueValidator(1), MaxValueValidator(150)])
    minutes = forms.IntegerField(initial=0, widget=forms.NumberInput(attrs={"class": "form-field"}),
                                 validators=[MinValueValidator(0), MaxValueValidator(180)])
    seconds = forms.IntegerField(initial=0, widget=forms.NumberInput(attrs={"class": "form-field"}),
                                 validators=[MinValueValidator(0), MaxValueValidator(59)])

    def clean_swim_valid(self):
        minutes = self.cleaned_data["minutes"]
        seconds = self.cleaned_data["seconds"]
        lap_count = self.cleaned_data["lap_count"]

        # minos speed: 30s/50m
        total_second = seconds + 60 * minutes
        if not total_second or total_second / lap_count < 30:
            self.add_error(None, "How can you swim faster than Minos??")
            return False

        return True


class AddVolunteerForm(forms.Form):
    student_id = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "12345", "class": "form-field"}),
                                 validators=[ValidateStudentID],
                                 error_messages={"required": "Please enter a valid student ID"})
    name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "EthanZhao", "class": "form-field"}),
                           max_length=100, validators=[ValidateUsername], label="Username")
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-field"}))
    re_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-field"}), label="Re-enter Password")

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"]
        if Volunteer.exist_student_id(student_id):
            raise ValidationError("Student ID already exists")
        return student_id

    def check_password(self):
        password = self.cleaned_data["password"]
        re_password = self.cleaned_data["re_password"]
        if password != re_password:
            self.add_error(None, "Password does not match")
            return False
        elif re_password == "":
            self.add_error(None, "Please enter a password")
            return False
        elif len(re_password) < 5:
            self.add_error(None, "Password must be at least 5 characters")
            return False
        return True
