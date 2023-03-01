from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Category(models.Model):
    categories = models.CharField(max_length = 100)
    def __str__(self):
        return f"{self.categories}"


class Watchlist(models.Model):
    list= models.ForeignKey('AuctionsList', on_delete =models.CASCADE)
    favorites = models.CharField(max_length = 50, default = "disable")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.favorites} made by {self.user}"

class AuctionsList(models.Model):
    title = models.CharField(max_length = 60)
    text = models.TextField()
    category = models.ForeignKey(Category, on_delete = models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete= models.CASCADE)
    button = models.CharField(max_length= 50, default ="enable")

    def __str__(self):
        return f"The {self.title}  of {self.category} made by {self.user}"

class Image(models.Model):
    list = models.ForeignKey(AuctionsList, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='files/lists')

    def __str__(self):
        return f"{self.image}"

class Bids(models.Model):
    list = models.ForeignKey(AuctionsList, on_delete=models.CASCADE)
    bid = models.IntegerField()
    user = models.ForeignKey(User, default = None ,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.list} = {self.bid} made by {self.user}"

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(AuctionsList, on_delete=models.CASCADE)
    comment = models.CharField(max_length = 150)

    def __str__(self):
        return f"Comment: {self.comment} made by {self.user} in {self.list}"