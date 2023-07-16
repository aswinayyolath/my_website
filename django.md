How to use Django Markdownx

### What is Markdown
Markdown is a plain text formatting syntax aimed at making writing for the internet easier. Markdown is widely used in blogging, instant messaging, online forums, collaborative software, documentation pages, and readme files.  It is an alternative to WYSIWYG (what you see is what you get) editors, which use rich text that later gets converted to proper HTML.

###Markdown packages in Django
As you might already know Django is a high-level Python web framework that enables the rapid development of secure and maintainable websites. Django has a rich set of packages that helps us to implement markdowns in our websites. To get a complete understanding of all the packages available take a look at them [here](https://djangopackages.org/grids/g/markdown/)

###django-markdownx 
Here we are going to look at a package called Django MarkdownX. According to the official documentation, Django MarkdownX is a comprehensive Markdown plugin built for Django. You can refer more to its feature [here](https://neutronx.github.io/django-markdownx/).

###Installation
To install the latest version of Django MarkdownX you can use the below command
```
python3 -m pip install django-markdownx
```
###Getting Started
After successful installation, we need to add `markdownx` to the `INSTALLED_APPS` in `settings.py`
```
INSTALLED_APPS = [
    # [...]
    'markdownx'
]
```
The next thing we need to do is to add the MarkdownX URL patterns to your urls.py.
```
urlpatterns = [
    # [...]
    path('markdownx/', include('markdownx.urls')),
]
```
In the models.py file create a model(table in the database) with the field type MarkdownxField().
```
from django.db import models
from markdownx.utils import markdownify
from markdownx.models import MarkdownxField

class MarkedDownExample(models.Model):
    title = models.CharField(max_length=200)
    markdown_description = MarkdownxField()
    
    # Create a property that returns the markdown	
    @property
    def formatted_markdown(self):
        return markdownify(self.markdown_description)	

    def get_absolute_url(self):
        return reverse('markdown-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title
```
Your forms.py should look something like this
```
from django import forms
from .models import MarkedDownExample

class MarkedDownExampleForm(forms.ModelForm):
    class Meta:
        
        model = MarkedDownExample
        fields = '__all__'
```
Now in your views.py, you can create a DetailView (can be any view, even a function-based view) to pass data to your template file as below.
```
from django.views.generic import DetailView
from .models import MarkedDownExample
from .forms import MarkedDownExampleForm

class MarkdownDetailView(DetailView):
    model = MarkedDownExample
```
Finally in your template file you can render the Marked content as below
```
<div class="container">
    <h1>{{ markeddownexample.title }}</h1>
    <p>{{ markeddownexample.formatted_markdown|safe }}</p>
</div>
```
You can even alter the style of displayed content by adding CSS to the rendered HTML. for example below CSS will modify the code segment and image displayed on your website. 
```
<style>
pre {
  	background: #2e2f2f;
	border-radius: 5px;
	padding: 10px;
}
img{
	width: 1000px;
	padding: 10px;
}
</style>
```
