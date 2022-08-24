from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

# User Admin Form
class VUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields


class VUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields
