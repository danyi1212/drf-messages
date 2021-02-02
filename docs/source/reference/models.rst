
Models
======

Message
-------

Fields:

:id: Integer, ID.
:session: Session, related sessions.Session object.
:message: String (up to 1024), the actual text of the message.
:level: Integer, describing the type of the message.
:extra_tags.all: List, all related drf_messages.MessageTag objects.
:view: String (up to 64), the view where the message was submitted from.
:read_at: Date (with time), when the message was read (or null).
:created: Date (with time), when the message was crated

Properties:

:level_tag: String, describing the level of the message


MessageTag
----------

Fields:

:id: Integer, ID.
:message: Message, related drf_messages.Message object.
:text: String (up to 128), custom tags for the message.