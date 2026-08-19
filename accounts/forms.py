"""Forms for signup and login."""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()


class SignupForm(UserCreationForm):
    """Signup with a single full name, email and password."""

    name = forms.CharField(max_length=120, required=True, label='Full name')
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        full_name = self.cleaned_data['name'].strip()
        user.email = email
        user.username = email  # keep username == email for admin compatibility
        # Store the full name in `first_name` so the existing User model keeps
        # working without a migration that breaks admin lookups.
        user.first_name = full_name
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Standard auth form — used with email-based users."""

    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))
