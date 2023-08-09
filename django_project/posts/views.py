from django.shortcuts import render
from django.views.generic import ListView,CreateView
from .models import Post
from django.http import HttpResponse
from django.urls import reverse_lazy
from .forms import PostForm
import requests
import cv2,json
import io
import os
from PIL import Image
from io import BytesIO
import numpy as np
from gtts import gTTS
import tempfile
from django.core.files import File
from django.shortcuts import redirect
from django.core.files.base import ContentFile

text_detected = ""
k=""


def detect_text(image):
        response = requests.get(image)
        img1 = Image.open(BytesIO(response.content))
        img1.show()
        img= np.array(img1)
        _,compressedimage = cv2.imencode(".png",img,[1,90])
        file_bytes = io.BytesIO(compressedimage)
        url_api = 'https://api.ocr.space/parse/image'
        result = requests.post(url_api,files={'.png':file_bytes},data={"apikey":"63e8d7969688957"})
        
        result = result.content.decode()
        result = json.loads(result)
        if (result.get("OCRExitCode")!=1):
               return "Could not detect text."
        parsed_results = result.get("ParsedResults")[0]
        text_detected = parsed_results.get("ParsedText")
        return text_detected


class HomePageView(ListView):
    model = Post
    template_name = "home.html"
    
    

class CreatePostView(CreateView):  
    model = Post
    form_class = PostForm
    template_name = "post.html"
    def get_success_url(self) -> str:
           return reverse_lazy('result',kwargs={'pk':self.iid})
    def form_valid(self,form):
        instance = form.save()
        # print("http://127.0.0.1:8000"+instance.cover.url)
        k = detect_text("http://10.4.16.81:2900/"+instance.cover.url)
        instance.text_detected=k
        mp4 = gTTS(text=k,lang=instance.language) 
        audio_buffer = io.BytesIO()
        mp4.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_content = audio_buffer.read()
        audio = ContentFile(audio_content) 
        file_name = '{}.mp3'.format(instance.language)
        file_path = file_name
        # print(file_path)
        instance.mp4.save(file_path, audio)
        # instance.instance_id=instance.id
        self.iid = instance.id
        instance.save()
        print("saved",instance.text_detected)
        # print(instance_id)
        return redirect(reverse_lazy('r',kwargs={'pk':self.iid}))
        

def result(request, pk):
    data_from_db = Post.objects.filter(id=pk)
    return render(request,'result.html',{'data_from_db':data_from_db})