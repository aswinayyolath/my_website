from django import forms
from .models import BlogContent
from django.utils.translation import gettext_lazy as _

class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial = kwargs.pop("initial")
        initial = self.initial
        self.label_suffix = ""
        super(PostForm, self).__init__(*args, **kwargs)
        try:
            if initial['url'] == 'create_blog':
                del self.fields['markdown_description']
            if initial['url'] == 'create-blog-markdown':
                del self.fields['description']
            if initial['url'] == 'updateblog':
                if BlogContent.objects.get(id=initial['post_id']).description:
                    del self.fields['markdown_description']
                if BlogContent.objects.get(id=initial['post_id']).markdown_description:
                    del self.fields['description']
        except KeyError:
            pass

    class Meta:
        model = BlogContent
        fields = ('title', 'subject', 'markdown_description', 'description',
                  'blog_card_image', 'created_by')
        labels = {
        "title":  _('TITLE'),
        "subject": _('SUBJECT'),
        "description": _('DESCRIPTION'),
        "markdown_description": _('DESCRIPTION'),
        "blog_card_image": _('CARD IMAGE')
        }
        widgets = {
        'title':forms.TextInput(attrs={
            'class':'form-control','placeholder':'Enter BLog Title', "id":"title"
            }),
        'subject':forms.Select(attrs={
            'class':'form-control'
            }),
        'description':forms.Textarea(attrs={
            'class':'form-control'
            }),
        'markdown_description':forms.Textarea(attrs={
            'class':'form-control'
            }),
        'created_by':forms.TextInput(attrs={
            'class':'form-control','value':'','id':'createdby','type':'hidden'
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        if not (cleaned_data.get('markdown_description') or cleaned_data.get('description')):
            self.add_error('description', 'Must provide Description for your blog!!!!')
            return cleaned_data