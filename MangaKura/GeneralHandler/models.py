from django.db import models
from django.contrib.auth.models import User

# This models links a manga to a user. Not necessary to have a "Manga" object of its own as this is strictly related to the user.
# Like, a user does not link a manga from a general database, he simply "creates" a new manga each time, just make sure that it exists because else it's a useless service!
class UserToManga(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    manga_title = models.CharField(max_length=255)
    animeclick_url = models.URLField(blank=True, null=True)
    owned_volumes = models.CharField(max_length=255)
    physical_position = models.CharField(max_length=255)
    volume_doubles = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    all_read = models.BooleanField(default=False, blank=True)
    completed = models.BooleanField(default=False, blank=True)
    #rating = models.FloatField(deafult=0.0, blank=True)

    def __str__(self):
        return f"{self.manga_title}"



# This models links a Variant to a user. Not necessary to have a "Variant" object of its own as this is strictly related to the user.
# Like, a user does not link a Variant from a general database, he simply "creates" a new Variant each time, just make sure that it exists because else it's a useless service!

class UserToVariant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    variant_title = models.CharField(max_length=255)
    related_manga_title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    stock_price = models.FloatField(blank=True, null=True)
    current_selling_price = models.FloatField(blank=True, null=True)
    physical_position = models.CharField(max_length=255)
    number_of_owned_copies = models.IntegerField()
    copies_sold = models.JSONField(default=list)
    useful_links = models.JSONField(default=list)
    vinted_description = models.TextField(blank=True, null=True)
    #rating = models.FloatField(deafult=0.0, blank=True)

    def __str__(self):
        return self.variant_title


class VariantImage(models.Model):
    variant = models.ForeignKey(UserToVariant, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='variant_images/')
    
    def __str__(self):
        return f"Image for {self.variant.variant_title}"




# Something that a user wants to buy, to put in a Wishlist.""
# Please note that the "Wishlist" itself is not a real Object, rather it is obtained by querying for UserToWishlist where user=logged_user
class UserToWishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    price = models.FloatField(blank=True, null=True)
    release_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    copies_to_buy = models.IntegerField(blank=True, null=True)
    useful_links = models.JSONField(default=list)

    def __str__(self):
        return self.title



class WishlistImage(models.Model):
    wishlist_item = models.ForeignKey(UserToWishlistItem, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='wishlist_images/')
    
    def __str__(self):
        return f"Image for {self.wishlist_item.title}"
    
    