from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import escape
from django.contrib.auth import logout

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

    amount_raised = total_laps * 5  # Each lap raise 5 rmb

    have_perm = request.user.has_perm("Swim4LoveV2.add_swimmer") and request.user.has_perm("Swim4LoveV2.add_volunteer")

    # 创建学院数据字典，用于排序（如果启用排行榜）
    house_data = [
        {"name": "Spring", "laps": spring_laps, "css_class": "spring"},
        {"name": "Summer", "laps": summer_laps, "css_class": "summer"},
        {"name": "Autumn", "laps": autumn_laps, "css_class": "autumn"},
        {"name": "Winter", "laps": winter_laps, "css_class": "winter"}
    ]
    
    # 如果启用排行榜，对学院数据排序
    if leaderboard:
        house_data.sort(key=lambda x: x["laps"], reverse=True)
    
    # 将学院数据添加到上下文
    context = {
        "num_swimmers": num_swimmers, 
        "total_laps": total_laps, 
        "amount_raised": amount_raised, 
        "num_volunteers": num_volunteers, 
        "swimmers": swimmers,
        "volunteers": volunteers, 
        "have_perm": have_perm, 
        "leaderboard": leaderboard,
        "house_data": house_data,
        # 保持原有的数据以兼容现有模板
        "spring_laps": spring_laps, 
        "summer_laps": summer_laps, 
        "autumn_laps": autumn_laps, 
        "winter_laps": winter_laps,
    }

    return render(request, "index.html", context=context)


# need to be volunteer
@permission_required("Swim4LoveV2.add_swimmer")
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
        )
        # return to the index page
        return HttpResponseRedirect(reverse('home'))

    else:
        form = AddSwimmerForm()

    return render(request, "add_swimmer.html", context={"form": form})


@permission_required("Swim4LoveV2.add_swimmer")
def delete_swimmer(request, pk):
    if request.method == "POST":
        Swimmer.objects.filter(id=pk).delete()
    return HttpResponseRedirect(reverse('home'))


@permission_required("Swim4LoveV2.add_swimmer")
def edit_swimmer(request, pk):
    swimmer = Swimmer.objects.get(id=pk)

    if request.method == "POST":
        form = AddSwimmerForm(request.POST, instance_id=pk)

        if not form.is_valid():
            return render(request, "edit_swimmer.html", context={"form": form, "id": pk})

        if not form.clean_swim_valid():
            return render(request, "edit_swimmer.html", context={"form": form, "id": pk})

        # change the database data
        swimmer.name = form.cleaned_data["name"]
        swimmer.student_id = form.cleaned_data["student_id"]
        swimmer.house = form.cleaned_data["house"]
        swimmer.lap_count = form.cleaned_data["lap_count"]
        swimmer.save()

        return HttpResponseRedirect(reverse('home'))

    else:
        form = AddSwimmerForm(
            initial={
                "name": swimmer.name,
                "student_id": swimmer.student_id,
                "house": swimmer.house,
                "lap_count": swimmer.lap_count,
            },
            instance_id=pk
        )
        return render(request, "edit_swimmer.html", context={"form": form, "id": pk})


@permission_required("Swim4LoveV2.add_swimmer")
def increment_laps(request, pk):
    if request.method == "POST":
        swimmer = Swimmer.objects.get(id=pk)
        swimmer.lap_count += 1
        swimmer.save()
        
        # 如果是AJAX请求，返回更多信息
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 重新计算总圈数
            all_swimmers = Swimmer.objects.all()
            spring_laps = sum([s.lap_count for s in all_swimmers if s.house == "Spring"])
            summer_laps = sum([s.lap_count for s in all_swimmers if s.house == "Summer"])
            autumn_laps = sum([s.lap_count for s in all_swimmers if s.house == "Autumn"])
            winter_laps = sum([s.lap_count for s in all_swimmers if s.house == "Winter"])
            total_laps = spring_laps + summer_laps + autumn_laps + winter_laps
            
            return JsonResponse({
                'success': True, 
                'lap_count': swimmer.lap_count,
                'house': swimmer.house,
                'spring_laps': spring_laps,
                'summer_laps': summer_laps,
                'autumn_laps': autumn_laps,
                'winter_laps': winter_laps,
                'total_laps': total_laps,
                'amount_raised': total_laps * 5
            })
        # 否则重定向到主页
        return HttpResponseRedirect(reverse('home'))


@permission_required("Swim4LoveV2.add_swimmer")
def decrement_laps(request, pk):
    if request.method == "POST":
        swimmer = Swimmer.objects.get(id=pk)
        if swimmer.lap_count > 0:
            swimmer.lap_count -= 1
            swimmer.save()
            
        # 如果是AJAX请求，返回更多信息
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 重新计算总圈数
            all_swimmers = Swimmer.objects.all()
            spring_laps = sum([s.lap_count for s in all_swimmers if s.house == "Spring"])
            summer_laps = sum([s.lap_count for s in all_swimmers if s.house == "Summer"])
            autumn_laps = sum([s.lap_count for s in all_swimmers if s.house == "Autumn"])
            winter_laps = sum([s.lap_count for s in all_swimmers if s.house == "Winter"])
            total_laps = spring_laps + summer_laps + autumn_laps + winter_laps
            
            return JsonResponse({
                'success': True, 
                'lap_count': swimmer.lap_count,
                'house': swimmer.house,
                'spring_laps': spring_laps,
                'summer_laps': summer_laps,
                'autumn_laps': autumn_laps,
                'winter_laps': winter_laps,
                'total_laps': total_laps,
                'amount_raised': total_laps * 5
            })
        # 否则重定向到主页
        return HttpResponseRedirect(reverse('home'))


@permission_required("Swim4LoveV2.add_volunteer")
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

        # add Swim4LoveV2.add_swimmer and Swim4LoveV2.add_volunteer permission
        add_swimmer_permission = Permission.objects.get(codename="add_swimmer", content_type__app_label="Swim4LoveV2")
        add_volunteer_permission = Permission.objects.get(codename="add_volunteer", content_type__app_label="Swim4LoveV2")
        user.user_permissions.add(add_swimmer_permission, add_volunteer_permission)

        return HttpResponseRedirect(reverse('home'))

    else:
        form = AddVolunteerForm()

    return render(request, "add_volunteer.html", context={"form": form})


@permission_required("Swim4LoveV2.add_volunteer")
def delete_volunteer(request, pk):
    print(1)
    pk = escape(pk)
    if request.method == "POST":
        username = Volunteer.objects.filter(student_id=pk).values('name').first()['name']

        User.objects.filter(username=username).delete()
        Volunteer.objects.filter(student_id=pk).delete()
        print(2)

    return HttpResponseRedirect(reverse('home'))

# 登出功能
def logout_view(request):
    # 无论是GET还是POST请求都允许登出
    logout(request)
    return render(request, "registration/logged_out.html")
