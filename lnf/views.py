from django.shortcuts import render, reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse, HttpResponseRedirect
from .models import Item, Profile
from django.db.models import Q
from .utils import send_html_mail

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
    return render(request, 'lnf/index.html')

def listings_view(request):
    if request.method == 'GET':
        return render(request, 'lnf/listings.html', {'items': Item.objects.all()})
    elif request.method == 'POST':
        s_item = request.POST['search']
        if not s_item:
            messages.add_message(request, messages.ERROR, 'Invalid search')
            return HttpResponseRedirect('listings')
        items = Item.objects.filter(
            Q(name__icontains=s_item) | Q(color__icontains=s_item) | Q(brand__icontains=s_item) | Q(location__icontains=s_item)
        )
        if not items:
            return render(request, 'lnf/listings.html', {'empty':True})
        return render(request, 'lnf/listings.html', {'items': items})

def userListings_view(request):
    items = Item.objects.filter(uploader=request.user)
    if not items:
        return render(request, 'lnf/userlistings.html', {'empty':True})
    return render(request, 'lnf/userlistings.html', {'items': items})

def report_view(request):
    if request.method == 'POST':
        try:
            image = request.FILES['inputImage']
        except:
            image = None
        item = Item(name=request.POST['inputName'].lower(), color=request.POST['inputColor'].lower(), location=request.POST['inputLocation'], date=request.POST['inputDate'].lower(), brand=request.POST['inputBrand'].lower(), contents=request.POST['inputContents'].lower(), status=request.POST['inputType'].lower(), uploader=request.user, image=image)
        item.save()
        messages.add_message(request, messages.SUCCESS, f'Added {request.POST["inputType"]} Report for {request.POST["inputName"]}')
        if item.status == 'found':
            MatchItem(request, item)
        return HttpResponseRedirect(reverse('home'))

def remove_view(request, item_id):
    item = Item.objects.get(pk=item_id)
    if not item:
        messages.add_message(request, messages.ERROR, 'Invalid item')
        return HttpResponseRedirect(reverse('userListings'))
    if item.uploader != request.user:
        messages.add_message(request, messages.ERROR, 'You are not authorized to do this action')
        return HttpResponseRedirect(reverse('userListings'))
    item.delete()
    return HttpResponseRedirect(reverse('userListings'))

def match(request, item_id):
    item = Item.objects.get(pk=item_id)
    #items = Item.objects.filter(name=item.name, color=item.color, status='found')
    items = Item.objects.filter((
            Q(name__icontains=item.name) | Q(color__icontains=item.color) | Q(brand__icontains=item.brand) | Q(location__icontains=item.location)
        ), status='found')
    return render(request, 'lnf/match.html', {'items': items})

def lostitems_view(request):
    return render(request, 'lnf/listings.html', {'items': Item.objects.filter(status='lost')})

def founditems_view(request):
    return render(request, 'lnf/listings.html', {'items': Item.objects.filter(status='found')})

def register(request):
    if request.method == 'GET':
        return render(request, 'lnf/register.html')
    try:
        username = request.POST['username']
        password = request.POST['password']
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Invalid Entry')
        return HttpResponseRedirect(reverse('register'))
    if not username:
        messages.add_message(request, messages.ERROR, 'Invalid Username')
        return HttpResponseRedirect(reverse('register'))
    if not password:
        messages.add_message(request, messages.ERROR, 'Invalid password')
        return HttpResponseRedirect(reverse('register'))
    
    check_user = User.objects.filter(username=username)
    if check_user:
        messages.add_message(request, messages.ERROR, 'UserName already exists, try something else')
        return HttpResponseRedirect(reverse('register'))

    user = User.objects.create_user(username=username, password=password, email=request.POST['email'])
    user.save()
    profile = Profile(user=user, contact=request.POST['contact'])
    profile.save()
    login(request, user)

    messages.add_message(request, messages.SUCCESS, 'Registeration successful!')
    return HttpResponseRedirect(reverse('home'))

def login_view(request):
    if request.method == 'GET':
        return render(request, 'lnf/login.html')
    try:
        username = request.POST['username']
        password = request.POST['password']
        
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Invalid Entry')
        return HttpResponseRedirect(reverse('login'))
    if not username:
        messages.add_message(request, messages.ERROR, 'Invalid Username')
        return HttpResponseRedirect(reverse('login'))
    if not password:
        messages.add_message(request, messages.ERROR, 'Invalid password')
        return HttpResponseRedirect(reverse('login'))

    user = authenticate(request, username=username, password=password)
    if not user:
        messages.add_message(request, messages.ERROR, 'Invalid Credentials')
        return HttpResponseRedirect(reverse('login'))
    else:
        login(request, user)
        messages.add_message(request, messages.SUCCESS, 'Logged in successfully')
        return HttpResponseRedirect(reverse('home'))

def logout_view(request):
    logout(request)
    messages.add_message(request, messages.SUCCESS, 'Logged Out successfully')
    return HttpResponseRedirect(reverse('home'))   

def MatchItem(request, item):
    items = Item.objects.filter((
            Q(name__icontains=item.name) | Q(color__icontains=item.color) | Q(brand__icontains=item.brand) | Q(location__icontains=item.location)
        ), status='lost')
    for item in items:
        link = reverse('match', kwargs={'item_id': item.pk})
        msg = f'System has found some matching items! Please visit this link to view {request.META["HTTP_HOST"]}{link}'
        send_html_mail(f'[ LostnFound ] Matches found for {item.name}', msg, [item.uploader.email])