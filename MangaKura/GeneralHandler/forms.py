from django import forms
from .models import UserToManga, UserToVariant, VariantImage, UserToWishlistItem, WishlistImage
from django.utils.html import format_html
from django.forms import inlineformset_factory

class MangaForm(forms.ModelForm):
    class Meta:
        model = UserToManga
        fields = ['manga_title', 'animeclick_url', 'description', 'owned_volumes', 'all_read', 'completed', 'physical_position', 'volume_doubles']
        help_texts = {
            'physical_position': format_html('Inserisci uno dei seguenti, e poi una pipe "|".\n- Baule\n- Mensola sopra PC 1/2\n- Libreria nera mensola 1/2/3/4/5\n- Mensola sopra termosifone 1/2/3\n- Scaffale pianoforte sx/dx 1/2\n- Mensola sopra il letto\n- Armadio del letto\n- Mobile della scrivania 1/2/3'.replace('\n', '<br>')),
        }

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
            'vinted_description', 'to_sell'
        ]
        help_texts = {
            'physical_position': format_html('Inserisci uno dei seguenti, e poi una pipe "|".\n- Baule\n- Mensola sopra PC 1/2\n- Libreria nera mensola 1/2/3/4/5\n- Mensola sopra termosifone 1/2/3\n- Scaffale pianoforte sx/dx 1/2\n- Mensola sopra il letto\n- Armadio del letto\n- Mobile della scrivania 1/2/3'.replace('\n', '<br>')),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize with one pair by default
        self.copies_sold_forms = [CopiesSoldForm(prefix='copy_0')]
        if self.instance and self.instance.useful_links:
            # Convert list to a string (one per line)
            self.fields['useful_links'].initial = "\n".join(self.instance.useful_links)


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


class VariantImageForm(forms.ModelForm):
    class Meta:
        model = VariantImage
        fields = ["image"]

VariantImageFormSet = inlineformset_factory(
    UserToVariant, VariantImage, form=VariantImageForm, extra=3, can_delete=True
)



class WishlistItemForm(forms.ModelForm):

    release_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    class Meta:
        model = UserToWishlistItem
        fields = [
            'title', 'price', 'release_date', 'description', 'copies_to_buy'
        ]

    useful_links = forms.CharField(widget=forms.Textarea, required=False, help_text="Enter useful links, one per line.")

    def clean_useful_links(self):
        data = self.cleaned_data['useful_links']
        if data:
            return [link.strip() for link in data.splitlines() if link.strip()]
        return []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.useful_links:
            # Convert list to a string (one per line)
            self.fields['useful_links'].initial = "\n".join(self.instance.useful_links)


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
                WishlistImage.objects.create(wishlist_item=instance, image=image)

        return instance
    

class WishlistImageForm(forms.ModelForm):
    class Meta:
        model = WishlistImage
        fields = ["image"]

WishlistImageFormSet = inlineformset_factory(
    UserToWishlistItem, WishlistImage, form=WishlistImageForm, extra=3, can_delete=True
)