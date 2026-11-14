# This file holds the logic for input validation

from django.core.exceptions import ValidationError

def validate_photo_size(file_obj):
    max_size_bytes = 10 * 1024 * 1024 # 10 MB
    if file_obj.size > max_size_bytes:
        raise ValidationError(
            "The uploaded photograph exceeds the maximum allowed size of 10 MB."
        )

def validate_bio_wordcount(value):
    words = value.strip().split()
    
    if len(words) > 50:
        raise ValidationError(
            f"Your biography cannot exceed 50 words (currently {len(words)} words)."
        ) 