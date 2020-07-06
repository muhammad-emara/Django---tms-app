from django.db import models
from django.forms import ModelForm
from django.core import validators

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Teacher(models.Model):
    first_name = models.CharField(max_length=26, null=False, blank=False)
    last_name = models.CharField(max_length=26, null=False, blank=False)
    profile_picture = models.ImageField(upload_to='images/', null=True, blank=True)
    email_address = models.EmailField(unique=True, validators=[validators.EmailValidator], null=False, blank=False)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    room_number = models.CharField(max_length=5, null=True, blank=True)
    subject_taught = models.ManyToManyField(Subject, null=False, blank=True)

    def __str__(self):
        return self.last_name + ' ' + self.first_name

    def save(self, *args, **kwargs):
        if self.profile_picture is None or self.profile_picture == ' ' or self.profile_picture == ' ':
            self.profile_picture = 'default.png'
        super(Teacher, self).save(*args, **kwargs)





