from .models import Contact
from django.db.models import Q
from django.utils import timezone

def identify_logic(data):
    email = data.get("email")
    phone = data.get("phoneNumber")

    # Step 1: Fetch existing contacts matching either email or phoneNumber
    matching_contacts = Contact.objects.filter(
        Q(email=email) | Q(phoneNumber=phone)
    ).order_by('createdAt')

    # Step 2: If no matches, create a new primary contact
    if not matching_contacts.exists():
        new_contact = Contact.objects.create(
            email=email,
            phoneNumber=phone,
            linkPrecedence='primary'
        )
        return {
            "contact": {
                "primaryContactId": new_contact.id,
                "emails": [email] if email else [],
                "phoneNumbers": [phone] if phone else [],
                "secondaryContactIds": []
            }
        }

    # Step 3: There are matches — find all related contacts
    contact_ids = set(matching_contacts.values_list('id', flat=True))
    linked_ids = set(matching_contacts.exclude(linkedId=None).values_list('linkedId', flat=True))

    all_related_ids = contact_ids.union(linked_ids)
    all_related_contacts = Contact.objects.filter(
        Q(id__in=all_related_ids) | Q(linkedId__in=all_related_ids)
    ).order_by('createdAt')

    # Step 4: Determine the primary contact (oldest one)
    primary_contact = None
    for contact in all_related_contacts:
        if contact.linkPrecedence == 'primary':
            if not primary_contact or contact.createdAt < primary_contact.createdAt:
                primary_contact = contact

    # Step 5: Ensure all others are linked to primary
    for contact in all_related_contacts:
        if contact.id != primary_contact.id and contact.linkPrecedence != 'secondary':
            contact.linkPrecedence = 'secondary'
            contact.linkedId = primary_contact.id
            contact.updatedAt = timezone.now()
            contact.save()

    # Step 6: If incoming email or phone is new, create secondary
    all_emails = set(filter(None, all_related_contacts.values_list('email', flat=True)))
    all_phones = set(filter(None, all_related_contacts.values_list('phoneNumber', flat=True)))

    new_secondary = None
    if (email and email not in all_emails) or (phone and phone not in all_phones):
        new_secondary = Contact.objects.create(
            email=email,
            phoneNumber=phone,
            linkPrecedence='secondary',
            linkedId=primary_contact.id
        )

    # Step 7: Prepare final response
    final_contacts = Contact.objects.filter(
        Q(id=primary_contact.id) | Q(linkedId=primary_contact.id)
    )

    emails = []
    phones = []
    secondary_ids = []

    for c in final_contacts:
        if c.email and c.email not in emails:
            emails.append(c.email)
        if c.phoneNumber and c.phoneNumber not in phones:
            phones.append(c.phoneNumber)
        if c.id != primary_contact.id:
            secondary_ids.append(c.id)

    return {
        "contact": {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phones,
            "secondaryContactIds": secondary_ids
        }
    }
