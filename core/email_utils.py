"""
core/email_utils.py — Phase 10 email notification helpers.

In development, set EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
in settings.py to see emails in the terminal instead of sending real ones.
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def _send(subject, template, context, recipient_email):
    """Internal helper — renders an HTML email and sends it."""
    if not recipient_email:
        return
    try:
        html_body = render_to_string(template, context)
        send_mail(
            subject=subject,
            message='',               # plain-text fallback (empty — HTML only)
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@suratpro.in'),
            recipient_list=[recipient_email],
            html_message=html_body,
            fail_silently=True,        # never crash the request
        )
    except Exception:
        pass  # silently ignore mail errors in all environments


# ── Public helpers ────────────────────────────────────────────────────────────

def email_new_proposal(proposal):
    """Notify the client that their job received a new proposal."""
    _send(
        subject=f'New Proposal on "{proposal.job.title}" — SuratPro',
        template='emails/new_proposal.html',
        context={'proposal': proposal, 'job': proposal.job},
        recipient_email=proposal.job.client.email,
    )


def email_proposal_accepted(proposal):
    """Notify the freelancer their proposal was accepted (contract created)."""
    _send(
        subject=f'🎉 Your Proposal Was Accepted — "{proposal.job.title}"',
        template='emails/proposal_accepted.html',
        context={'proposal': proposal, 'job': proposal.job},
        recipient_email=proposal.freelancer.email,
    )


def email_payment_received(contract, payment):
    """Notify the freelancer that payment was completed for their contract."""
    _send(
        subject=f'Payment Received — ₹{payment.amount} for "{contract.job.title}"',
        template='emails/payment_received.html',
        context={'contract': contract, 'payment': payment},
        recipient_email=contract.freelancer.email,
    )


def email_new_message(message):
    """Notify the other participant about a new message (if they have email)."""
    other_user = message.conversation.get_other_participant(message.sender)
    if not other_user:
        return
    _send(
        subject=f'New message from {message.sender.get_full_name() or message.sender.username} — SuratPro',
        template='emails/new_message.html',
        context={'message': message, 'sender': message.sender, 'recipient': other_user},
        recipient_email=other_user.email,
    )
