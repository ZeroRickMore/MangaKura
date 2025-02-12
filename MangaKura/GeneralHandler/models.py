from django.db import models
from django.contrib.auth.models import User

# This models links a manga to a user. Not necessary to have a "Manga" object of its own as this is strictly related to the user.
# Like, a user does not link a manga from a general database, he simply "creates" a new manga each time, just make sure that it exists because else it's a useless service!
class UserToManga(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manga_title = models.CharField(max_length=255)
    animeclick_url = models.URLField()
    owned_volumes = models.CharField(max_length=255)
    physical_position = models.CharField(max_length=255)
    volume_doubles = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.manga_title} by {self.user.username}"



# This models links a Variant to a user. Not necessary to have a "Variant" object of its own as this is strictly related to the user.
# Like, a user does not link a Variant from a general database, he simply "creates" a new Variant each time, just make sure that it exists because else it's a useless service!

class UserToVariant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    variant_title = models.CharField(max_length=255)
    related_manga_title = models.CharField(max_length=255)
    description = models.TextField()
    stock_price = models.FloatField()
    current_selling_price = models.FloatField()
    physical_position = models.CharField(max_length=255)
    number_of_owned_copies = models.IntegerField()
    copies_sold = models.JSONField(default=list)
    useful_links = models.JSONField(default=list)
    vinted_description = models.TextField()

    def __str__(self):
        return self.variant_title

class VariantImage(models.Model):
    variant = models.ForeignKey(UserToVariant, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='variant_images/')
    
    def __str__(self):
        return f"Image for {self.variant.variant_title}"
