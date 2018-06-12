from rest_framework.views import APIView 
from rest_framework.response import Response 
 
from jsonstore import models 
from .serializers import JsonStatSerializer 
 
 
class JsonStatList(APIView): 
	""" 
	Return the most recent public posts by all users 
	""" 
	def get(self, request): 
		msgs = models.JsonStat.objects.all()
		data = JsonStatSerializer(msgs, many=True).data 
		return Response(data)
