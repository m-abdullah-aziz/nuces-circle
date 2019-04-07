from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Education, Interests, Skills, Profile, UserConnections, User
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, EducationForm, InterestsForm, SkillForm
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')  # When data is cleaned it is converted to appropriate type
            messages.success(request, f'Account created for {username}!')
            return redirect('circle-login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def view_profile(request, *args, **kwargs):
    # Education.objects.all().delete()
    uid = int(kwargs['uid'])
    ##############################################################################################################
    to_user = User.objects.get(pk=uid)
    p = Profile.objects.get(user=to_user)
    friends = p.friends.all()

    # is this user our friend
    button_status = 'none'
    if p not in request.user.profile.friends.all():
        button_status = 'not_friend'
        # if we have sent him a friend request
        if len(UserConnections.objects.filter(from_user=request.user).filter(to_user=p.user)) == 1:
            button_status = 'friend_request_sent'
    edu_data = Education.objects.all()
    interests = Interests.objects.all()
    skill_data = Skills.objects.all()
    context = {
        'to_user': to_user,
        'button_status': button_status,
        'friends_list': friends,
        'education_data': edu_data,
        'interests': interests,
        'skill_data': skill_data,
        'uid': uid
    }
    return render(request, 'users/view_profile.html', context)


@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)  # current logged in user
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            fuser = user_form.save(commit=False)
            fuser.set_password(request.POST.get('password'))
            fuser.save()
            profile_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)  # current logged in user
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/profile.html', context)


@login_required
def edit_education_info(request, *args, **kwargs):
    edu_id = int(kwargs['edu_info_id'])
    edu_data = Education.objects.get(pk=edu_id)
    education_form = EducationForm(instance=edu_data)
    return render(request, 'users/edit_edu.html', context={'education_form': education_form,
                                                           'edu_data': edu_data})


@login_required
def update_education_info(request, *args, **kwargs):
    eid = int(kwargs['edu_info_id'])
    if request.method == 'POST':
        # obj = Education.objects.filter(pk=eid)
        edu_data = Education.objects.get(pk=eid)
        education_form = EducationForm(request.POST, instance=edu_data)
        education_form.save()
    # edu_data = Education.objects.all()
    return redirect('view-profile')


@login_required
def add_education_info(request):
    education_from = EducationForm()
    return render(request, 'users/add_edu.html', context={'education_form': education_from})


@login_required
def submit_education_info(request):
    if request.method == 'POST':
        education_from = EducationForm(request.POST)
        ed = education_from.save(commit=False)
        ed.user = request.user
        ed.save()
    return redirect('view-profile')


@login_required
def edit_interest_info(request):
    int_data = Interests.objects.all().first()
    int_form = InterestsForm(instance=int_data)
    return render(request, 'users/edit_int.html', context={'int_form': int_form,
                                                           'int_data': int_data})


@login_required
def update_interest_info(request):
    if request.method == 'POST':
        # obj = Education.objects.filter(pk=eid)
        int_data = Interests.objects.all().first()
        int_form = InterestsForm(request.POST, instance=int_data)
        int_f = int_form.save(commit=False)
        int_f.user = request.user
        int_f.save()
    # edu_data = Education.objects.all()
    return redirect('view-profile')


@login_required
def edit_skill_info(request, *args, **kwargs):
    skill_id = int(kwargs['skill_id'])
    skill_data = Skills.objects.get(pk=skill_id)
    skill_form = SkillForm(instance=skill_data)
    return render(request, 'users/edit_skill.html', context={'skill_form': skill_form,
                                                             'skill_data': skill_data})


@login_required
def add_skill_info(request):
    skill_form = SkillForm()
    return render(request, 'users/add_skill.html', context={'skill_form': skill_form})


@login_required
def submit_skill_info(request):
    if request.method == 'POST':
        skill_form = SkillForm(request.POST)
        sk = skill_form.save(commit=False)
        sk.user = request.user
        sk.save()
    return redirect('view-profile')


@login_required
def delete_skill_info(request, *args, **kwargs):
    skill_id = int(kwargs['skill_id'])
    # if request.method == 'POST':
    # obj = Education.objects.filter(pk=eid)
    sk = Skills.objects.get(pk=skill_id)
    print(sk.skill)
    sk.delete()
    # edu_data = Education.objects.all()
    return redirect('view-profile')


@login_required
def update_skill_info(request, *args, **kwargs):
    skill_id = int(kwargs['skill_id'])
    if request.method == 'POST':
        # obj = Education.objects.filter(pk=eid)
        skill_data = Skills.objects.get(pk=skill_id)
        skill_form = SkillForm(request.POST, instance=skill_data)
        skill_form.save()
    # edu_data = Education.objects.all()
    return redirect('view-profile')

# For connecting with users


def users_list(request):
    users = Profile.objects.exclude(user=request.user)
    context = {
        'users': users
    }
    return render(request, "", context)


def send_connect_request(request, *args, **kwargs):
    uid = int(kwargs['uid'])
    user = get_object_or_404(User, id=uid)
    frequest, created = UserConnections.objects.get_or_create(from_user=request.user, to_user=user)
    return redirect('view-profile', uid=uid)


def cancel_connect_request(request, *args, **kwargs):
    uid = int(kwargs['uid'])
    user = get_object_or_404(User, id=uid)
    frequest = UserConnections.objects.filter(
        from_user=request.user,
        to_user=user).first()
    frequest.delete()
    return redirect('view-profile', uid=uid)


def accept_connect_request(request, *args, **kwargs):
    uid = int(kwargs['uid'])
    from_user = get_object_or_404(User, id=uid)
    frequest = UserConnections.objects.filter(from_user=from_user, to_user=request.user).first()
    user1 = frequest.to_user
    user2 = from_user
    user1.profile.friends.add(user2.profile)
    user2.profile.friends.add(user1.profile)
    frequest.delete()
    return redirect('/users/{}'.format(request.user.profile.slug))


def delete_connect_request(request, *args, **kwargs):
    uid = int(kwargs['uid'])
    from_user = get_object_or_404(User, id=uid)
    frequest = UserConnections.objects.filter(from_user=from_user, to_user=request.user).first()
    frequest.delete()
    return redirect('/users/{}'.format(request.user.profile.slug))
