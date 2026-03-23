from django import forms
from django.contrib.auth.models import User

from .models import Customer, UserProfile



class checkEmail:
    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email


class UserForm(checkEmail, forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('first_name', 'last_name', 'email'):
            self.fields[field].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserUpdateForm(checkEmail, forms.ModelForm):

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ('first_name', 'last_name', 'email'):
            self.fields[field].required = True


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'e.g. +1 555 000 1234'}),
        }


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
