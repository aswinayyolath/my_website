from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from markdownx.utils import markdownify
from markdownx.models import MarkdownxField

class Subjects(models.Model):
    subject = models.CharField(max_length=100)

    class Meta:
        db_table = 'Subjects'

    def __str__(self):
        return self.subject

class BlogContent(models.Model):
    title = models.CharField(max_length=100)
    description = RichTextField(null=True, blank=True)
    markdown_description = MarkdownxField(null=True, blank=True)
    subject =  models.ForeignKey(Subjects, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=200)
    blog_card_image = models.ImageField()
    likes = models.ManyToManyField(User, related_name='blog_post')

    class Meta:
        db_table = 'BlogContent'

    def total_likes(self):
        return self.likes.count()

    @property
    def formatted_markdown(self):
        return markdownify(self.markdown_description)
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('myarticles')
