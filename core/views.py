from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Movie, MovieList
import re
from django.http import JsonResponse
from django.shortcuts import get_object_or_404


# Create your views here.

@login_required(login_url='login')
def index(request):
    movies = Movie.objects.all()
    featured_movie = movies[len(movies) - 1]
    
    context = {
        'movies': movies,
        'featured_movie': featured_movie
    }
    return render(request, 'index.html', context)

@login_required(login_url='login')
def movie(request, pk):
    movie_uuid = pk
    
    movie = Movie.objects.get(uu_id=movie_uuid)
    
    context= {
        'movie_details': movie
    }

    return render(request, 'movie.html', context)

@login_required(login_url='login')
def my_list(request):
    movie_obj_list = MovieList.objects.filter(owner_user=request.user)
    movie_list = []
    
    for obj in movie_obj_list:
        movie_list.append(obj.movie)

    context = {
        'movies': movie_list
    }
    
    return render(request, 'my_list.html', context)

@login_required(login_url='login')
def add_to_list(request):
    if request.method == 'POST':
        movie_url = request.POST.get('movie_id')
        uuid_pattern = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}'
        match = re.search(uuid_pattern, movie_url)
        movie_id = match.group() if match else None
        
        movie = get_object_or_404(Movie, uu_id = movie_id)
        movie_list, created = MovieList.objects.get_or_create(owner_user=request.user, movie = movie)
        
        if created:
            response_data = {'status': 'success', 'message': 'Added'}
        else:
            response_data = {'status': 'info', 'message': 'Movie already in list'}
            
        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required(login_url='login')
def genre(request, pk):
    movie_genre = pk
    movies = Movie.objects.filter(genre=movie_genre)
    
    context = {
        'movies': movies,
        'movie_genre': movie_genre
    }
    
    return render(request, 'genre.html', context)

@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        search_term = request.POST['search_term']
        movies = Movie.objects.filter(title__icontains=search_term)
        
        context = {
            'movies': movies,
            'search_term': search_term
        }
        return render(request, 'search.html', context)
    else:
        return redirect('/')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Username or password is invalid')
            return redirect('login')
    else:
        return render(request, 'login.html')

@login_required(login_url='login')
def user_logout(request):
    auth.logout(request)
    return redirect('login')

def user_register(request):
    if request.method == 'POST':
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password == password2:
            email = request.POST['email']
            username = request.POST['username']
            if User.objects.filter(email = email).exists():
                messages.info(request, 'Email already exists!')
                return redirect('register')
                
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exists!')
                return redirect('register')
                    
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                
                # login user
                auth_user = auth.authenticate(username=username, password=password)
                auth.login(request, auth_user)
                return redirect('/')
                
        else:
            messages.info(request, 'Passwords do not match!')
            return redirect('register')

    else:
        return render(request, 'register.html')
    
