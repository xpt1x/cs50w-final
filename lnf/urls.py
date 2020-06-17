from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('register', views.register, name='register'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('listings', views.listings_view, name='listings'),
    path('report', views.report_view, name='report'),
    path('remove/<int:item_id>', views.remove_view, name='remove_item'),
    path('userListings', views.userListings_view, name='userListings'),
    path('match/<int:item_id>', views.match, name='match'),
    path('lostitems', views.lostitems_view, name='lostitems'),
    path('founditems', views.founditems_view, name='founditems')
]