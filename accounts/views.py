"""Views for signup, login, logout."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignupForm


class SignupView(CreateView):
    """Create a new account and log the user in."""

    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('bookings:dashboard')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Welcome to CybergateFX.')
        return response


def login_view(request):
    """Email-based login."""
    from .forms import LoginForm  # imported here to avoid circular import
    from django.contrib.auth import authenticate

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.email}.')
            return redirect('bookings:dashboard')
    else:
        form = LoginForm(request)
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Log out and send the user back to the homepage."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('mentors:home')
