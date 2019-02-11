from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
import sys
from django.core.files.uploadedfile import InMemoryUploadedFile


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        # Opening the uploaded image
        im = Image.open(self.image)

        output = BytesIO()

        # Resize/modify the image
        output_size = (300, 300)
        im = im.resize(output_size)

        # after modifications, save it to the output
        im.save(output, format='JPEG', quality=90)
        output.seek(0)

        # change the imagefield value to be the newly modified image value
        self.image = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.image.name.split('.')[0], 'image/jpeg',
                                          sys.getsizeof(output), None)
        super().save(*args, **kwargs)
