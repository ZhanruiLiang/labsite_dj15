from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms
from debug import dprint

class User(AbstractUser):
    usertype = models.CharField(max_length=10)
    studentID = models.CharField(max_length=10)

AvailType = ['TA', 'student']

class RegisterForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': ("A user with that username already exists."),
        'password_mismatch': ("The two password fields didn't match."),
        'studentID_invalid': ("The studentID is invalid."),
    }
    username = forms.RegexField(label=("Username"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': ("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    studentID = forms.RegexField(label=("StudentID"), max_length=10,
            regex=r'^\d{8}$',)
    password1 = forms.CharField(label=("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('username', 'studentID', 'password1', 'password2', 'email')

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def clean_studentID(self):
        studentID = self.cleaned_data['studentID']
        # TODO: some check here
        return studentID

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

LoginForm = AuthenticationForm
