
from django.urls import path
from . import views

urlpatterns = [
    path('insertManga/', views.insert_manga, name='insert_manga'),
    path('insertVariant/', views.insert_variant, name='insert_variant'),
    path('variant_detail/<int:variant_id>/', views.variant_detail, name='variant_detail'),
    path('manga_detail/<int:manga_id>/', views.manga_detail, name='manga_detail'),
    path('viewManga/', views.view_manga, name='view_manga'),
    path('viewVariant/', views.view_variant, name='view_variant'),
    path('manga/<int:manga_id>/edit/', views.edit_manga, name='edit_manga'),
    path('manga/<int:manga_id>/delete/', views.delete_manga, name='delete_manga'),
    path('variant/<int:variant_id>/edit/', views.edit_variant, name='edit_variant'),
    path('variant/<int:variant_id>/delete/', views.delete_variant, name='delete_variant'),
    path('search/<str:category>/', views.search_view, name='search'),
    path('viewVariant/sortBy/', views.view_variants, name='view_variants'),
    path('viewManga/sortBy/', views.view_mangas, name='view_mangas'),
    path('wishlist', views.view_wishlist, name='view_wishlist'),
    path('media/variant_images/<str:image_path>/', views.serve_protected_variant_image, name='serve_protected_variant_image'),
]




#from django.conf import settings
#from django.conf.urls.static import static

# Serve media files in development (only works if DEBUG=True)
# if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
