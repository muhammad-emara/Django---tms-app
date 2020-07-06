from django.contrib import admin
from django.contrib import  messages
from django.urls import path
from django.shortcuts import redirect, render
from django.forms import forms
from django.utils.safestring import mark_safe
from .models import Teacher, Subject
import unicodecsv as csv

# Register your models here.


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin, CsvImportForm):
    change_list_template = "entities/teachers_changelist.html"
    readonly_fields = ["profile_picture_image"]

    def profile_picture_image(self, obj):
        return mark_safe('<img src="{url}" width="250" />'.format(
            url=obj.profile_picture.url
            )
        )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            file_lines = csv_file.read().splitlines()
            reader = csv.DictReader(file_lines)
            invalid_data = 0
            success_message = "Your csv file has been uploaded"
            for row in reader:
                if row['First Name'].isspace() or row['First Name'] is None or len(row['First Name']) == 0:
                    invalid_data += 1
                    continue
                if row['Last Name'].isspace() or row['Last Name'] is None or len(row['Last Name']) == 0:
                    invalid_data += 1
                    continue
                if row['Email Address'].isspace() or row['Email Address'] is None or len(row['Email Address']) == 0:
                    invalid_data += 1
                    continue
                if row['Profile picture'].isspace() or row['Profile picture'] is None or len(row['Profile picture']) == 0:
                    row['Profile picture'] = 'default.png'

                # add a teacher if he/she does not have a duplicate email
                try:
                    email_exists = Teacher.objects.get(email_address=row['Email Address'])
                except Teacher.DoesNotExist:
                    email_exists = None

                if email_exists is not None:
                    failed = row['First Name'] + ' ' + row['Last Name'] + " has an email that already exists. "
                    self.message_user(request, failed, level=messages.ERROR)

                teacher = Teacher.objects.create(email_address=row['Email Address'])
                teacher.first_name = row['First Name']
                teacher.last_name = row['Last Name']
                teacher.room_number = row['Room Number']
                teacher.phone_number = row['Phone Number']
                teacher.profile_picture = '/images/' + row['Profile picture']

                # add a teacher if he/she has 5 subjects or less
                subjects = row['Subjects taught'].split(',')
                if len(subjects) > 5:
                    failed = row['First Name'] + ' ' + row['Last Name'] + " has more than 5 subjects. "
                    self.message_user(request, failed, level=messages.ERROR)
                    continue

                # create the subject if it does not exist
                for subject in subjects:
                    try:
                        subject_exists = Subject.objects.get(name=subject)
                    except Subject.DoesNotExist:
                        subject_exists = None
                    if subject_exists is None:
                        Subject.objects.create(name=subject)
                    teacher.subject_taught.add(Subject.objects.get(name=subject))

                teacher.save()
            failed = str(invalid_data) + " record(s) had invalid data"
            self.message_user(request, failed, level=messages.ERROR)
            self.message_user(request, success_message)

            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "admin/csv_form.html", payload
        )


admin.site.register(Subject)
