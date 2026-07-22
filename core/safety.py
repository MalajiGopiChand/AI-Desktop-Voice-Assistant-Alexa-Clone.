"""Safety gate — requires confirmation before destructive or sensitive actions."""

DANGEROUS_ACTIONS = {
    ("desktop_agent", "delete_file"),
    ("desktop_agent", "shutdown"),
    ("desktop_agent", "restart"),
    ("desktop_agent", "format"),
    ("comms_agent", "send_email"),
    ("comms_agent", "send_whatsapp"),
    ("comms_agent", "forward_email"),
    ("automation_agent", "purchase"),
}

CONFIRM_WORDS = {"yes", "yeah", "yep", "confirm", "do it", "go ahead", "proceed", "sure", "ok", "okay"}
DENY_WORDS = {"no", "nope", "cancel", "stop", "don't", "abort", "never mind", "nevermind"}


def requires_confirmation(agent_name, action):
    return (agent_name, action) in DANGEROUS_ACTIONS


def build_confirmation_prompt(agent_name, action, params):
    if action == "delete_file":
        path = params.get("path", "the file")
        return f"This will permanently delete {path}. Should I proceed?"
    if action == "send_whatsapp":
        contact = params.get("contact", "the contact")
        message = params.get("message", "")
        preview = message[:60] + ("..." if len(message) > 60 else "")
        return f"Send WhatsApp message to {contact}: '{preview}'. Confirm?"
    if action == "send_email":
        to = params.get("to", "recipient")
        subject = params.get("subject", "")
        return f"Send email to {to} with subject '{subject}'. Confirm?"
    if action in ("shutdown", "restart"):
        return f"This will {action} your computer. Are you sure?"
    return f"Confirm action: {agent_name}.{action}?"
