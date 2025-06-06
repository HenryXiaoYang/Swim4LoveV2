import re

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from Swim4LoveV2.models import Swimmer


def ValidateUsername(value):
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError("The username can contain only letters, numbers, and _, @, +, ., -")


class AddSwimmerForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.instance_id = kwargs.pop('instance_id', None)
        super().__init__(*args, **kwargs)

    name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Name", "class": "form-field"}),
        max_length=100
    )
    student_id = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Student ID（Optional）", "class": "form-field"}),
        required=False,
        help_text="If there is no student ID, you can leave it blank"
    )
    house = forms.ChoiceField(
        choices=[("Spring", "Spring"), ("Summer", "Summer"), ("Autumn", "Autumn"), ("Winter", "Winter")],
        widget=forms.Select(attrs={"class": "form-field"})
    )
    lap_count = forms.IntegerField(
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-field"}),
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )

    def clean_student_id(self):
        student_id = self.cleaned_data.get("student_id")
        if student_id:
            # 检查是否存在相同学号的其他学生（排除当前正在编辑的学生）
            existing_swimmer = Swimmer.objects.filter(student_id=student_id).exclude(id=self.instance_id).first()
            if existing_swimmer:
                raise ValidationError("Student ID already exists!")
        return student_id

    def clean_swim_valid(self):
        return True
