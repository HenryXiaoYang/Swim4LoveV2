from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils.html import escape
from django.conf import settings
from django.db.models import Q

from .forms import AddSwimmerForm
from .models import Swimmer

def check_passkey(request):
    """Check if the user has entered the correct passkey"""
    return request.session.get('passkey_authenticated', False)

def passkey_required(view_func):
    """Decorator to require passkey authentication"""
    def wrapper(request, *args, **kwargs):
        if not check_passkey(request):
            return HttpResponseRedirect(reverse('passkey_login'))
        return view_func(request, *args, **kwargs)
    return wrapper

def passkey_login(request):
    """Handle passkey authentication"""
    if request.method == "POST":
        entered_passkey = request.POST.get('passkey', '')
        if entered_passkey == settings.PASSKEY:
            request.session['passkey_authenticated'] = True
            return HttpResponseRedirect(reverse('home'))
        else:
            return render(request, "passkey_login.html", {"error": "Incorrect passkey"})
    
    return render(request, "passkey_login.html")

def passkey_logout(request):
    """Logout by removing passkey authentication"""
    request.session.pop('passkey_authenticated', None)
    return HttpResponseRedirect(reverse('home'))

def index(request):
    leaderboard = request.GET.get('leaderboard', 'false') == 'true'
    search_query = request.GET.get('search', '').strip()

    num_swimmers = Swimmer.objects.all().count()

    # Get all swimmers and sort them
    swimmers = Swimmer.objects.all()
    
    # Apply search filter if search query exists
    if search_query:
        swimmers = swimmers.filter(
            Q(name__icontains=search_query) |
            Q(student_id__icontains=search_query) |
            Q(house__icontains=search_query)
        )
    
    if leaderboard:
        swimmers = swimmers.order_by('-lap_count')
    else:
        swimmers = swimmers.order_by('name')

    spring_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Spring"])
    summer_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Summer"])
    autumn_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Autumn"])
    winter_laps = sum([swimmer.lap_count for swimmer in swimmers if swimmer.house == "Winter"])
    total_laps = spring_laps + summer_laps + autumn_laps + winter_laps

    amount_raised = total_laps * 5  # Each lap raise 5 rmb

    have_perm = check_passkey(request)

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
        "swimmers": swimmers,
        "have_perm": have_perm,
        "leaderboard": leaderboard,
        "house_data": house_data,
        "spring_laps": spring_laps,
        "summer_laps": summer_laps,
        "autumn_laps": autumn_laps,
        "winter_laps": winter_laps,
        "passkey_authenticated": check_passkey(request),
        "search_query": search_query,
    }

    return render(request, "index.html", context=context)


@passkey_required
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


@passkey_required
def delete_swimmer(request, pk):
    if request.method == "POST":
        Swimmer.objects.filter(id=pk).delete()
    return HttpResponseRedirect(reverse('home'))


@passkey_required
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


@passkey_required
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


@passkey_required
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
