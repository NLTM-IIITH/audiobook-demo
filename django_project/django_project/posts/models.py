from django.db import models
import requests
import cv2,json
import io,os
from gtts import gTTS
import tempfile
from django.core.files import File
# Create your models here to save them in the database. Apply migrate and makemigrations
class Post(models.Model):
    languages = [
        ("en", "english"),
        ("hi", "hindi"),
        ("te", "telugu"),
        ("ta", "tamil"),
        ("mr", "marati"),
        ("ml", "malayalam"),
        ("mr", "marati"),
        ("bn","bengali"),
        ("gu","gujarati"),
        ("kn","kannada"),
        ("ne","nepali"),
        ("ur","urdu")
    ]
    language = models.CharField(
        max_length=2,
        choices=languages,
        default="en",
    )
    # instance_id = models.BigIntegerField(default=0)
    cover = models.ImageField()
    text_detected = models.TextField(default="default")
    mp4 = models.FileField(null=True)
    # renames the instances of the model
    # with their language
    def __str__(self):
        return self.language