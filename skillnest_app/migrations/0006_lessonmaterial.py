from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('skillnest_app', '0005_coursepublishstatus_teachermessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('file', models.FileField(upload_to='lesson_materials/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='materials', to='skillnest_app.lesson')),
            ],
        ),
    ]
