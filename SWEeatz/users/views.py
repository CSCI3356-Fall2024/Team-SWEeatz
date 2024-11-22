from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .forms import StudentForm, RewardForm
from .models import Student, Campaign, Reward, RewardExchange, Action, CompletedAction, Reward
from django.shortcuts import get_object_or_404
from django.utils import timezone 
from django.utils.timezone import now
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
import json
from django.views.decorators.csrf import csrf_exempt
from .models import Campaign, Student
from datetime import date
from django.contrib import messages

def home(request):
    return render(request, "home.html")

def landing(request):
    today = date.today()

    #campaigns = Campaign.objects.all()
    campaigns = Campaign.objects.filter(start_date__lte=today, end_date__gte=today)

    top_3_students = Student.objects.order_by('-points_balance')[:3]
    other_top_students = Student.objects.order_by('-points_balance')[3:6]

    current_user = request.user
    try:
        current_student = Student.objects.get(user=current_user)
    except:
        current_student = None
    
    context = {
        'top_3_students':top_3_students,
        'other_top_students':other_top_students,
        'current_student':current_student,
        'user_not_in_top':current_student not in top_3_students and current_student not in other_top_students,
        'campaigns':campaigns,
    }
    return render(request, 'landing.html', context)
    #return render(request, "landing.html", {'campaigns':campaigns})

def logout_view(request):
    logout(request)
    return redirect("/")

def student_create_view(request):
    user = request.user
    student, created = Student.objects.get_or_create(user=user)  # Create or fetch the student's profile

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)  # Use the existing student instance
        if form.is_valid():
            form.save()  # Save updates
            return redirect('profile')  # Redirect to the profile page (adjust this as necessary)
    else:
        # Pre-populate the form with the user's data
        form = StudentForm(instance=student)

    return render(request, 'student_form.html', {'form': form, 'full_name': user.get_full_name()})

def post_login_redirect(request):
    user = request.user

    # Check if the user already has a Student profile
    try:
        student = Student.objects.get(user=user)
        # If the user has a profile, redirect them to the list page
        return redirect('profile')  # or whatever URL name you have for the list page
    except Student.DoesNotExist:
        # If no profile exists, redirect them to the profile creation page
        return redirect('student_create')

def student_list_view(request):
    user = request.user
    student = get_object_or_404(Student, user=user)  # Fetch only the logged-in user's profile
    if user.is_superuser:
        role = "Admin"
    else:
        role = "Student"
    return render(request, 'student_list.html', {'student': student, 'full_name': user.get_full_name(), 'role':role})

# Custom function to check if user is an admin
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin, login_url='home')  # Redirects non-admins to home

def create_campaign(request):
    today = date.today()
    if request.method == 'POST':
        # Handle the form submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        image = request.FILES.get('image')
        points = request.POST.get('points', 0)

        if title and description and start_date and end_date:
            Campaign.objects.create(
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                image=image,
                points=points
            )
            return redirect('create_campaign')

    # Get the first 2 campaigns and the total count
    campaigns =Campaign.objects.filter(start_date__lte=today, end_date__gte=today)[:2]
    total_campaigns =Campaign.objects.filter(start_date__lte=today, end_date__gte=today).count()
    return render(request, 'campaign_create.html', {'campaigns': campaigns, 'total_campaigns': total_campaigns})

def load_more_campaigns(request):
    today = date.today()
    offset = int(request.GET.get('offset', 2))

    # Filter for active campaigns only
    campaigns = Campaign.objects.filter(start_date__lte=today, end_date__gte=today)[offset:]
    campaign_data = [
        {
            "id": campaign.id,
            "title": campaign.title,
            "description": campaign.description,
            "points": campaign.points,
            "start_date": campaign.start_date.strftime("%Y-%m-%d"),
            "end_date": campaign.end_date.strftime("%Y-%m-%d"),
            "image_url": campaign.image.url if campaign.image else None  # Handle missing image
        }
        for campaign in campaigns
    ]
    return JsonResponse({"campaigns": campaign_data})

@csrf_exempt
def update_campaign(request, campaign_id):
    if request.method == 'POST':
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Retrieve updated fields
            title = request.POST.get('title', campaign.title)
            description = request.POST.get('description', campaign.description)
            start_date = request.POST.get('start_date', campaign.start_date)
            end_date = request.POST.get('end_date', campaign.end_date)
            points = request.POST.get('points', campaign.points)

            # Update text fields
            campaign.title = title
            campaign.description = description
            campaign.start_date = start_date
            campaign.end_date = end_date
            campaign.points = points

            # Handle image update or deletion
            if 'image' in request.FILES:
                campaign.image = request.FILES['image']  # Update with new image
            elif request.POST.get('delete_image') == 'true':
                campaign.image.delete(save=False)  # Delete existing image
                campaign.image = None

            campaign.save()

            # Return updated campaign data, including the image URL if it exists
            response_data = {
                "success": True,
                "image_url": campaign.image.url if campaign.image else None  # Updated image URL
            }
            return JsonResponse(response_data)
        except Campaign.DoesNotExist:
            return JsonResponse({"success": False, "error": "Campaign not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})


def delete_campaign(request, campaign_id):
    if request.method == 'POST':
        try:
            campaign = Campaign.objects.get(id=campaign_id)
            campaign.delete()
            return JsonResponse({"success": True})
        except Campaign.DoesNotExist:
            return JsonResponse({"success": False, "error": "Campaign not found."})

def rewards_activity_view(request):
    user = request.user
    student = user.student  # Assuming there's a Student profile related to the user
    current_balance = student.points_balance

    if request.method == "POST":
        reward_id = request.POST.get("reward_id")
        reward = Reward.objects.get(id=reward_id)

        if student.points_balance >= reward.points_required and reward.is_active:
            # Deduct points and create RewardExchange entry
            student.points_balance -= reward.points_required
            student.save()

            RewardExchange.objects.create(
                student=student,
                reward=reward,
                points_used=reward.points_required
            )

            messages.success(request, f"You have successfully redeemed {reward.title}!")
            # Mark the reward as inactive
            reward.is_active = False
            reward.save()
        else:
            messages.error(request, "You do not have enough points or the reward is not available.")

        return redirect("rewards_activity")  # Adjust the redirect as needed

    # Fetch completed campaigns
    completed_actions = CompletedAction.objects.filter(student=student)

    # Fetch previous reward exchanges
    previous_exchanges = RewardExchange.objects.filter(student=student)

    # Fetch available rewards for redemption
    possible_rewards = Reward.objects.filter(
        is_active=True,
        available_from__lte=timezone.now(),
        available_until__gte=timezone.now()
    )

    context = {
        'current_balance': current_balance,
        'completed_actions': completed_actions,
        'previous_exchanges': previous_exchanges,
        'possible_rewards': possible_rewards,
    }
    return render(request, 'rewards_activity.html', context)

#def actions(request):
    return render(request, 'actions.html')

def action_page_view(request):
    user = request.user
    student = user.student
    ongoing_campaigns = Campaign.objects.filter(start_date__lte=now(), end_date__gte=now())

    if request.method == "POST":
        campaign_ids = request.POST.get("campaign")
        photo = request.FILES.get("photo")

        if not campaign_ids or not photo:
            messages.error(request, "Please select at least one campaign and upload a photo.")
            return redirect("action_page")

        for campaign_id in campaign_ids:
            campaign = Campaign.objects.get(id=campaign_id)
            
            # Create Action first
            action = Action.objects.create(
                name=f"{campaign.title} Completion",
                description=f"Completed {campaign.title}",
                points=campaign.points,
                is_active=True
            )

            # Then create CompletedAction with both action and campaign
            CompletedAction.objects.create(
                student=student,
                action=action,
                campaign=campaign,
                photo=photo,
                date_completed=now(),
                points_earned=campaign.points
            )

            student.points_balance += campaign.points
            if student.user.email not in campaign.completed_by:
                campaign.completed_by.append(student.user.get_full_name())
        campaign.save()
        student.save()
        messages.success(request, "Action submitted successfully!")
        return redirect("rewards_activity")

    return render(request, "action_page.html", {
        "ongoing_campaigns": ongoing_campaigns,
    })

from django.utils.timezone import now

def campaign_data_view(request):
    today = now().date()

    past_campaigns = Campaign.objects.filter(end_date__lt=today)
    present_campaigns = Campaign.objects.filter(start_date__lte=today, end_date__gte=today)
    future_campaigns = Campaign.objects.filter(start_date__gt=today)

    context = {
        'past_campaigns': past_campaigns,
        'present_campaigns': present_campaigns,
        'future_campaigns': future_campaigns
    }
    return render(request, 'campaign_data.html', context)


def create_reward(request):
    today = date.today()
    if request.method == 'POST':
        # Handle the form submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        points_required = request.POST.get('points_required', 0)
        available_from = request.POST.get('available_from')
        available_until = request.POST.get('available_until')

        if title and description and points_required and available_from and available_until:
            Reward.objects.create(
                title=title,
                description=description,
                points_required=points_required,
                available_from=available_from,
                available_until=available_until,
            )
            return redirect('create_reward')

    # Get the first 2 rewards and the total count
    rewards = Reward.objects.filter(available_from__lte=today, available_until__gte=today)[:2]
    total_rewards = Reward.objects.filter(available_from__lte=today, available_until__gte=today).count()
    return render(request, 'reward_create.html', {'rewards': rewards, 'total_rewards': total_rewards})

def load_more_rewards(request):
    today = date.today()
    offset = int(request.GET.get('offset', 2))

    rewards = Reward.objects.filter(available_from__lte=today, available_until__gte=today)[offset:]
    reward_data = [
        {
            "id": reward.id,
            "title": reward.title,
            "description": reward.description,
            "points_required": reward.points_required,
            "available_from": reward.available_from.strftime("%Y-%m-%d"),
            "available_until": reward.available_until.strftime("%Y-%m-%d"),
        }
        for reward in rewards
    ]
    return JsonResponse({"rewards": reward_data})

@csrf_exempt
def update_reward(request, reward_id):
    if request.method == 'POST':
        try:
            reward = Reward.objects.get(id=reward_id)

            # Retrieve updated fields
            title = request.POST.get('title', reward.title)
            description = request.POST.get('description', reward.description)
            points_required = request.POST.get('points_required', reward.points_required)
            available_from = request.POST.get('available_from', reward.available_from)
            available_until = request.POST.get('available_until', reward.available_until)

            # Update fields
            reward.title = title
            reward.description = description
            reward.points_required = points_required
            reward.available_from = available_from
            reward.available_until = available_until

            reward.save()

            return JsonResponse({"success": True})
        except Reward.DoesNotExist:
            return JsonResponse({"success": False, "error": "Reward not found."})
    return JsonResponse({"success": False, "error": "Invalid request method."})

def delete_reward(request, reward_id):
    if request.method == 'POST':
        try:
            reward = Reward.objects.get(id=reward_id)
            reward.delete()
            return JsonResponse({"success": True})
        except Reward.DoesNotExist:
            return JsonResponse({"success": False, "error": "Reward not found."})
