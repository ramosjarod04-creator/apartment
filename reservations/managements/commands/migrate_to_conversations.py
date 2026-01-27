from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import Q

class Command(BaseCommand):
    help = 'Migrate messages to conversation system'

    def handle(self, *args, **kwargs):
        from yourapp.models import Message, Conversation
        
        # Get messages without conversations
        orphaned_messages = Message.objects.filter(conversation__isnull=True)
        
        if not orphaned_messages.exists():
            self.stdout.write(self.style.SUCCESS('No messages to migrate!'))
            return
        
        # Group by sender-recipient pairs
        user_pairs = set()
        
        for msg in orphaned_messages:
            # Get original sender and recipient from related_name
            # Since we don't have recipient field anymore, we need to handle old data
            
            # If old messages still have recipient field
            if hasattr(msg, 'recipient'):
                pair = tuple(sorted([msg.sender.id, msg.recipient.id]))
                user_pairs.add(pair)
        
        # Create conversations for each pair
        for pair in user_pairs:
            user1_id, user2_id = pair
            user1 = User.objects.get(id=user1_id)
            user2 = User.objects.get(id=user2_id)
            
            # Create conversation
            conversation = Conversation.objects.create(
                subject=f"Conversation with {user2.username}"
            )
            conversation.participants.add(user1, user2)
            
            # Link messages to this conversation
            messages_to_update = orphaned_messages.filter(
                Q(sender=user1) | Q(sender=user2)
            )
            
            messages_to_update.update(conversation=conversation)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created conversation between {user1.username} and {user2.username}'
                )
            )
        
        self.stdout.write(self.style.SUCCESS('Migration complete!'))