from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max
from accounts.models import User
from jobs.models import Job

from .models import Conversation, Message
from .forms import MessageForm

from django.db.models.functions import Coalesce

@login_required
def inbox_view(request):
    """List all conversations for the current user."""
    # Get conversations, order by latest message
    qs = request.user.conversations.annotate(
        latest_message_time=Coalesce(Max('messages__created_at'), 'updated_at')
    ).order_by('-latest_message_time').prefetch_related('participants', 'messages')

    conversations = list(qs)
    for conv in conversations:
        conv.other_participant = conv.get_other_participant(request.user)
        conv.unread_count = conv.unread_count_for_user(request.user)

    context = {
        'conversations': conversations,
    }
    return render(request, 'messaging/inbox.html', context)


@login_required
def conversation_view(request, pk):
    """View a specific conversation and reply."""
    conversation = get_object_or_404(Conversation, pk=pk)

    # Ensure user is a participant
    if request.user not in conversation.participants.all():
        messages.error(request, 'You do not have permission to view this conversation.')
        return redirect('messaging:inbox')

    # Mark unread messages as read
    conversation.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Update conversation timestamp
            conversation.save() # triggers auto_now=True
            
            return redirect('messaging:conversation', pk=conversation.pk)
    else:
        form = MessageForm()

    context = {
        'conversation': conversation,
        'other_user': conversation.get_other_participant(request.user),
        'form': form,
    }
    return render(request, 'messaging/conversation.html', context)


@login_required
def start_conversation_view(request, username):
    """Start a new conversation or redirect to existing one."""
    other_user = get_object_or_404(User, username=username)
    
    if request.user == other_user:
        messages.warning(request, "You cannot message yourself.")
        return redirect('core:home')

    job_id = request.GET.get('job')
    job = None
    if job_id:
        try:
            job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            pass

    # Check if a conversation already exists between these two users (with this job context)
    # If job is provided, look for that specific job context.
    # Otherwise look for a general conversation without job context.
    conversations = Conversation.objects.filter(participants=request.user).filter(participants=other_user).distinct()
    if job:
        existing_conversation = conversations.filter(job=job).first()
    else:
        existing_conversation = conversations.filter(job__isnull=True).first()

    if existing_conversation:
        return redirect('messaging:conversation', pk=existing_conversation.pk)

    # Create new conversation
    conversation = Conversation.objects.create(job=job)
    conversation.participants.add(request.user, other_user)

    return redirect('messaging:conversation', pk=conversation.pk)


@login_required
def unread_count_api(request):
    """Phase 8: JSON API — returns total unread message count for the current user."""
    from django.http import JsonResponse
    count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False
    ).exclude(sender=request.user).count()
    return JsonResponse({'unread': count})
