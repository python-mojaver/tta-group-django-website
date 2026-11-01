from django.core.exceptions import ValidationError


def validate_upload_size(value):
    """Limit each stored upload, including files streamed to disk by Django."""
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("Maximum upload size is 5 MB.", code="file_too_large")


def validate_pdf(value):
    """Extension validation is separate; check the PDF header without consuming the file."""
    # Restore the cursor: storage still needs to read the complete upload.
    position = value.tell()
    try:
        value.seek(0)
        if value.read(5) != b"%PDF-":
            raise ValidationError("Upload a PDF document.", code="invalid_pdf")
    finally:
        value.seek(position)
