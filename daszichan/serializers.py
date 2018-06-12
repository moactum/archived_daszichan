from rest_framework import serializers 
from jsonstore import models 
 
 
class JsonStatSerializer(serializers.ModelSerializer): 
	class Meta: 
		model = models.JsonStat
		fields = ("metric", "timestamp","data")
