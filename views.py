from django.conf import settings
from django.db import models
from django.utils.text import slugify
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response


@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_submission(request):
    subject = request.data.get("subject")
    description = request.data.get("description")
    file = request.data.get("file")

    try:
        validate_file_format(file)
    except ValidationError as e:
        return Response({"success": False, "msg": str(e)})

    try:
        file_url = upload_file_to_s3(file)
    except:
        return Response({"success": False, "msg": "Unable to upload the file"})

    submission = Submission.objects.create(
        subject=subject,
        description=description,
        file_url=file_url,
        token=slugify(file.name),
        uploaded_by=request.user,
    )

    generate_pdf_and_send_it_via_email(submission)

    return Response({"success": True})


class Submission(models.Model):
    token = models.CharField("Auto-generated unique token", max_length=40, unique=True)

    subject = models.CharField("Subject", max_length=200)
    description = models.TextField("Description", blank=True, null=True)
    file_url = models.URLField("File URL")

    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField("Date uploaded", auto_now=True)


def validate_file_format(file):
    is_valid = dummy_read_and_validate(file)
    if not is_valid:
        raise ValidationError("The file format is not valid")


def dummy_read_and_validate(file) -> bool:
    """
    The idea is this function is responsible for the logic to read and check
    the file contents. The assumption is that it returns either True or False
    """


def upload_file_to_s3(file) -> str:
    """
    Logic for uploading the file to S3.
    :returns file url
    :raises UploadError if sth goes wrong during the upload.
    """


def generate_pdf_and_send_it_via_email(submission: Submission):
    """
    The PDF is generated and sent to the sales/marketing.
    The details of how to generate the pdf and send it via email is not important
    """
