from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Url(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    title = models.CharField(max_length=200)
 
    def __str__(self):
        return self.title

#Model that stores the repository data like the created user of the repo, title, and the url.
class Repository(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    url = models.URLField(max_length=200)

    def __str__(self):
        return self.title

#Model that stores the user, email, subject, and text of the email sent by the user to a contributor.
class SendEmail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Email = models.EmailField()
    subject = models.TextField()
    text = models.TextField()

    def __str__(self):
        return self.recepientemail


    

    

