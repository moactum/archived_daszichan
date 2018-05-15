"""daszichan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import permissions
from django.urls import include, path, re_path
from admin.admin_site import my_admin_site
from admin.admin_site_public import my_admin_site_public
from rest_framework_simplejwt.views import (
	TokenObtainPairView,
	TokenVerifyView,
	TokenRefreshView,
)
from .views import homepage
# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
	class Meta:
		model = User
		fields = ('url', 'username', 'email', 'is_staff')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	serializer_class = UserSerializer
	#permission_classes = [ permissions.IsAuthenticated ]

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
	re_path('^$', homepage, name='home'),
	path('admin/doc/', include('django.contrib.admindocs.urls')),
	path('admin/', admin.site.urls),
	path('agents/', my_admin_site.urls),
	path('public/', my_admin_site_public.urls),
	path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
	path('api/', include(router.urls)),
]
