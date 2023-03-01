from django.urls import path
from django.conf.urls.static import static

from django.conf import settings
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("list/<int:id>",views.list, name="list"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("addlist", views.addlist, name="addlist"),
    path("watchlist", views.watchlist, name = "watchlist"),
    path("categories", views.categories , name = "categories"),
    path("category/<int:id>", views.category_list, name = "category_list"),
    path("winlist", views.winlist, name="winlist")
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)
