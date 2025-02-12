from django import forms
from .models import UserToManga

class MangaForm(forms.ModelForm):
    class Meta:
        model = UserToManga
        fields = ['manga_title', 'animeclick_url', 'owned_volumes', 'physical_position', 'volume_doubles']






from .models import UserToVariant, VariantImage

class CopiesSoldForm(forms.Form):
    price = forms.CharField(label="Price when sold", required=False)  # Will store a JSON string of prices
    amount = forms.CharField(label="Amount of variants sold for the price", required=False)  # Will store a JSON string of amounts

    def clean(self):
        """
        Ensures `price` and `amount` are valid lists of numbers.
        Expected format: JSON string like "[10, 15, 20]" for price and "[2, 3, 5]" for amount.
        """

        """
        Completely bypasses `super().clean()` and manually processes price and amount as lists.
        """
        cleaned_data = {}  # Do NOT use super().clean() to avoid losing list data

        #print("PRICE RAW ->", self.price)
        #print("AMOUNT RAW ->", self.amount)

        # Get raw input values
        price_raw = self.data.getlist(self.add_prefix('price'))
        amount_raw = self.data.getlist(self.add_prefix('amount'))

        # Convert string numbers to floats
        try:
            cleaned_data['price'] = [float(p) for p in price_raw if p]
            cleaned_data['amount'] = [int(a) for a in amount_raw if a]
        except ValueError:
            raise forms.ValidationError("Invalid format: Price must be numbers, and Amount must be integers.")

        # Ensure both lists have the same length
        if len(cleaned_data['price']) != len(cleaned_data['amount']):
            raise forms.ValidationError("Price and Amount lists must have the same length.")

        return cleaned_data

class UserToVariantForm(forms.ModelForm):
    copies_sold = forms.CharField(widget=forms.HiddenInput(), required=False)  # Hidden field for storing JSON
    useful_links = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter useful links, one per line.")
    
    stock_price = forms.FloatField(required=False, label="Stock Price")
    current_selling_price = forms.FloatField(required=False, label="Current Selling Price")

    class Meta:
        model = UserToVariant
        fields = [
            'variant_title', 'related_manga_title', 'description', 'stock_price', 
            'current_selling_price', 'physical_position', 'number_of_owned_copies', 
            'vinted_description'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize with one pair by default
        self.copies_sold_forms = [CopiesSoldForm(prefix='copy_0')]


    def clean_useful_links(self):
        data = self.cleaned_data['useful_links']
        if data:
            return [link.strip() for link in data.splitlines() if link.strip()]
        return []

    def save(self, commit=True):
        instance = super().save(commit=False)

        useful_links_data = self.cleaned_data['useful_links']
        instance.useful_links = useful_links_data  # Assign cleaned useful_links to the instance

        if commit:
            instance.save()

        # Handle saving each uploaded image
        if 'images' in self.cleaned_data and self.cleaned_data['images']:
            images = self.cleaned_data['images']
            for image in images:
                VariantImage.objects.create(variant=instance, image=image)

        return instance
