from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.db.models import Max,Count

from .models import User,AuctionsList,Comments,Bids,Category,Watchlist,Image

from django.forms import ModelForm,TextInput,Textarea,FileInput,NumberInput

class AddlistForm (ModelForm):
    class Meta:
        model = AuctionsList
        fields =['title','text']
        widgets={
            "title":TextInput(attrs ={"class":"form-control"}),
            "text":Textarea(attrs ={"class":"form-control"}),
        }

class BidsForm(ModelForm):
    class Meta:
        model = Bids
        fields=["bid"]
        widgets={
            "bid":NumberInput(attrs ={"class":"form-control"}),
        }

class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']
        widgets={
            "comment":TextInput(attrs ={"class":"form-control"}),
        }

class ImageForm(ModelForm):
    class Meta:
        model =Image
        fields=['image']
        widgets={
            "image":FileInput(attrs ={"class":"form-control"}),
        }

def count_win(request):
    win_list=[]
    wins_bids= Bids.objects.values("list").filter(list__button ="disable").annotate(Max("bid"))
    for wins in wins_bids:
        win = Bids.objects.filter(list__id = wins["list"], bid= wins["bid__max"],user = request.user)
        for w in win:
            if w :
                win_list.append(w)
    return len(win_list)

def index(request):
    bids = Bids.objects.values("list__id").annotate(Max("bid"))

    image = Image.objects.all()
    user =request.user
    
    if user.is_authenticated:
        id = Watchlist.objects.filter(user= user, favorites = "enable").aggregate(Count('favorites'))
        win =count_win(request) 
    else:
        id = 0
        win=0
    return render(request, "auctions/index.html",{
        "models": AuctionsList.objects.all().order_by('-date'),
        "bids":bids,
        "image":image,
        "id":id,
        "win":win
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def addlist(request):
        if request.method == "POST":
            form = AddlistForm(request.POST)
            cat = request.POST.get("categ")
            if form.is_valid():
                title = form.cleaned_data["title"]
                text = form.cleaned_data['text']
                user = request.user
                list = AuctionsList(title = title, text = text, category = Category.objects.get(id = cat),user = user)
                list.save()
                imageform=ImageForm(request.POST,request.FILES)
                if imageform.is_valid():
                    image = request.FILES['image']
                    images = Image(list= list, image = image)
                    images.save()
                bidform = BidsForm(request.POST)
                if bidform.is_valid():
                    bid = bidform.cleaned a["bid"]
                    user = request.user
                    Addbids = Bids(list = list, bid = bid,user = user)
                    Addbids.save()
            return redirect(f"/")
               
        else:          
            form = AddlistForm()
            categories = Category.objects.all()
            bidform = BidsForm()
            imageform = ImageForm()
            id = Watchlist.objects.filter(user= request.user, favorites = "enable").aggregate(Count('favorites'))
            win =count_win(request) 
            return render(request,"auctions/Addlist.html",{
                "form":form,
                "categories":categories,
                "bidform":bidform,
                "imageform":imageform,
                "id": id,
                "win":win
            })



def categories(request):
    categories = Category.objects.all()
    id = Watchlist.objects.filter(user= request.user, favorites = "enable").aggregate(Count('favorites'))
    win =count_win(request) 
    count_category = AuctionsList.objects.values("category_id").annotate(Count("title"))
    return render(request, "auctions/categories.html",{
        "categories": categories,
        "id":id,
        "counts":count_category,
        "win":win
    })

def watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(user =user).all()
    image = Image.objects.all()
    bids = Bids.objects.values("list__id").annotate(Max("bid"))
    id = Watchlist.objects.filter(user= request.user, favorites = "enable").aggregate(Count('favorites'))
    win =count_win(request) 
    return render(request,"auctions/watchlist.html",{
        "watchlist":watchlist,
        "image":image,
        "bids":bids,
        "id":id,
        "win":win
    })
    
@login_required
def list(request, id):
    if request.method == "POST":
        bidform = BidsForm(request.POST)
        if bidform.is_valid():
            new_bid = bidform.cleaned_data['bid']
            user = request.user
            bids = Bids(list = AuctionsList.objects.filter(id = id).first(), bid = new_bid,user = user)
            bids.save()
        try:
            button = request.POST["change"]
            AuctionsList.objects.filter(id = id).update(button = button)
        except:
            pass
        try:
            check_watchlist = request.POST["watchlist"]
            Watchlist.objects.filter(list=AuctionsList.objects.get(id=id),user = request.user).update(favorites = check_watchlist)
        except:
            pass
        commentsform = CommentsForm(request.POST)
        if commentsform.is_valid():
            comment = commentsform.cleaned_data["comment"]
            id_comm = request.POST['titlecom']
            add_c = Comments(list = AuctionsList.objects.get(id= id_comm), user = request.user , comment = comment)
            add_c.save()
        
        return HttpResponseRedirect(f"{id}")
    else:
        list = AuctionsList.objects.get(id = id)
        image = Image.objects.get(list= list)
        bid = Bids.objects.filter(list = list)
        max = bid.aggregate(Max("bid"))
        counts = bid.aggregate(Count("bid"))
        winner = Bids.objects.get(list=list, bid = max["bid__max"])
        if not Watchlist.objects.filter(list = AuctionsList.objects.get(id = id), user= request.user).all():
            Addwatchlist= Watchlist(list = AuctionsList.objects.get(id = id),user = request.user)
            Addwatchlist.save()
        check_list = Watchlist.objects.get(list = AuctionsList.objects.filter(id = id).first(), user = request.user)
        bidform = BidsForm(max)
        check_user = request.user
        comments = CommentsForm()
        comments_all = Comments.objects.filter(list =AuctionsList.objects.get(id = id))
        id = Watchlist.objects.filter(user= request.user, favorites = "enable").aggregate(Count('favorites'))
        win =count_win(request) 
        return render(request,"auctions/list.html",{
            "list": list,
            "bidform":bidform,
            "bid":max,
            "winner":winner,
            "counts":counts,
            'check_user':check_user,
            "check_list":check_list,
            "comments":comments,
            "comments_all":comments_all,
            "image": image,
            "id":id,
            "win":win
        })


def category_list(request,id):
    bids = Bids.objects.values("list__id").annotate(Max("bid"))
    name = Category.objects.get(id = id)
    lists = AuctionsList.objects.filter( category = Category.objects.get(id= id)).all()
    image = Image.objects.all()
    id = Watchlist.objects.filter(user= request.user, favorites = "enable").aggregate(Count('favorites'))
    win =count_win(request) 
    return render(request,"auctions/category_list.html",{
        "lists":lists,
        "name":name,
        "image":image,
        "id":id,
        "bids":bids,
        "win":win
    })

def winlist(request):
    wins_bids= Bids.objects.values("list").filter(list__button ="disable").annotate(Max("bid"))
    win =count_win(request) 
    win_pages = []
    for w in wins_bids:
        win1 = Bids.objects.filter(list__id = w["list"], bid= w["bid__max"],user = request.user)
        win_pages.append(win1)
    bids = Bids.objects.values("list__id").annotate(Max("bid"))
    image = Image.objects.all()
    return render(request,"auctions/winlist.html",{
        "image":image,
        "wins":win_pages,
        "bids":bids,
        "win":win

    })
