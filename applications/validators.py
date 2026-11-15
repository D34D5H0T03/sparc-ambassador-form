from django.core.exceptions import ValidationError

from .constants import (
    MAX_BIO_WORD_COUNT,
    MAX_PHOTO_SIZE_BYTES,
    MAX_PHOTO_SIZE_MB,
)


def validate_photo_size(file_obj):
    if file_obj.size > MAX_PHOTO_SIZE_BYTES:
        raise ValidationError(
            f"The uploaded photograph exceeds the maximum allowed size of {MAX_PHOTO_SIZE_MB} MB."
        )


def validate_bio_word_count(value):
    words = value.strip().split()
    if len(words) > MAX_BIO_WORD_COUNT:
        raise ValidationError(
            f"Your biography cannot exceed {MAX_BIO_WORD_COUNT} words (currently {len(words)} words)."
        )