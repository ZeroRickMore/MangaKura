# MangaKura
Manga Kura – "Kura" means "warehouse/storage", so it translates to "Manga Warehouse".  

A service containing information about manga series and variants YOU OWN.  
This is not a place to find information about the mangas themselves, rather a storage for personal use, to just remember the items owned.  
The service MUST be heavily hatsune miku-palette inspired, with the theme being dark because as everyone knows, light attracts bugs.

Each user can insert a new manga series or modify some of his stuff, and the user's activity is completely invisible to everyone else.
So, if a user owns a manga, there is no way to access its data or even know it exists in the first place.

Supports basic search capabilities in your own database of manga/variant, being able to search into the Mangas or into the Variants.

## Manga series
A manga series has a Title, a link to AnimeClick's website of it to have its information (too lazy to update on its own, the website is cool and always up to date so let's use it), volumes owned, and a physical position where it's placed as a description.  
Why not, also have a "doubles" place to simply list volumes that you mistakenly bought multiple times, even though they are not special editions.

Manga information:
Manga Title (string)
Animeclick Manga URL (string, url)
Owned Volumes (string)
Physical Position (string)
Volume Doubles (string)


## Manga variant
A manga variant has a Title, a brief description, a stock price, a selling price, physical position, a Vinted description, and one or more images.  
Also, an amount of copies owned, and amount of copies sold for a specific price (grouped by price).

Variant Title (string)
Related Manga Title (string)
Images (you can upload one or more images)
Description (string)
Stock Price (float)
Current Selling Price (float)
Physical Position (string)
Number of Owned  Copies (int)
Amount of copies already sold, each having a price (you can add entries of couple price - amount of copies sold)
Useful Links (list of strings)
Vinted Description (string)
