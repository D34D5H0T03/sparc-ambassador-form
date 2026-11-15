from django.conf import settings

# Byte Conversion & Validation Limits
BYTES_PER_MB = 1024 * 1024
MAX_PHOTO_SIZE_MB = getattr(settings, "MAX_PHOTO_SIZE_MB", 10)
MAX_PHOTO_SIZE_BYTES = MAX_PHOTO_SIZE_MB * BYTES_PER_MB
MAX_BIO_WORD_COUNT = getattr(settings, "MAX_BIO_WORD_COUNT", 50)
BIO_WARNING_WORD_THRESHOLD = max(1, MAX_BIO_WORD_COUNT - 8)

# Photo Upload Rules
PHOTO_UPLOAD_SUBDIR = "ambassador_photos"
ALLOWED_PHOTO_EXTENSIONS = ["jpg", "jpeg", "png"]
ALLOWED_PHOTO_MIME_TYPES = ["image/jpeg", "image/png"]
ALLOWED_PHOTO_ACCEPT_ATTR = ".jpg,.jpeg,.png,image/jpeg,image/png"

# Database Field Max Lengths
MAX_NAME_LENGTH = 150
MAX_PHONE_LENGTH = 30
MAX_CHOICE_LENGTH = 30
MAX_INSTITUTION_LENGTH = 200
MAX_DEPARTMENT_LENGTH = 150
MAX_ID_LENGTH = 100

# Form Widget Dimensions
BIO_TEXTAREA_ROWS = 4
MOTIVATION_TEXTAREA_ROWS = 6

# Outbound Mail Campaign Identifier
CAMPAIGN_APPLICATION_RECEIVED = "ambassador_received"

# Exact Choices from SPARC Ambassador Application 2026 Specification
GENDER_CHOICES = [
    ("male", "Male"),
    ("female", "Female"),
]

STUDY_YEAR_CHOICES = [
    ("1st", "1st Year"),
    ("2nd", "2nd Year"),
    ("3rd", "3rd Year"),
    ("4th", "4th Year"),
    ("postgraduate", "Postgraduate"),
]

IEEE_GRADE_CHOICES = [
    ("student", "Student Member"),
    ("graduate", "Graduate Student Member"),
    ("member", "Member"),
    ("other", "Other"),
]

ACTIVITY_CHOICES = [
    ("social_media_posts", "Social media posts and stories"),
    ("short_videos", "Making short videos"),
    ("campus_posters", "Hanging posters on campus"),
    ("student_outreach", "Talking to students and societies"),
    ("writing_captions", "Writing quotes and captions"),
    ("campus_sessions", "Organizing campus sessions"),
]

REFERRAL_SOURCE_CHOICES = [
    ("social_media", "Social media"),
    ("friend", "Friend"),
    ("ieee_branch", "IEEE branch"),
    ("university", "University"),
    ("other", "Other"),
]