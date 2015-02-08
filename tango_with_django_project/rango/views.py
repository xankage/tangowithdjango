from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime

@login_required
def restricted(request):
  return HttpResponse('Since you can see this, you are logged in! <br/><a hreF="/rango/">Home</a>')
#
#def user_login(request):
#  if request.method == 'POST':
#    username = request.POST['username']
#    password = request.POST['password'] 
#
#    user = authenticate(username=username, password=password)
#
#    if (user):
#      if (user.is_active):
#        login(request, user)
#        return HttpResponseRedirect('/rango/')
#
#      else:
#       return HttpResponse('Your rango account has been disabled. <br/><a href='/rango/login/'>Return</a>')
#    else:
#      print "Invalid login details: {0}, {1}".format(username, password)
#      return HttpResponse("Invalid login details. <br/><a href='/rango/login/'>Return</a>") #replace with more informative statement? i.e. username does not exist/wrong password - poor idea security-wise
#  else:
#    return render(request, 'rango/login.html', {})
   
#@login_required
#def user_logout(request):
#  logout(request)
#  
#  return HttpResponseRedirect('/rango/')
#
#def register(request):
#  if request.session.test_cookie_worked():
#    print "test cookie worked"
#    request.session.delete_test_cookie()
#  registered = False
#
#  if request.method == 'POST':
#    user_form = UserForm(data=request.POST)
#    profile_form = UserProfileForm(data=request.POST)
#    
#    if user_form.is_valid() and profile_form.is_valid(): 
#      user = user_form.save()
#      
#      user.set_password(user.password)
#      user.save()
#
#      profile = profile_form.save(commit = False)
#      profile.user = user
#      
#      if 'picture' in request.FILES:
#        profile.picture = request.FILES['picture']  
#      
#      profile.save()
#
#      registered = True
#    else:
#      print user_form.errors, profile_form.errors
#  else:
#    user_form = UserForm()
#    profile_form = UserProfileForm()
#
#  return render(request, 'rango/register.html', {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

@login_required
def add_category(request):
  if request.method == 'POST':
    form = CategoryForm(request.POST)  
    
    if form.is_valid():
      form.save(commit=True)
      return index(request) 
    else:
      print form.errors

  else:
    form = CategoryForm()

  return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
  try:
    cat = Category.objects.get(slug=category_name_slug)
  except Category.DoesNotExist:
    cat = None

  if request.method == 'POST':
    form = PageForm(request.POST)

    if form.is_valid():
      if cat:
        page = form.save(commit=False)
        page.category = cat
        page.save()
        return index(request)
    else:
      print form.errors

  else:
    form = PageForm()

  return render(request, 'rango/add_page.html', {'form': form, 'cat': cat})

def index(request):
  request.session.set_test_cookie()

  categories_list = Category.objects.order_by('-likes')[:5]
  pages_list = Page.objects.order_by('-views')[:5]
  context_dict = {'categories': categories_list, 'pages': pages_list,
  }
  
  visits = request.session.get('visits')
  if not visits:
    visits = 1 
  reset_last_visit_time = False

  last_visit = request.session.get('last_visit')  
  if last_visit:
    last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - last_visit_time).days > 0:
      visits = visits + 1
      reset_last_visit_time = True
  else:
      reset_last_visit_time = True

  if (reset_last_visit_time):
    request.session['visits'] = visits
    request.session['last_visit'] = str(datetime.now())
    
  context_dict['visits'] = visits
  response = render(request, 'rango/index.html', context_dict) #why called twice??

  return response

def about(request):
  context_dict = {'author': "Alexander Nedergaard, 2018207"}
  visits = request.session.get('visits')
  if not visits:
    visits = 0 
  context_dict['visits'] = visits
  return render(request, 'rango/about.html', context_dict)


# pages_list = Page.objects.all()
 # context_dict = {'categories': categories_list, 'pages': pages_list}
 # return render(request, 'rango/details.html', context_dict)

def category(request, category_name_slug):
  context_dict = {}
  try:
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category_name'] = category.name
    pages = Page.objects.filter(category=category)
    context_dict['pages'] = pages
    context_dict['category'] = category
    context_dict['category_slug_name'] = category.slug
  except Category.DoesNotExist:
    pass
  return render(request, 'rango/category.html', context_dict)

def what(request):
  context_dict = {}
  return render(request, 'rango/what.html', context_dict)
