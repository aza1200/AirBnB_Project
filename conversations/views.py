from django.db.models import Q
from django.shortcuts import render,redirect,reverse
from django.views.generic import DetailView
from users import models as user_models
from . import models

def go_conversation(request, a_pk, b_pk):
    try:
        user_one = user_models.User.objects.get(pk=a_pk)
    except user_models.User.DoesNotExist:
        user_one = None
    try:
        user_two = user_models.User.objects.get(pk=b_pk)
    except user_models.User.DoesNotExist:
        user_two = None

    if user_one is not None and user_two is not None:
        conversation = models.Conversation.objects.filter(participants=user_one).filter(
        participants=user_two)

    if conversation.count() == 0:
        conversation = models.Conversation.objects.create()
        conversation.participants.add(user_one, user_two)
        conversation = models.Conversation.objects.filter(
        participants=user_one
        ).filter(participants=user_two)

    return redirect(reverse("conversations:detail", kwargs={"pk": conversation[0].pk}))


class ConversationDetailView(DetailView):

    model = models.Conversation