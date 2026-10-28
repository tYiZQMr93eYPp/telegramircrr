from telethon.tl.custom import Message, MessageButton


def button_urls(message: Message) -> list[str]:
    """URLs of the message's buttons, read through Telethon's `MessageButton` so TL layer changes don't break us."""
    rows = message.buttons
    if rows is None and message.reply_markup:
        # `message.buttons` is None when Telethon can't resolve the chat/sender; `.url` doesn't need them.
        rows = [[MessageButton(None, b, None, None, message.id) for b in row.buttons]
                for row in message.reply_markup.rows]
    return [b.url for row in rows or [] for b in row if b.url]
