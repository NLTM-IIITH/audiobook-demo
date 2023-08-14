from typing import Any, Optional
from django.db import models
from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,CreateView,DeleteView
from .models import Post
from django.http import HttpResponse
from django.urls import reverse_lazy
from .forms import PostForm
import requests
import cv2,json
import io
import os
import base64
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


def detect_text(image,lang,name):
        arr = []
        text_detected = ""
        response = requests.get(image)
        img1 = Image.open(BytesIO(response.content))
        # img1.show()
        img= np.array(img1)
        _,compressedimage = cv2.imencode(".png",img,[1,90])
        file_bytes = io.BytesIO(compressedimage)
        # url_api = 'https://api.ocr.space/parse/image'
        url_api = 'https://ilocr.iiit.ac.in/layout/'
        result = requests.post(url_api, files={'images': ('.png', file_bytes, 'image/png')})
        # for i in result:
        #     print(i)
        result = result.content.decode()
        result = json.loads(result)
        bb = result[0]['regions']
        for i in bb:
            x = i['bounding_box']['x']
            y = i['bounding_box']['y']
            w = i['bounding_box']['w']
            h = i['bounding_box']['h']

            
            
            cropped_image = img1.crop((x, y, x + w, y + h))
            # cropped_image.show()
            image_array = np.array(cropped_image)
            image_data = Image.fromarray(image_array)
            image_buffer = io.BytesIO()
            image_data.save(image_buffer, format="PNG")  # Replace "JPEG" with the appropriate format
            base64_encoded = base64.b64encode(image_buffer.getvalue()).decode('utf-8')

            arr.append(base64_encoded)
        
        ocr_api = 'https://ilocr.iiit.ac.in/ocr/infer'
        data = {
            "imageContent":arr,
            "modality": "printed",
            "level": "word",
            "language": lang,
            "version": "v4",
            "modelid": "",
            "omit": True,
            "meta": {}

        }
        
        result2 = requests.post(ocr_api, json=data)
        print(result2.status_code)
        # for i in result2:
        #     if(i['detail']=="No model available for "):
        #         return "Could not detect any text"
        if(result2.status_code == 200):
            for i in result2.json():
                print(i)
                text_detected = text_detected +i['text']+" "

            print(text_detected)
            if (text_detected == " " or text_detected == ""):
                return "Could not detect any text"
                
            else:
                return text_detected
        else:
            return "Could not detect any text"


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
        k = detect_text("http://10.4.16.81:2900/"+instance.cover.url,instance.language,instance.cover)
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

def delete_item(request, pk):
    item = get_object_or_404(Post, pk=pk)
    item.delete()
    return redirect('add_post')
