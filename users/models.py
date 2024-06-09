from django.db import models
from django.contrib.auth.models import User
from PIL import Image

# Create your models here.
#using the below argument, we say that one user can have a single profile.
#cascade tells us that if an user is deleted, delete the profile as well and if we delete the profile the user wont be deleted.
# We are creating this models to enable the users to upload a profile picture.
class Profile(models.Model): 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pictures')

    def __str__(self):
        return f'{self.user.username} Profile'
    #for restricting the profile image size
    
    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        re_size = Image.open(self.image.path)
        if re_size.height >300 or re_size.width >300:
            output_size = (300,300)
            re_size.thumbnail(output_size)
            re_size.save(self.image.path) 



   


