from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label='用户名',
                                max_length=100,
                                required=True,
                                widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "用户名"})
                                )
    password = forms.CharField(label='密码',
                                max_length=100,
                                required=True,
                                widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "密码"})
                                )
