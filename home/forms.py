from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import Url, Repository, SendEmail

#Form that lets the user to add an existing URL
class AddUrlForm(ModelForm):
    url = forms.URLField()
    title = forms.TextInput()

    class Meta():
        model = Url
        fields = ['url','title']

#Repository creation form with title and studentnames fields.
class RepositoryForm(ModelForm):
    title = forms.TextInput()
    students = forms.CharField(
        widget=forms.Textarea,
        help_text='Enter the GitHub usernames of the students separated by commas.'
    )

    class Meta:
        model = Url
        fields = ['title', 'students']

#Form to send emails to the students
class EmailForm(ModelForm):
    Email = forms.EmailField()
    subject = forms.CharField()
    text = forms.TextInput()
    class Meta:
        model = SendEmail
        fields = ['Email','subject', 'text']



    