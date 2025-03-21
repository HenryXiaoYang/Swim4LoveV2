from django.contrib.auth import logout
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import escape

from .forms import AddSwimmerForm, AddVolunteerForm
from .models import Swimmer, Volunteer


def index(request):
    leaderboard = request.GET.get('leaderboard', 'false') == 'true'

    num_swimmers = Swimmer.objects.all().count()
    num_volunteers = Volunteer.objects.all().count()

    # Get the current user's volunteer profile if logged in
    current_volunteer = None
    if request.user.is_authenticated:
        try:
            current_volunteer = Volunteer.objects.get(name=request.user.username)
        except Volunteer.DoesNotExist:
            # 如果是管理员/超级用户，尝试自动创建志愿者记录（仅供显示用，不保存）
            if request.user.is_staff or request.user.is_superuser:
                # 只检查是否存在对应的志愿者记录，如果不存在，首次加载时不显示收藏状态
                # 用户点击收藏按钮后，toggle_favorite会创建记录并添加收藏
                pass

    # Get all swimmers and sort them
    swimmers = Swimmer.objects.all()
    if leaderboard:
        swimmers = swimmers.order_by('-lap_count')
    elif current_volunteer:
        # Sort by favorites first, then by name
        swimmers = sorted(swimmers, key=lambda s: (not current_volunteer.favorites.filter(id=s.id).exists(), s.name))
    else:
        swimmers = swimmers.order_by('name')

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
        "spring_laps": spring_laps,
        "summer_laps": summer_laps,
        "autumn_laps": autumn_laps,
        "winter_laps": winter_laps,
        "current_volunteer": current_volunteer,
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


@permission_required("Swim4LoveV2.add_swimmer")
def toggle_favorite(request, pk):
    if request.method == "POST":
        swimmer = get_object_or_404(Swimmer, id=pk)

        # 检查用户是否有对应志愿者记录，如果没有且用户是管理员，则创建一个
        volunteer = None
        try:
            volunteer = Volunteer.objects.get(name=request.user.username)
        except Volunteer.DoesNotExist:
            # 如果是管理员/超级用户，自动创建志愿者记录
            if request.user.is_staff or request.user.is_superuser:
                # 创建临时学号
                temp_student_id = f"admin_{request.user.id}"
                volunteer = Volunteer.objects.create(
                    student_id=temp_student_id,
                    name=request.user.username
                )
            else:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': '找不到对应的志愿者记录'
                    }, status=400)
                return HttpResponseRedirect(reverse('home'))

        # 处理收藏逻辑
        was_favorited = swimmer in volunteer.favorites.all()

        if was_favorited:
            volunteer.favorites.remove(swimmer)
        else:
            volunteer.favorites.add(swimmer)

        # 确保变更被保存
        volunteer.save()

        # 再次检查收藏状态，确保变更已保存
        current_favorites = volunteer.favorites.all()
        is_favorite_after_save = swimmer in current_favorites

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 返回更详细的状态信息，并使用保存后的实际状态
            response_data = {
                'success': True,
                'is_favorite': is_favorite_after_save,  # 使用实际保存后的状态，而不是预期状态
                'swimmer_id': str(swimmer.id),
                'swimmer_name': swimmer.name,
                'favorites_count': volunteer.favorites.count()
            }
            return JsonResponse(response_data)

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
        add_volunteer_permission = Permission.objects.get(codename="add_volunteer",
                                                          content_type__app_label="Swim4LoveV2")
        user.user_permissions.add(add_swimmer_permission, add_volunteer_permission)

        return HttpResponseRedirect(reverse('home'))

    else:
        form = AddVolunteerForm()

    return render(request, "add_volunteer.html", context={"form": form})


@permission_required("Swim4LoveV2.add_volunteer")
def delete_volunteer(request, pk):
    pk = escape(pk)
    if request.method == "POST":
        username = Volunteer.objects.filter(student_id=pk).values('name').first()['name']

        User.objects.filter(username=username).delete()
        Volunteer.objects.filter(student_id=pk).delete()

    return HttpResponseRedirect(reverse('home'))


# 登出功能
def logout_view(request):
    # 无论是GET还是POST请求都允许登出
    logout(request)
    return render(request, "registration/logged_out.html")
