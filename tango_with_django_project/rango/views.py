from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page

def index(request):
  #return HttpResponse("Rango says hello world! <br/> <a href='/rango/about'>About</a>")
  categories_list = Category.objects.order_by('-likes')[:5]
  pages_list = Page.objects.order_by('-views')[:5]
  context_dict = {'categories': categories_list, 'pages': pages_list,
  }
  return render(request, 'rango/index.html', context_dict)

def about(request):
  context_dict = {'author': "Alexander Nedergaard, 2018207."}
  return render(request, 'rango/about.html', context_dict)
  #return HttpResponse("Rango says here is the about page. <br/> <i>This tutorial has been put together by Alexander Nedergaard, 2018207.</i> <br/> <a href='/rango'>Index</a>")

#def details(request):
 # categories_list = Category.objects.all()
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
  except Category.DoesNotExist:
    pass
  return render(request, 'rango/category.html', context_dict)

def what(request):
  context_dict = {}
  return render(request, 'rango/what.html', context_dict)
