from django.shortcuts import render, redirect
from .forms import RegisterForm, ProfileForm
import logging
logger = logging.getLogger(__name__)


# Create your views here.
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            return redirect("login")
    else:
        form = RegisterForm()
        profile_form = ProfileForm()

    return render(request, 'registration/register.html', {"form": form, "profile_form": profile_form})
