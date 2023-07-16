import json
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .decorators import my_login_required
from django.views.generic import CreateView, UpdateView, DetailView
from django.views.generic.list import ListView
from .models import Subjects, BlogContent
from .forms import PostForm
from django.utils.decorators import method_decorator
from collections import defaultdict
from django.conf import settings 
from django.core.mail import send_mail 
from django.views.generic import View
from django.urls import reverse

from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site

from .utils import token_generator
from .const_manual_content import article_const
import threading
from threading import Thread
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    """
       root view of the website
    """
    logged_user = ''
    if 'username' in request.session:
        logged_user = request.session['username']
    content = BlogContent.objects.all().values().order_by('-updated_date')[:5]
    context= {}
    likes_list, markdown_list = [], []
    for record in BlogContent.objects.filter():
        total_likes = record.total_likes() 
        likes_list.append({'total_likes':total_likes, 'id':record.id})
        if record.markdown_description:
            markdown_list.append({'marked_content':record.formatted_markdown, 'id':record.id})

    d = defaultdict(dict)
    for l in (content, likes_list):
        for elem in l:
            d[elem['id']].update(elem)

    for l in (content, markdown_list):
        for elem in l:
            d[elem['id']].update(elem)
    l3 = d.values()
    content = l3
    '''
    below code is a test on pagination
    '''
    page = request.GET.get('page', 1)
    paginator = Paginator(list(content), 2)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    '''
    Pagination Test ends
    '''
    return render(request, 'index.html', {'content':articles, 'logged_user':logged_user})


def sign_up(request):
    """
        view for sign_up
    """
    first_name = request.POST.get('FirstName')
    user_name = request.POST.get('user_name')
    password = request.POST.get('password')
    email = request.POST.get('Email')
    try:
        user = User.objects.create_user(username=user_name,
                                        password=password,
                                        email=email, 
                                        first_name=first_name,
                                        is_active=False)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('activate', kwargs={
            'uidb64':uidb64, 'token':token_generator.make_token(user)})
        activate_url = domain+link
        subject = 'Welcome to Tech Trends'
        message = f'Hi {user.username}, thank you for registering in Tech Trends. Please click below link to verify mail.\n' + activate_url
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [user.email, ] 
        EmailThread(subject, message, email_from, recipient_list).start()
        #send_mail( subject, message, email_from, recipient_list ) 
        return HttpResponse(json.dumps({'status': True}),
                        content_type="application/json")
    except Exception as e:
        return HttpResponse(json.dumps({'status': False}),
                        content_type="application/json")

class EmailThread(threading.Thread):
    def __init__(self, subject, message, email_from, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.message = message
        self.email_from = email_from
        threading.Thread.__init__(self)

    def run (self):
        send_mail(self.subject, self.message, self.email_from, self.recipient_list ) 

class VerifiationView(View):
    def get(self,request,uidb64,token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if user.is_active:
                pass
            else:
                user.is_active = True
                user.save()
        except Exception as e:
            pass
        return redirect('home')


def sign_in(request):
    """
        view for sign in
    """
    if request.is_ajax():
        user_name = request.POST.get('user_name')
        password = request.POST.get('password')
        center_sign_in = request.POST.get('centralSignin')
        try:
            if User.objects.get(username=user_name, is_active=False):
                return HttpResponse(json.dumps({'status': 'inactive'}),
                        content_type="application/json") 
        except User.DoesNotExist:
            login_obj = authenticate(username=user_name, password=password)
            if login_obj is not None:
                request.session['username'] = user_name
                if center_sign_in:
                    return HttpResponse(json.dumps({'status': 'centerTrue'}),
                                content_type="application/json")
                else:
                    return HttpResponse(json.dumps({'status': True}),
                                content_type="application/json")
            else:
                return HttpResponse(json.dumps({'status': False}),
                            content_type="application/json")
        


from django.urls import resolve
@method_decorator(my_login_required, name='dispatch')
class AddPostView(CreateView):
    model = BlogContent
    form_class = PostForm
    def get_initial(self):
        initial = {}
        current_url = resolve(self.request.path_info).url_name
        initial['url']=current_url
        return initial
    template_name = 'create_blog.html'

@method_decorator(my_login_required, name='dispatch')
class AddPostViewMarkdown(CreateView):
    model = BlogContent
    form_class = PostForm
    def get_initial(self):
        initial = {}
        current_url = resolve(self.request.path_info).url_name
        initial['url']=current_url
        return initial
    template_name = 'create_blog_markdown.html'

@method_decorator(my_login_required, name='dispatch')
class UpdatePostView(UpdateView):
    model = BlogContent
    form_class = PostForm
    def get_initial(self):
        initial = {}
        current_url = resolve(self.request.path_info).url_name
        post_id = resolve(self.request.path_info).kwargs['pk']
        initial['url']=current_url
        initial['post_id']=post_id
        return initial
    template_name = 'update_blog.html'

@method_decorator(my_login_required, name='dispatch')
class MyArticles(ListView):
    model = BlogContent
    template_name = 'my_articles.html'  

    def get_queryset(self, *args, **kwargs): 
        query_set = super(MyArticles, self).get_queryset(*args, **kwargs) 
        query_set = query_set.filter(created_by__iexact=User.objects.get(
            username=self.request.user.username).first_name)
        # query_set = query_set.filter(created_by__iexact=User.objects.get(
        #     username=self.request.user.username))
        return query_set
  

@my_login_required
def delete_article(request):
    article_id = request.POST.get('blog_id')
    try:
        BlogContent.objects.get(id=article_id).delete()
        return HttpResponse(json.dumps({'status': True}),
                            content_type="application/json")
    except Exception as e:
        print(e)
        return HttpResponse(json.dumps({'status': False}),
                            content_type="application/json")


@my_login_required
def logout(request):
    if 'username' in request.session:
        del request.session['username']
    return HttpResponse(json.dumps({'status': True}),
                        content_type="application/json")

def about(request):
    logged_user = ''
    if 'username' in request.session:
        logged_user = request.session['username']
    return render(request, "about.html", {'logged_user':logged_user})
    
def contact(request):
    logged_user = ''
    if 'username' in request.session:
        logged_user = request.session['username']
    return render(request, "contact.html", {'logged_user':logged_user})

def list_articles(request, article):
    """
       Need to work
    """
    logged_user = ''
    if 'username' in request.session:
        logged_user = request.session['username']
    article = article
    if article=='dataeng':
        content = BlogContent.objects.filter(subject=(
            Subjects.objects.get(
                subject='Data Engineering'))).order_by('-updated_date')[:5]
    if article=='web':
        content = BlogContent.objects.filter(subject=(
            Subjects.objects.get(
                subject='Web Development'))).order_by('-updated_date')[:5]
    if article=='mobile':
        content = BlogContent.objects.filter(subject=(
            Subjects.objects.get(
                subject='Mobile Development'))).order_by('-updated_date')[:5]
    if article=='cloud':
        content = BlogContent.objects.filter(subject=(
            Subjects.objects.get(
                subject='Cloud Technologies'))).order_by('-updated_date')[:5]
    '''
    below code is a test on pagination
    '''
    page = request.GET.get('page', 1)
    paginator = Paginator(content, 1)
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    '''
    Pagination Test ends
    '''
    return render(request, 'index.html', {'content':articles, 'logged_user':logged_user})


def like_view(request, pk):
    post = get_object_or_404(BlogContent, id=pk)
    post.likes.add(User.objects.get(username=request.session['username']).id)
    return HttpResponse(json.dumps({'status': True}),
                            content_type="application/json")


def check_email(request):
    #Complete the Function
    email = request.POST.get('email')
    try:
        user = User.objects.get(email=email)
        email = user.email
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        domain = get_current_site(request).domain
        link = reverse('reset-password', kwargs={
            'uidb64':uidb64, 'token':PasswordResetTokenGenerator().make_token(user)})
        reset_url = domain+link
        subject = 'Reset password'
        message = f'Hi {user.username}, Please click on below link to reset the password\n' + reset_url
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [user.email, ] 
        EmailThread(subject, message, email_from, recipient_list).start()

        return HttpResponse(json.dumps({'status': True}),
                            content_type="application/json")
    except  Exception as e:
        return HttpResponse(json.dumps({'status': False}),
                            content_type="application/json")

class CompletePasswordReset(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64':uidb64,
            'token':token
        }
        user_id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.add_message(request, messages.INFO, "password link is already used!!")
        return render(request, 'set_new_password.html', context)

    def post(self, request, uidb64, token):
        password = request.POST.get('password')
        user_id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        user.set_password(password)
        user.save()
        return HttpResponse(json.dumps({'status': True}),
                            content_type="application/json")



class ArticleDetailView(DetailView):
    model = BlogContent
    template_name = 'blogcontent_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        logged_user = ''
        if 'username' in self.request.session:
            logged_user = self.request.session['username']
        context['logged_user'] = logged_user

        return context