from django import forms

from .models import *


class ProblemTagForm(forms.ModelForm):
    class Meta:
        model = ProblemTag
        fields = []


class ProblemCommentForm(forms.ModelForm):
    class Meta:
        model = ProblemComment
        fields = ['content', 'parent']


class ProblemMemoForm(forms.ModelForm):
    class Meta:
        model = ProblemMemo
        fields = ['content']


# class ProblemCollectionForm(forms.ModelForm):
#     class Meta:
#         model = ProblemCollectionItem
#         fields = ['title']
