document.addEventListener("DOMContentLoaded", () => {
    // Conditional IEEE Membership Fields Toggle
    const ieeeCheckbox = document.getElementById("id_is_ieee_member");
    const ieeeWrapper = document.getElementById("ieee-fields-wrapper");

    function syncIeeeVisibility() {
        if (!ieeeCheckbox || !ieeeWrapper) return;
        const isChecked = ieeeCheckbox.checked;
        ieeeWrapper.classList.toggle("is-hidden", !isChecked);
        ieeeWrapper.setAttribute("aria-hidden", String(!isChecked));
    }

    if (ieeeCheckbox && ieeeWrapper) {
        ieeeCheckbox.addEventListener("change", syncIeeeVisibility);
        syncIeeeVisibility();
    }

    // Live 50-Word Biography Counter
    const bioInput = document.getElementById("id_bio");
    const bioCounter = document.getElementById("bio-word-counter");
    const MAX_BIO_WORDS = 50;

    function updateBioWordCount() {
        if (!bioInput || !bioCounter) return;
        const trimmed = bioInput.value.trim();
        const words = trimmed.length > 0 ? trimmed.split(/\s+/) : [];
        const count = words.length;

        bioCounter.textContent = `${count} / ${MAX_BIO_WORDS} words`;
        bioCounter.classList.remove("near-limit", "over-limit");

        if (count > MAX_BIO_WORDS) {
            bioCounter.classList.add("over-limit");
        } else if (count >= 42) {
            bioCounter.classList.add("near-limit");
        }
    }

    if (bioInput && bioCounter) {
        bioInput.addEventListener("input", updateBioWordCount);
        updateBioWordCount();
    }
    // Photograph Size & Type Pre-Check + Thumbnail Preview
    const photoInput = document.getElementById("id_photo");
    const previewContainer = document.getElementById("photo-preview-container");
    const previewImg = document.getElementById("photo-preview-img");
    const fileNameSpan = document.getElementById("photo-file-name");
    const fileSizeSpan = document.getElementById("photo-file-size");
    const photoClientError = document.getElementById("photo-client-error");
    const MAX_PHOTO_BYTES = 10 * 1024 * 1024; // 10 MB
    const ALLOWED_MIME_TYPES = ["image/jpeg", "image/png"];
    let activeObjectUrl = null;

    function resetPhotoPreview() {
        if (activeObjectUrl) {
            URL.revokeObjectURL(activeObjectUrl);
            activeObjectUrl = null;
        }
        if (previewContainer) previewContainer.classList.add("is-hidden");
        if (previewImg) previewImg.removeAttribute("src");
    }

    if (photoInput) {
        photoInput.addEventListener("change", () => {
            resetPhotoPreview();
            if (photoClientError) {
                photoClientError.textContent = "";
                photoClientError.classList.add("is-hidden");
            }

            const file = photoInput.files && photoInput.files[0];
            if (!file) return;

            if (!ALLOWED_MIME_TYPES.includes(file.type)) {
                if (photoClientError) {
                    photoClientError.textContent = "Invalid file format. Please select a JPG or PNG image.";
                    photoClientError.classList.remove("is-hidden");
                }
                photoInput.value = "";
                return;
            }

            if (file.size > MAX_PHOTO_BYTES) {
                const sizeMb = (file.size / (1024 * 1024)).toFixed(2);
                if (photoClientError) {
                    photoClientError.textContent = `Selected file is ${sizeMb} MB, which exceeds the 10 MB limit.`;
                    photoClientError.classList.remove("is-hidden");
                }
                photoInput.value = "";
                return;
            }

            activeObjectUrl = URL.createObjectURL(file);
            if (previewImg) previewImg.src = activeObjectUrl;
            if (fileNameSpan) fileNameSpan.textContent = file.name;
            if (fileSizeSpan) {
                fileSizeSpan.textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
            }
            if (previewContainer) previewContainer.classList.remove("is-hidden");
        });
    }

    // Prevent Accidental Double Submissions
    const applicationForm = document.getElementById("ambassador-form");
    const submitBtn = document.getElementById("submit-btn");

    if (applicationForm && submitBtn) {
        applicationForm.addEventListener("submit", () => {
            submitBtn.disabled = true;
            submitBtn.textContent = "Submitting Application...";
        });
    }
});