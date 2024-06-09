from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserSignupForm


#User registration view
def signup(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created successfully for {username}. Sign in with new credentials.')
            return redirect('wdg-login')
    else:
        form = UserSignupForm()
    return render(request,'signup.html',{'form':form})




