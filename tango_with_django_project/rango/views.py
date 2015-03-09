from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from datetime import datetime
from rango.bing_search import run_query

def track_url(request):
  if request.method == 'GET':
    if 'page_id' in request.GET:
      title = request.GET['page_id']
      page = Page.objects.get(title = title)
      page.views = page.views + 1
      page.save()
      return HttpResponseRedirect(page.url)
  return HttpResponse('Page not found <br/><a href="/rango/">Home</a>')

@login_required
def restricted(request):
  return HttpResponse('Since you can see this, you are logged in! <br/><a hreF="/rango/">Home</a>')

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

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


def category(request, category_name_slug):
  context_dict = {}
  context_dict['result_list'] = None
  context_dict['query'] = None
 
  if request.method == 'POST':
    query = request.POST['query'].strip()
    if query:
      result_list = run_query(query)
      context_dict['result_list'] = result_list
      context_dict['query'] = query

  try:
    category = Category.objects.get(slug=category_name_slug)
    context_dict['category_name'] = category.name
    pages = Page.objects.filter(category=category)
    context_dict['pages'] = pages
    context_dict['category'] = category
    context_dict['category_slug_name'] = category.slug
  except Category.DoesNotExist:
    pass
 
  
  if not context_dict['query']:
    context_dict['query'] = category.name
 
  return render(request, 'rango/category.html', context_dict)
