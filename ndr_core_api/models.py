from django.db import models
from django.urls import reverse, NoReverseMatch


class NdrCorePage(models.Model):
    name = models.CharField(max_length=200,
                            help_text='The name of the page, e.g. the page\'s title')

    label = models.CharField(max_length=200,
                             help_text='The label of the page, e.g. the page\'s navigation label')

    view_name = models.CharField(max_length=200,
                                 help_text='The name of the view to display')

    nav_icon = models.CharField(max_length=200,
                                help_text='The fontawesome nav icon (leave blank if none)',
                                blank=True)

    index = models.IntegerField(default=0)

    def url(self):
        try:
            reverse_url = reverse(f'main:{self.view_name}')
        except NoReverseMatch:
            reverse_url = '#'

        return reverse_url

    def __str__(self):
        return f"{self.name}: {self.label}"
