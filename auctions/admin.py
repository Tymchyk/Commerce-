from django.contrib import admin

from .models import AuctionsList,Bids,Comments,Category,Watchlist
admin.site.register(AuctionsList)
admin.site.register(Bids)
admin.site.register(Category)
admin.site.register(Comments)
admin.site.register(Watchlist)