
from django.urls import path
from . import views
from . import extra_functions

urlpatterns = [
    path('search/<str:category>/', views.search_view, name='search'),

    # ============================== MANGA STUFF ==============================

    path('insertManga/', views.insert_manga, name='insert_manga'),
    path('manga_detail/<int:manga_id>/', views.manga_detail, name='manga_detail'),
    path('viewManga/', views.view_manga, name='view_manga'),
    path('manga/<int:manga_id>/edit/', views.edit_manga, name='edit_manga'),
    path('manga/<int:manga_id>/delete/', views.delete_manga, name='delete_manga'),
    path('viewManga/sortBy/', views.view_mangas, name='view_mangas'),

    # ============================== VARIANT STUFF ==============================

    path('insertVariant/', views.insert_variant, name='insert_variant'),
    path('variant_detail/<int:variant_id>/', views.variant_detail, name='variant_detail'),
    path('viewVariant/', views.view_variant, name='view_variant'),
    path('variant/<int:variant_id>/edit/', views.edit_variant, name='edit_variant'),
    path('variant/<int:variant_id>/delete/', views.delete_variant, name='delete_variant'),
    path('viewVariant/sortBy/', views.view_variants, name='view_variants'),
    path('media/variant_images/<str:image_path>/', views.serve_protected_variant_image, name='serve_protected_variant_image'),

    # ============================== WISHLIST STUFF ==============================

    path('insertWishlistItem/', views.insert_wishlist_item, name='insert_wishlist_item'),
    path('wishlist_item_detail/<int:wishlist_item_id>/', views.wishlist_item_detail, name='wishlist_item_detail'),
    path('wishlist', views.view_wishlist, name='view_wishlist'),
    path('wishlist_item/<int:wishlist_item_id>/edit/', views.edit_wishlist_item, name='edit_wishlist_item'),
    path('wishlist_item/<int:wishlist_item_id>/delete/', views.delete_wishlist_item, name='delete_wishlist_item'),
    path('media/wishlist_images/<str:image_path>/', views.serve_protected_wishlist_item_image, name='serve_protected_wishlist_item_image'),

    # ============================== EXTRA REST API STUFF ========================

    path('apis', extra_functions.apis),
    path('api/recalculate_own_manga_costs', extra_functions.recalculate_own_manga_costs),
    path('api/cleanup_unused_images', extra_functions.cleanup_unused_images),

]




#from django.conf import settings
#from django.conf.urls.static import static

# Serve media files in development (only works if DEBUG=True)
# if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
