#importing the necessary modules to render the templates
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from users.forms import UserUpdateForm, ProfileUpdateForm
from django.contrib import messages
from django.http import HttpResponse
from .forms import AddUrlForm, RepositoryForm, EmailForm
from .models import Url, Repository
import requests
import time
import sys 
import json
import os
from datetime import datetime
from collections import defaultdict
from collections import Counter
import plotly.graph_objs as go
import plotly.io as pio
from functools import lru_cache
from pydriller import Repository
import pandas as pd
import plotly.offline as opy
sys.setrecursionlimit(100000)
from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponseBadRequest
from django.core.mail import send_mail
from django.http import HttpResponseBadRequest



#views for user profile
@login_required
def profile(request):
    if request.method == 'POST':
        user_update_form = UserUpdateForm(request.POST, instance=request.user)
        profile_update_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_update_form.is_valid() and profile_update_form.is_valid():
            user_update_form.save()
            profile_update_form.save()
            messages.success(request, 'Profile Updated Successfully')
            return redirect('wdg-home')
    else:
        user_update_form = UserUpdateForm(instance=request.user)
        profile_update_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request,'profile.html',{'user_update_form':user_update_form,'profile_update_form':profile_update_form})


#views for user home
@login_required
def home(request):
    if request.method == 'GET':
        add_url_form = AddUrlForm()
        repository_form = RepositoryForm()
        urls = Url.objects.filter(user=request.user)
        return render(request, 'home.html', {'add_url_form':add_url_form,'repository_form':repository_form,'urls': urls})
    else:
        add_url_form = AddUrlForm(request.POST)
        repository_form = RepositoryForm(request.POST)

        if request.method == 'POST':
            if add_url_form.is_valid():
                url = add_url_form.save(commit=False)
                url.user = request.user
                add_url_form.save()
                messages.success(request, 'Successfully added url')
                return redirect('wdg-home')
            elif repository_form.is_valid():
                personal_access_token = os.environ.get("PERSONAL_ACCESS_TOKEN")
                api_base_url = "https://api.github.com"
                title = repository_form.cleaned_data['title']
                students = repository_form.cleaned_data['students'].split(',')
                data = {
                    "name":title,
                    "private": False,
                    "collaborators": students
                }
                response = requests.post(f"{api_base_url}/user/repos", json=data, headers={"Authorization": f"Bearer {personal_access_token}"})
                if response.status_code == 201:
                    owner = response.json()["owner"]["login"]
                    repo_name = response.json()["name"]
                    repo_url = response.json()["html_url"]
                    print("Successfully created repository")
                    for collaborator in data["collaborators"]:
                        response = requests.put(f"{api_base_url}/repos/{owner}/{repo_name}/collaborators/{collaborator}", headers={"Authorization": f"Bearer {personal_access_token}"})
                        
                    if response.status_code != 204:
                        print(f"Failed to add collaborator {collaborator}")
                repository = repository_form.save(commit=False)
                repository.user = request.user
                repository.url = repo_url
                repository_form.save()
                messages.success(request, f'Successfully Created the Repository for {title}')
                return redirect('wdg-home')
            else:
                messages.error(request, 'Error: Invalid form submission')
                redirect('wdg-home')


# View function to delete an URL from the added list
@login_required
def delete_url(request, url_id):
    url = get_object_or_404(Url, id=url_id, user=request.user)
    url.delete()
    return redirect('wdg-home')


#views for the user dashboard
@login_required
@lru_cache(maxsize=128, typed=False)
def dashboard(request, url_id):
    url = get_object_or_404(Url, pk=url_id)
    url_spl = url.url
    slash = url_spl.split('/')
    repo_name = (slash[4].split('.'))[0]
    personal_access_token = os.environ.get("PERSONAL_ACCESS_TOKEN")
    owner = slash[3]
    headers={"Authorization": f"Bearer {personal_access_token}"}
    api = f'https://api.github.com/repos/{owner}/{repo_name}/commits'
    params = {"per_page": 100}
    results = []

    #Bypassing the GitHub pagination
    while api:
        response = requests.get(api, params=params, headers=headers)
        results += response.json()
        api = None
        if "Link" in response.headers:
            links = response.headers["Link"].split(", ")
            for link in links:
                if "rel=\"next\"" in link:
                    api = link[link.index("<") + 1 : link.index(">")]

    #Number of commits from the main/master branch
    contributors = []
    contributorsemails =[]
    dict1 = {}
    for commitdata in results:
        if "commit" in commitdata and "author" in commitdata["commit"] and "name" in commitdata["commit"]["author"]:
            contributors.append(commitdata["commit"]["author"]["name"])
            contributorsemails.append(commitdata["commit"]["author"]["email"])
            dict1[commitdata["commit"]["author"]["name"]] = commitdata["commit"]["author"]["email"]
    # print(dict1)
    noc = dict(Counter(contributors))
    nocemail = dict(Counter(contributorsemails))
    contrib_dict = {name: email for name, email in zip(contributors, contributorsemails)}

    #Appending the branch names to gather the commits other than the main/master branch
    api4 = f'https://api.github.com/repos/{owner}/{repo_name}/branches'
    response4 = requests.get(api4, headers=headers)
    branchnames = []
    for data in response4.json():
        if data['name'] == 'main': pass
        elif data['name'] == 'master': pass
        else: branchnames.append(data['name'])

    #Number of commits from the remaining branches
    results1 = []
    contributors1 = []
    contributorsemails1 = []
    for branch in branchnames:
        api1 = f'https://api.github.com/repos/{owner}/{repo_name}/commits?sha={branch}'
        params = {"per_page": 100}
        while api1:
            response1 = requests.get(api1, params=params,headers=headers)
            results1 += response1.json()
            api1 = None
            if "Link" in response1.headers:
                links = response1.headers["Link"].split(", ")
                for link in links:
                    if "rel=\"next\"" in link:
                        api1 = link[link.index("<") + 1 : link.index(">")]
    for commitdata1 in results1:
        # print(commitdata1)
        contributors1.append(commitdata1["commit"]["author"]["name"])
        contributorsemails1.append(commitdata1["commit"]["author"]["email"])
    noc1 = dict(Counter(contributors1))
    nocemail1 = dict(Counter(contributorsemails1))               

    for key in noc1:
        if key in noc:
            noc[key] += noc1[key]
        else:
            noc[key] = noc1[key]
    for key in nocemail1:
        if key in nocemail:
            nocemail[key] += nocemail1[key]
        else:
            nocemail[key] = nocemail1[key]

    total_commits = sum(noc.values())
    cons = []
    for keys, value in noc.items():
        cons.append(keys)
    
    consemail = []
    for keys, value in nocemail.items():
        consemail.append(keys)
    #request.session['consemail'] = consemail
    request.session['consemail'] = dict1

    
    #plotting the contributors vs. commits made as bargraph    
    x = list(noc.keys())
    y = list(noc.values())
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y))
    fig.update_layout(title='Contributor vs. Commits', xaxis_title='Contributor', yaxis_title='Commits made')
    chart_html = pio.to_html(fig, full_html=False)
    time.sleep(0.5)

    #Plotting the Authors vs. Total Lines of Code (LOC)
    authors1 = defaultdict(int)
    gen = Repository(url_spl).traverse_commits()
    while True:
        try:
            commit = next(gen)
            author = commit.author.name
            authors1[author] += commit.lines
        except StopIteration:
            break
        except Exception as e:
            print(f"Error in loop: {e}")
    
    author_names = list(authors1.keys())
    lines_per_author = list(authors1.values())

    trace_authors = go.Scatter(
    x=author_names,
    y=lines_per_author,
    name='Authors'
    )
    trace1 = [trace_authors]
    layout2 = go.Layout(title='Authors vs. Lines of Code (LOC)', xaxis=dict(title='Author'), yaxis=dict(title='Lines of Code'))
    fig2 = go.Figure(data=trace1, layout=layout2)
    plot_lines = opy.plot(fig2, auto_open=False, output_type='div')


    #Plotting the languages used in a GitHub repository as a pie chart
    api2 = f'https://api.github.com/repos/{owner}/{repo_name}/languages'
    response2 = requests.get(api2, headers=headers)
    languages = response2.json()
    labels = list(languages.keys())
    values = list(languages.values())
    layout = go.Layout(title='Languages Used')
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)], layout=layout)
    time.sleep(0.5)

    #listing all the branches
    api3 = f'https://api.github.com/repos/{owner}/{repo_name}/branches'
    response3 = requests.get(api3, headers=headers)
    branches = response3.json()
    
    #General Information
    api_general = f"https://api.github.com/repos/{owner}/{repo_name}"
    api_tags = f"https://api.github.com/repos/{owner}/{repo_name}/tags"
    response4 = requests.get(api_general, headers=headers)
    if response4.status_code == 200:
        data_gen = json.loads(response4.text)
        created_at = data_gen["created_at"]
        updated_at = data_gen["updated_at"]
        forks_count = data_gen["forks_count"]
        github_url = data_gen["clone_url"]
        default_branch = data_gen["default_branch"]
        repo_visibility = data_gen["visibility"]
        created_at_datetime = datetime.fromisoformat(created_at[:-1])
        updated_at_datetime = datetime.fromisoformat(updated_at[:-1])
        age_in_days = (datetime.now() - created_at_datetime).days
    else:
        print(f"Error: {response.status_code}")
    tags_response = requests.get(api_tags)
    if tags_response.status_code == 200:
        tags_data = json.loads(tags_response.text)
        tags_count = len(tags_data)
    else:
        tags_count = 0

    repo_data = [f'Created on: {created_at_datetime}',f'Updated on: {updated_at_datetime}',f'Repository age: {age_in_days} days',f'Visibility: {repo_visibility}',f'Default branch: {default_branch}',f'Forks count: {forks_count}',f'Tags count: {tags_count}']
    return render(request, 'dashboard.html', {'url': url,'chart': chart_html,'plot':fig.to_html(full_html=False), 'branches': branches,'total_commits':total_commits, 'cons':contrib_dict.keys(), 'consemail':consemail, 'repo_data':repo_data,'github_url':github_url,'plot_lines':plot_lines})

#View that defines the code quality page
@login_required
def codequality(request, url_id):
    sys.setrecursionlimit(100000)
    url = get_object_or_404(Url, pk=url_id)
    url_spl = url.url

    #Plotting the Delta maintainability of the commits vs. time to asses the quality of the commits
    repo_path = url_spl
    delta_maintainability = []
    commit_dates = []
    commit_hashes= []
    insertions = []
    deletions = []
    modifications = []
    authors =[]
    lines =[]
    authors1 = defaultdict(int)
    #generating the generator object of the repository to iterate over the commits
    gen = Repository(repo_path).traverse_commits()
    while True:
        try:
            commit = next(gen)
            delta_maintainability.append(commit.dmm_unit_complexity)
            commit_dates.append(commit.author_date)
            commit_hashes.append(commit.hash)
            authors.append(commit.author.name)
            author = commit.author.name
            authors1[author] += commit.lines
            lines.append(commit.lines)
            insertions.append(commit.insertions)
            deletions.append(commit.deletions)
            modifications.append((commit.lines) - (commit.insertions+commit.deletions))
        except StopIteration:
            break
        except Exception as e:
            print(f"Error in loop: {e}")


    #Plotting the Cyclomatic Complexity vs. commit dates
    delta_maintainability_new = [0 if x==None else x for x in delta_maintainability]
    trace_dates = go.Scatter(
    x=commit_dates,
    y=delta_maintainability_new,
    mode='lines+markers',
    name='Dates'
    )
    layout = go.Layout(title='Maintainability vs. Time', xaxis=dict(title='Commit Date'), yaxis=dict(title='Cyclomatic Complexity'))
    fig = go.Figure(data=trace_dates, layout=layout)
    plot_show = opy.plot(fig, auto_open=False, output_type='div')


    #Plotting the code churn for each commit
    trace_insertions = go.Scatter(
    x=commit_dates,
    y=insertions,
    mode='lines+markers',
    name='Insertions'
    )

    trace_deletions = go.Scatter(
    x=commit_dates,
    y=deletions,
    mode='lines+markers',
    name='Deletions'
    )

    trace_modifications = go.Scatter(
        x=commit_dates,
        y=modifications,
        mode='lines+markers',
        name='Modifications'
    )

    layout1 = go.Layout(
    title='Code Churn vs. Commit',
    xaxis=dict(title='Commit Date'),
    yaxis=dict(title='Number of Lines')
    )

    data_lines = [trace_insertions, trace_deletions, trace_modifications]
    fig1 = go.Figure(data=data_lines, layout=layout1)
    plot_html = opy.plot(fig1, auto_open=False, output_type='div')


    return render(request, 'codequality.html', {'url': url, 'plot_show':plot_show,'plot_html': plot_html})

#View to send individual and group emails
def send_email_view(request,url_id):
    if request.method == 'GET':
        name = request.GET.get('name')
        consemail = request.session.get('consemail')
        email_form = EmailForm(initial={'Email':consemail[name]})
        return render(request, 'email.html', {'email_form':email_form})
    elif request.method == 'POST':
        email_form = EmailForm(request.POST)
        user = request.user
        if email_form.is_valid():
            subject = email_form.cleaned_data['subject']
            message = email_form.cleaned_data['text']
            recipient_list = [email_form.cleaned_data['Email']]
            sender = user

            try:
                send_mail(subject, message, sender, recipient_list, fail_silently=False)
            except Exception as e:
                return HttpResponseBadRequest("Error sending email: " + str(e))

            return HttpResponse("Email sent!")
    else:
        return HttpResponseBadRequest("Invalid request method")
    
#View that defines the help documentation page
def help(request):
    if request.method == 'GET':
       return render(request, 'help.html')








    
