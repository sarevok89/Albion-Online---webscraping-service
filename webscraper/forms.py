from django import forms


class WebscraperForm(forms.Form):
    fight_name = forms.CharField(label="Fight name:", max_length=100)
    urls = forms.CharField(label="Paste your URLs below:", widget=forms.Textarea(attrs={'rows': 8}))
