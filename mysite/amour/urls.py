from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'amour.views.index'),
    url(r'^results$', 'amour.views.results'),
)
