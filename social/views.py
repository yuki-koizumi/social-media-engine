from django.shortcuts import render
from django.shortcuts import get_object_or_404

from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.views import generic

from django.db.models import Q

# Create your views here.

from .forms import TweetUploadForm, VolunteerTaskUpdateForm
from .models import Tweet, VerificationTask, FirstresponderTask

from .demo import create_demo_data

class CrowdListView(generic.ListView):
    model = Tweet
    paginate_by = 200
    template_name = 'social/crowd_list.html'
    mode = 'production'

    def get_queryset(self):
        query = (Q(relevance1_score__gte = 0.5)
                 & Q(is_volunteer_verified = False)
                 & Q(firstresponder_status = -1))
        return Tweet.objects.filter(query).order_by('-relevance1_score')

class VolunteerListView(generic.ListView):
    model = Tweet
    paginate_by = 100
    template_name = 'social/volunteer_list.html'

    def get_queryset(self):
        query = (Q(firstresponder_status = -1)
                 & Q(is_volunteer_verified = False)
                 & Q(relevance1_score__gte = 0.7)
                 & Q(firsthand_result__in = [1, 2])
                 & Q(firstresponder_status = -1))
        return Tweet.objects.filter(query).distinct().order_by('-rescue1_score')

class FirstresponderListView(generic.ListView):
    model = Tweet
    paginate_by = 100
    template_name = 'social/firstresponder_list.html'

    def get_queryset(self):
        query = (Q(firstresponder_status = -1)
                 & ((Q(is_volunteer_verified = True)
                     & Q(verification_result = 0)
                     & Q(verification_status = 0))
                    | (Q(firsthand_result__in = [1, 2])
                       & Q(relevance1_score__gte = 0.8)
                       & Q(rescue1_score__gte = 0.8)
                       & Q(address_type = 1))))
        qs = Tweet.objects.filter(query).order_by('rescue1_score').reverse()
        return qs

class FirstresponderResolvedListView(generic.ListView):
    model = Tweet
    paginate_by = 100
    template_name = 'social/firstresponder_resolved.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resolved'] = True
        return context

    def get_queryset(self):
        query = Q(firstresponder_status = 1)
        qs = Tweet.objects.filter(query).order_by('rescue1_score').reverse()
        return qs

class FirstresponderDismissedListView(generic.ListView):
    model = Tweet
    paginate_by = 100
    template_name = 'social/firstresponder_resolved.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resolved'] = False
        return context

    def get_queryset(self):
        query = Q(firstresponder_status = 2)
        qs = Tweet.objects.filter(query).order_by('rescue1_score').reverse()
        return qs

class TweetDetailView(generic.DetailView):
    model = Tweet
    context_object_name = 'tweet'
    template_name = 'social/tweet_detail.html'

class VolunteerTweetDetailView(generic.DetailView):
    model = Tweet
    context_object_name = 'tweet'
    template_name = 'social/volunteer_detail.html'

def crowd_update_tweet(request, pk):
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        print(request.POST)

        tweet = Tweet.objects.get(pk=pk)

        key = f'relevant-{pk}'
        if key in request.POST:
            if request.POST[key] == '1':
                tweet.relevance1_reaction += 1
            else:
                tweet.relevance0_reaction += 1

        key = f'firsthand-{pk}'
        if key in request.POST:
            if request.POST[key] == '1':
                tweet.firsthand1_reaction += 1
            elif request.POST[key] == '2':
                tweet.firsthand2_reaction += 1
            else:
                tweet.firsthand0_reaction += 1

        key = f'rescue-{pk}'
        if key in request.POST:
            if request.POST[key] == '1':
                tweet.rescue1_reaction += 1
            else:
                tweet.rescue0_reaction += 1

        key = f'inferred-address-{pk}'
        if key in request.POST:
            addr = request.POST[key]
            if addr:
                tweet.inferred_address.append(addr)

        key = f'urgent-{pk}'
        if key in request.POST:
            tweet.urgent_reaction += 1

        key = f'doubtful-{pk}'
        if key in request.POST:
            tweet.doubtful_reaction += 1

        tweet.save()

    return HttpResponse('OK')

def creating_demo_db(request):
    create_demo_data('result.txt')
    return render(request, 'social/import_result.html', { 'status': 'OK' })

def import_result(request, status):
    return render(request, 'social/import_result.html', { 'status': status })

class TweetImportView(generic.FormView):
    template_name = 'social/upload_tweet.html'
    form_class = TweetUploadForm
    success_url = reverse_lazy('social:import_result', args=('OK',))

    def form_valid(self, form):
        form.import_tweet()
        return super().form_valid(form)

def create_verification_task(request, tweet_id):
    v = VerificationTask.objects.create(tweet_id = tweet_id)
    return HttpResponseRedirect(reverse('social:volunteer_update', args=(v.id, tweet_id)))

class FirstresponderStartWorkingView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        tweet_id = self.kwargs['tweet_id']
        self.execute(tweet_id)
        return reverse_lazy('social:firstresponder_working', args=[self.kwargs['tweet_id']])

    def execute(self, tweet_id):
        t = Tweet.objects.get(pk=tweet_id)
        t.firstresponder_status = 0
        t.save()
        return

class FirstresponderResolveView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        tweet_id = self.kwargs['tweet_id']
        self.execute(tweet_id)
        return reverse_lazy('social:firstresponder')

    def execute(self, tweet_id):
        t = Tweet.objects.get(pk=tweet_id)
        t.firstresponder_status = 1
        t.save()
        return

class FirstresponderDismissTweetView(generic.RedirectView):
    permanent = False
    url = reverse_lazy('social:firstresponder')
    def get_redirect_url(self, *args, **kwargs):
        tweet_id = self.kwargs['tweet_id']
        self.dismiss_tweet(tweet_id)
        return super().get_redirect_url(*args, **kwargs)

    def dismiss_tweet(self, tweet_id):
        t = Tweet.objects.get(pk=tweet_id)
        t.firstresponder_status = 2
        t.save()
        return

class FirstresponderWorkingView(generic.DetailView):
    model = Tweet
    context_object_name = 'tweet'
    template_name = 'social/firstresponder_working.html'

class VolunteerTaskUpdateView(generic.UpdateView):
    model = VerificationTask
    template_name = 'social/volunteer_work_update_form.html'
    # fields = ('result', 'status', 'address', 'note', 'image')
    form_class = VolunteerTaskUpdateForm
    success_url = reverse_lazy('social:volunteer')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['tweet'] = Tweet.objects.get(pk=self.kwargs['tweet_id'])
        # context['tweet'] = self.object.tweet
        return context

    def form_valid(self, form):
        self.object.is_completed = True
        self.object.save()

        if self.object.result != 2: # not "unsure" selection
            # t = Tweet.objects.get(pk=self.kwargs['tweet_id'])
            t = self.object.tweet
            t.verification_result  = self.object.result
            t.verification_status  = self.object.status
            t.verification_note    = self.object.note
            t.verification_address = self.object.address
            t.is_volunteer_verified = True
            t.save()
            
        return super().form_valid(form)
