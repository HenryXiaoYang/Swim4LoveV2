from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import escape

from .forms import AddSwimmerForm, AddVolunteerForm
from .models import Swimmer, Volunteer


def index(request):
    leaderboard = request.GET.get('leaderboard', 'false') == 'true'

    num_swimmers = Swimmer.objects.all().count()
    num_volunteers = Volunteer.objects.all().count()

    swimmers = Swimmer.objects.all().order_by('-lap_count') if leaderboard else Swimmer.objects.all()
    volunteers = Volunteer.objects.all()

    spring_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Spring"])
    summer_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Summer"])
    autumn_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Autumn"])
    winter_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Winter"])
    total_laps = spring_laps + summer_laps + autumn_laps + winter_laps

    have_perm = request.user.has_perm("LapCount.add_swimmer") and request.user.has_perm("LapCount.add_volunteer")

    return render(
        request,
        "index.html",
        context={"num_swimmers": num_swimmers, "total_laps": total_laps, "spring_laps": spring_laps,
                 "summer_laps": summer_laps, "autumn_laps": autumn_laps, "winter_laps": winter_laps,
                 "num_volunteers": num_volunteers,
                 "swimmers": swimmers, "volunteers": volunteers, "have_perm": have_perm, "leaderboard": leaderboard}, )


# need to be volunteer
@permission_required("LapCount.add_swimmer")
def add_swimmer(request):
    if request.method == "POST":
        form = AddSwimmerForm(request.POST)

        if not form.is_valid():
            return render(request, "add_swimmer.html", context={"form": form})

        if Swimmer.exist_student_id(student_id=form.cleaned_data["student_id"]):
            form.add_error(None, "Student ID already exists")
            return render(request, "add_swimmer.html", context={"form": form})

        if not form.clean_swim_valid():
            return render(request, "add_swimmer.html", context={"form": form})

        Swimmer.objects.create(
            name=form.cleaned_data["name"],
            student_id=form.cleaned_data["student_id"],
            house=form.cleaned_data["house"],
            lap_count=form.cleaned_data["lap_count"],
            minutes=form.cleaned_data["minutes"],
            seconds=form.cleaned_data["seconds"],
        )
        # return to the index page
        return HttpResponseRedirect(reverse('index'))

    else:
        form = AddSwimmerForm()

    return render(request, "add_swimmer.html", context={"form": form})


@permission_required("LapCount.add_swimmer")
def delete_swimmer(request, pk):
    pk = escape(pk)
    if request.method == "POST":
        Swimmer.objects.filter(student_id=pk).delete()
    return HttpResponseRedirect(reverse('index'))


@permission_required("LapCount.add_volunteer")
def edit_swimmer(request, pk):
    pk = escape(pk)

    swimmer = Swimmer.objects.get(student_id=pk)

    if request.method == "POST":
        form = AddSwimmerForm(request.POST)

        if not form.is_valid():
            return render(request, "edit_swimmer.html", context={"form": form})

        if not form.clean_swim_valid():
            return render(request, "edit_swimmer.html", context={"form": form})

        # change the database data
        swimmer.name = form.cleaned_data["name"]
        swimmer.student_id = form.cleaned_data["student_id"]
        swimmer.house = form.cleaned_data["house"]
        swimmer.lap_count = form.cleaned_data["lap_count"]
        swimmer.minutes = form.cleaned_data["minutes"]
        swimmer.seconds = form.cleaned_data["seconds"]
        swimmer.save()

        return HttpResponseRedirect(reverse('index'))


    else:
        form = AddSwimmerForm(initial={"name": swimmer.name, "student_id": swimmer.student_id, "house": swimmer.house,
                                       "lap_count": swimmer.lap_count, "minutes": swimmer.minutes,
                                       "seconds": swimmer.seconds})
        return render(request, "edit_swimmer.html", context={"form": form, "student_id": pk})


@permission_required("LapCount.add_volunteer")
def add_volunteer(request):
    if request.method == "POST":
        form = AddVolunteerForm(request.POST)

        if not form.is_valid():
            return render(request, "add_volunteer.html", context={"form": form})

        if not form.check_password():
            return render(request, "add_volunteer.html", context={"form": form})

        if Volunteer.exist_student_id(student_id=form.cleaned_data["student_id"]):
            form.add_error(None, "Student ID already exists")
            return render(request, "add_volunteer.html", context={"form": form})

        if User.objects.filter(username=form.cleaned_data["name"]).exists():
            form.add_error(None, "Username already exists")
            return render(request, "add_volunteer.html", context={"form": form})

        Volunteer.objects.create(
            student_id=form.cleaned_data["student_id"],
            name=form.cleaned_data["name"],
        )

        # create user
        user = User.objects.create_user(username=form.cleaned_data["name"], password=form.cleaned_data["password"])

        # add LapCount.add_swimmer and LapCount.add_volunteer permission
        add_swimmer_permission = Permission.objects.get(codename="add_swimmer")
        add_volunteer_permission = Permission.objects.get(codename="add_volunteer")
        user.user_permissions.add(add_swimmer_permission, add_volunteer_permission)

        return HttpResponseRedirect(reverse('index'))

    else:
        form = AddVolunteerForm()

    return render(request, "add_volunteer.html", context={"form": form})


@permission_required("LapCount.add_volunteer")
def delete_volunteer(request, pk):
    print(1)
    pk = escape(pk)
    if request.method == "POST":
        username = Volunteer.objects.filter(student_id=pk).values('name').first()['name']

        User.objects.filter(username=username).delete()
        Volunteer.objects.filter(student_id=pk).delete()
        print(2)

    return HttpResponseRedirect(reverse('index'))
