from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import NPTView, index
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = {
    #url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'v1.0/npt/$', NPTView.as_view(), name="npt" ),
    #url(r'^get-token/', obtain_auth_token),
}

urlpatterns = format_suffix_patterns(urlpatterns)