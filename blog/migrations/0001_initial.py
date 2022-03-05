# Generated by Django 4.0.3 on 2022-03-05 10:44

import blog.models.article
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('title', models.CharField(db_index=True, max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
                ('html', models.TextField(blank=True)),
                ('publish', models.BooleanField(default=False, help_text='Publish this article')),
                ('feature', models.BooleanField(default=False, help_text='Feature this article')),
                ('is_explicit', models.BooleanField(default=False, help_text='All images will be tagged explicit')),
                ('video_url', models.URLField(blank=True, null=True)),
                ('text_first', models.BooleanField(default=False)),
                ('gallery_layout', models.CharField(choices=[('one_column', 'One Column'), ('two_column', 'Two Column'), ('slideshow', 'Slideshow')], default='one_column', max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'ordering': ('-created',),
                'permissions': (('publish_article', 'Can publish an article'),),
            },
            bases=(blog.models.article.Analytics, models.Model),
        ),
        migrations.CreateModel(
            name='BlogSetting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='%(class)s', help_text='Navbar label', max_length=400)),
                ('show_in_navbar', models.BooleanField(default=True, help_text='Show link in navbar')),
                ('show_in_footer', models.BooleanField(default=True, help_text='Show link in footer')),
                ('article_list_template', models.CharField(choices=[('one_column', 'One Column'), ('masonry', 'Masonry')], default='one_column', max_length=20, verbose_name='article list template')),
                ('featured_text_hex', models.CharField(default='#000', help_text="The color in which to display the featured article's text on the articles list page", max_length=7, verbose_name='featured article hex color')),
                ('accept_submissions', models.BooleanField(default=False)),
                ('submission_terms', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Blog Settings',
                'verbose_name_plural': 'Blog Settings',
                'ordering': ('site',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='creation date and time')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='update date and time')),
                ('name', models.CharField(db_index=True, max_length=200)),
                ('slug', models.SlugField(max_length=200, unique=True)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ('name',),
            },
        ),
    ]
