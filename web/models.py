from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class Account(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    code = models.CharField(max_length=6, null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.email

class Session(models.Model):
    sessionID = models.CharField(max_length=255, primary_key=True)
    expiry = models.DateTimeField()
    userID = models.ForeignKey(Account, on_delete=models.CASCADE)

class Topic(models.Model):
    topicName = models.CharField(max_length=100)
    dailyPrice = models.DecimalField(max_digits=10, decimal_places=2)
    weeklyPrice = models.DecimalField(max_digits=10, decimal_places=2)
    monthlyPrice = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.topicName

class TopicVideo(models.Model):
    topicID = models.ForeignKey(Topic, on_delete=models.CASCADE)
    videoName = models.CharField(max_length=200)
    videoLink = models.URLField()
    thumbnail = models.TextField()  # Base64 encoded image

    def __str__(self):
        return self.videoName

class Subscription(models.Model):
    userID = models.ForeignKey(Account, on_delete=models.CASCADE)
    topicID = models.ForeignKey(Topic, on_delete=models.CASCADE)
    expiry = models.DateTimeField()

    def __str__(self):
        return f"{self.userID} - {self.topicID}"