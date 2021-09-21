from django.urls import path
from django.views import generic
from . import views

app_name = 'social'

urlpatterns = [
    path('', generic.TemplateView.as_view(template_name = 'social/index.html'), name='index'),

    # crowd volunteers' view
    path('crowd/', views.CrowdListView.as_view(), name='crowd'),
    path('crowd/verbose/', views.CrowdListView.as_view(mode='verbose'), name='crowd_verbose'),
    path('crowd/<int:pk>/update/', views.crowd_update_tweet, name='crowd_update'),

    # on-site volunteers' view
    path('volunteer/', views.VolunteerListView.as_view(), name='volunteer'),
    path('volunteer/<int:pk>/', views.VolunteerTweetDetailView.as_view(), name='volunteer_detail'),
    path('volunteer/task_create/<int:tweet_id>/', views.create_verification_task, name='volunteer_task_create'),
    path('volunteer/task/<int:pk>/<int:tweet_id>', views.VolunteerTaskUpdateView.as_view(), name='volunteer_update'),

    # firstresponders' view
    path('firstresponder/', views.FirstresponderListView.as_view(), name='firstresponder'),
    path('firstresponder/resolved/', views.FirstresponderResolvedListView.as_view(), name='firstresponder_resolved_list'),
    path('firstresponder/dismissed/', views.FirstresponderDismissedListView.as_view(), name='firstresponder_dismissed_list'),
    path('firstresponder/dismiss/<int:tweet_id>', views.FirstresponderDismissTweetView.as_view(), name='firstresponder_dismiss'),
    path('firstresponder/start_working/<int:tweet_id>', views.FirstresponderStartWorkingView.as_view(), name='firstresponder_start_working'),
    path('firstresponder/resolve/<int:tweet_id>', views.FirstresponderResolveView.as_view(), name='firstresponder_resolved'),
    path('firstresponder/working/<int:pk>', views.FirstresponderWorkingView.as_view(), name='firstresponder_working'),

    # management
    path('tweet/<int:pk>/', views.TweetDetailView.as_view(), name='tweet_detail'),
    path('upload_tweet/', views.TweetImportView.as_view(), name='upload_tweet'),
    path('create_demo_db/', views.creating_demo_db, name='creating_demo_db'),
    path('import_result/<slug:status>/', views.import_result, name='import_result'),

]
