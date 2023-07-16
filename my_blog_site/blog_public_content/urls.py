from django.urls import path
from . import views

urlpatterns = [
	path('', views.home, name='home'),
	path('about/', views.about, name='about'),
	path('signin/', views.sign_in, name='sign_in'),
	path('signup/', views.sign_up, name='sign_up'),
	path('createblog/', views.AddPostView.as_view(), name='create_blog'),
	path('updateblog/<int:pk>', views.UpdatePostView.as_view(), name='updateblog'),
	path('logout/', views.logout, name='logout'),
	path('contact/', views.contact, name='contact'),
	path('listarticles/<str:article>/', views.list_articles, name='listarticles'),
	path('myarticles/', views.MyArticles.as_view(), name='myarticles'),
	path('delete_article/', views.delete_article, name='delete_article'),
	path('like/<int:pk>', views.like_view, name='likeview'),
	path('activate/<uidb64>/<token>', views.VerifiationView.as_view(), name='activate'),
	path('check-email', views.check_email, name='check_valid_email'),
	path('set-new-password/<uidb64>/<token>', views.CompletePasswordReset.as_view(), name='reset-password'),
	path('markdown-view', views.AddPostViewMarkdown.as_view(), name='create-blog-markdown'),
	path('readmore/<int:pk>', views.ArticleDetailView.as_view(), name='read-more'),

]
