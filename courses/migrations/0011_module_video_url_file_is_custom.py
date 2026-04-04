# Generated manually: restore fields removed in 0008 but still used in views/templates

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_alter_userprogress_module'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='video_url',
            field=models.URLField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name='Ссылка на видео (YouTube)',
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='file',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='modules/files/',
                verbose_name='Дополнительный файл',
            ),
        ),
        migrations.AddField(
            model_name='module',
            name='is_custom',
            field=models.BooleanField(default=False, verbose_name='Изменён преподавателем'),
        ),
    ]
