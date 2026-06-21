from django.db import models

class FooterSettings(models.Model):
    about_text = models.TextField(default="CampaignManager is a secure, intelligent outreach platform.", max_length=300)
    contact_email = models.EmailField(default="support@campaignmanager.com", blank=True, null=True)
    twitter_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    copyright_year = models.CharField(max_length=4, default="2026")

    class Meta:
        verbose_name_plural = "1. Global Footer Settings"

    def __str__(self):
        return "Global Settings (About, Social, Contact)"

class FooterColumn(models.Model):
    title = models.CharField(max_length=50, help_text="e.g., Platform, Resources, Company")
    order = models.IntegerField(default=0, help_text="Lower numbers appear first (left to right)")

    class Meta:
        ordering = ['order']
        verbose_name_plural = "2. Footer Columns (Main Categories)"

    def __str__(self):
        return self.title

class FooterItem(models.Model):
    column = models.ForeignKey(FooterColumn, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, help_text="Text displayed on website")
    url = models.CharField(max_length=200, help_text="e.g., /dashboard/ or https://google.com")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class LegalPage(models.Model):
    title = models.CharField(max_length=100, help_text="e.g., Privacy Policy")
    slug = models.SlugField(unique=True, help_text="e.g., privacy, terms")
    content = models.TextField(help_text="Write your content here. Paragraphs will be formatted automatically.")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Legal Page"
        verbose_name_plural = "3. Legal Pages"

    def __str__(self):
        return self.title

class ResourcePage(models.Model):
    title = models.CharField(max_length=150, help_text="e.g., Cold Email Guide")
    slug = models.SlugField(unique=True, help_text="e.g., cold-email-guide")
    content = models.TextField(help_text="Write your guide here. HTML tags supported.")
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Resource Page"
        verbose_name_plural = "4. Resource Pages"

    def __str__(self):
        return self.title