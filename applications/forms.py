from django import forms
from .models import AmbassadorApplications

ACTIVITY_CHOICES = [
    ("social_media", "Social Media Promotion & Sharing"),
    ("short_videos", "Creating Short-form Videos / Reels"),
    ("campus_events", "Organizing or Hosting Campus Workshops & Info Sessions"),
    ("content_writing", "Content Writing & Blog Posts"),
    ("graphic_design", "Graphic Design & Visual Branding"),
    ("community_outreach", "Student Community Outreach & Networking"),
]

class AmbassadorApplicationsForm(forms.ModelForm):
    activities = forms.MultipleChoiceField(
        choices=ACTIVITY_CHOICES,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "checkbox-group-input"}
        ),
        required=True,
        error_messages={
            "required": "Please select at least one activity you are comfortable with."
        },
    )

    confirmed_accuracy = forms.BooleanField(
        required=True,
        error_messages={
            "required": "You must confirm that the information provided is accurate."
        },
    )
    agreed_photo_usage = forms.BooleanField(
        required=True,
        error_messages={
            "required": "You must agree to allow SPARC to use your photograph and bio on the website."
        },
    )
    understood_point_system = forms.BooleanField(
        required=True,
        error_messages={
            "required": "You must acknowledge that you understand the ambassador point system."
        },
    )
    agreed_contact = forms.BooleanField(
        required=True,
        error_messages={
            "required": "You must agree to be contacted regarding your application."
        },
    )
    
    class Meta:
        model = AmbassadorApplications
        exclude = ["submitted_at"]
        widgets = {
            "full_name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your full legal name",
                    "autocomplete": "name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "name@example.com",
                    "autocomplete": "email",
                }
            ),
            "whatsapp_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "+880 1XXX-XXXXXX",
                    "autocomplete": "tel",
                }
            ),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "gender": forms.Select(attrs={"class": "form-control"}),
            "university": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., North South University",
                }
            ),
            "department": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Electrical and Computer Engineering",
                }
            ),
            "year_of_study": forms.Select(attrs={"class": "form-control"}),
            "student_id": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your university student ID",
                }
            ),
            "is_ieee_member": forms.CheckboxInput(
                attrs={
                    "class": "form-checkbox",
                    "id": "id_is_ieee_member",
                }
            ),
            "ieee_membership_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your 8-digit IEEE Membership Number",
                }
            ),
            "ieee_membership_grade": forms.Select(
                attrs={"class": "form-control"}
            ),
            "ieee_student_branch": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., IEEE NSU Student Branch",
                }
            ),
            "ieee_position": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., General Member, Vice Chair (Optional)",
                }
            ),
            "photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-file-input",
                    "accept": ".jpg,.jpeg,.png,image/jpeg,image/png",
                }
            ),
            "bio": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Write a short biography for the SPARC website (maximum 50 words)...",
                }
            ),
            "motivation": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Tell us why you want to represent SPARC at your university...",
                }
            ),
            "referral_source": forms.Select(attrs={"class": "form-control"}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        # check uniqueness
        if AmbassadorApplications.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An application with this email address has already been submitted."
            )
        return email

    def clean_bio(self):
        bio = self.cleaned_data.get("bio", "").strip()
        words = bio.split()
        # max length
        if len(words) > 50:
            raise forms.ValidationError(
                f"Your biography must not exceed 50 words (currently {len(words)} words)."
            )
        return bio

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo:
            if photo.size > 10 * 1024 * 1024:
                raise forms.ValidationError(
                    "The uploaded photograph must be smaller than 10 MB."
                )
        return photo

    def clean(self):
        cleaned_data = super().clean()
        is_member = cleaned_data.get("is_ieee_member")

        if is_member:
            required_ieee_fields = {
                "ieee_membership_number": "Please provide your IEEE membership number.",
                "ieee_membership_grade": "Please select your IEEE membership grade.",
                "ieee_student_branch": "Please provide your IEEE Student Branch name.",
            }
            for field_name, error_msg in required_ieee_fields.items():
                value = cleaned_data.get(field_name)
                if not value or not str(value).strip():
                    self.add_error(field_name, error_msg)
        else:
            # Wipe out any stale IEEE data if the user unchecked IEEE membership
            cleaned_data["ieee_membership_number"] = ""
            cleaned_data["ieee_membership_grade"] = ""
            cleaned_data["ieee_student_branch"] = ""
            cleaned_data["ieee_position"] = ""

        return cleaned_data