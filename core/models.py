from django.db import models

class TimeStampedModel(models.Model):
    
    """ Time Stamped Model """

    created = models.DateTimeField(auto_now_add=True) #생성할때 자동을 값 집어넣음
    updated = models.DateTimeField(auto_now = True)  #수정할때마다 새로운 Data 집어넣

    class Meta:
        abstract = True
        
