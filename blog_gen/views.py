import os
from bson import ObjectId
from django.shortcuts import render, redirect
from .auth import is_logged_in, is_not_logged_in
from .uploader import upload_image, upload_audio
from .generator import get_title_keywords, generate_image, generate_audio
from .database import user_table, cred_table, keywords_table, blogs_table
import bcrypt

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
USE_AWS = os.environ.get('USE_AWS') == 'true'
source = "https://ai-blog-photos.s3.ap-south-1.amazonaws.com/" if USE_AWS else "/static/"


@is_not_logged_in
def index(request):
    """Displays the index page."""

    return render(request, 'index.html')

@is_logged_in
def home(request):
    """Displays the home page."""

    data = user_table.find_one({'username': request.session['username']})
    if data['initialized']:
        interests = data['interests']
        keywords_list = []
        for interest in interests:
            keyword_data = keywords_table.find_one(
                {interest: {'$exists': True}}, {interest: 1, '_id': 0})
            for key, keyword in keyword_data.items():
                if keyword == "":
                    continue
                if isinstance(keyword, list):
                    keywords_list.extend(keyword)
                else:
                    keywords_list.append(keyword)
        blogs = list(blogs_table.find(
            {'keywords': {'$in': keywords_list}}, {'id': "$_id", 'link': 1, 'title': 1, 'keywords': 1, 'image': 1, 'username': 1, '_id': 0}))
        return render(request, 'home.html', {'blogs': blogs, 'source': source})
    else:
        return redirect('initialize')


@is_logged_in
def initialize(request):
    """Initializes the user's interests."""

    categories = list(keywords_table.find({}, {'_id': 0}).limit(1)[0].keys())
    if request.method == 'POST':
        data = user_table.find_one(
            {'username': request.session['username']})
        if not data['initialized']:
            inputs = list(request.POST.values())[1:]
            if len(inputs) < 3:
                return render(request, 'initialize.html', {'categories': categories, 'message': 'Select atleast 3 categories'})
            categories = list(keywords_table.find(
                {}, {'_id': 0}).limit(1)[0].keys())
            interests = []
            for value in inputs:
                if value in categories:
                    interests.append(value)
            user_table.update_one({'username': request.session['username']}, {
                                    '$set': {'initialized': True, 'interests': interests}})
            return redirect('home')
    

    return render(request, 'initialize.html', {'categories': categories})


@is_logged_in
def add_blog(request):
    """Adds a blog to the database."""
    
    if request.method == 'POST':
        link = request.POST.get('link')
        content = request.POST.get('content')
        print(link, content)
        data = get_title_keywords(content)
        if not data:
            return render(request, 'add_blog.html', {'message': 'In generating data'})
        titles = data['titles']
        keywords = data['keywords']
        categories = data['categories']
        image = generate_image(titles, keywords)
        if not image:
            return render(request, 'add_blog.html', {'message': 'In generating image'})
        if USE_AWS:
            image = upload_image(image)
        blogs_table.insert_one({'username': request.session['username'], 'link': link,
                                'content': content, 'title': titles, 'keywords': keywords, 'image': image, 'audio': ''})
        for category, keyword in categories.items():
            keywords_table.find_one_and_update({category: {"$exists": True}}, {'$push': {category: keyword}})
        return render(request, 'add_blog.html')
    return render(request, 'add_blog.html', )


@is_logged_in
def all_blogs(request):
    """Displays all the blogs."""

    blogs = list(blogs_table.find({}, {'id': "$_id", 'link': 1, 'title': 1, 'keywords': 1, 'image': 1, 'username': 1, '_id': 0}))
    return render(request, 'all_blogs.html', {'blogs': blogs, 'source': source})


@is_logged_in
def liked_blogs(request):
    """Displays the blogs liked by the user."""

    data = user_table.find_one({'username': request.session['username']})
    if not data['likes']:
        return render(request, 'liked_blogs.html', {'message': 'No liked blogs'})
    object_ids = [ObjectId(id_) for id_ in data['likes'] if id_]
    print(object_ids)
    blogs = list(blogs_table.find({'_id': {'$in': object_ids}}, {'id': "$_id", 'link': 1, 'title': 1, 'keywords': 1, 'image': 1, '_id': 0}))
    return render(request, 'liked_blogs.html', {'blogs': blogs, 'id': id, 'source': source})



def login(request):
    """Handles user login."""

    if request.method == 'POST':
        username = request.POST.get('username').strip().lower()
        password = request.POST.get('password').strip()

        # if cred_table.find_one({'username': username, 'password': password}):
        #     request.session['username'] = username
        #     return redirect('home')
        # return render(request, 'index.html', {'message': 'Invalid Credentials'})
        stored_hash = cred_table.find_one({'username': username})['password_hash'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            request.session['username'] = username
            return redirect('home')

    return render(request, 'index.html', {'message': 'Invalid Credentials'})


def signup(request):
    """Handles user signup."""

    if request.method == 'POST':
        username = request.POST.get(
            'username').strip().lower()  
        password = request.POST.get('password').strip()

        if cred_table.find_one({'username': username}):
            return render(request, 'index.html', { 'message': 'Username already exists', 'is_signup': True})
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cred_table.insert_one({'username': username, 'password': password, 'password_hash': password_hash.decode('utf-8')})
        user_table.insert_one({'username': username, 'initialized': False, 'likes': [], 'interests': []})
        return redirect('home')

    return render(request, 'index.html', {"is_signup": True})


@is_logged_in
def logout(request):
    """Logs out the user by deleting the 'username' key from the session."""

    del request.session['username']
    return render(request, 'index.html', {'message': 'Logged Out Successfully'})


@is_logged_in
def blog_action(request, id, action):
    """Likes or dislikes a blog."""

    if action == 'like':
        data = list(user_table.find({'username': request.session['username']}))
        print(data)
        if id not in data[0]['likes']:
            user_table.update_one({'username': request.session['username']}, {
                                '$push': {'likes': id}})
        else:
            user_table.update_one({'username': request.session['username']}, {
                                '$pull': {'likes': id}})
        return redirect('blog', id=id)
    elif action == 'audio':
        data = blogs_table.find_one({'_id': ObjectId(id)}, {'_id': 0})
        print(data['audio'])
        if not data['audio']:
            audio = generate_audio(data['content'])
            if not audio:
                return redirect('blog', id=id, message='Error in generating audio')
            if USE_AWS:
                audio = upload_audio(audio)
            blogs_table.update_one({'_id': ObjectId(id)}, {
                '$set': {'audio': audio}})
        return redirect('blog', id=id)


@is_logged_in
def show_blog(request, id):
    """Displays a blog."""
    data = user_table.find_one({'username': request.session['username']})
    if id in data['likes']:
        liked = True
    else:
        liked = False
    blog = blogs_table.find_one({'_id': ObjectId(id)}, {'_id': 0})
    return render(request, 'show_blog.html', {'blog': blog, 'id': id, 'liked': liked, 'source': source})