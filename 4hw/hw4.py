import datetime
import json

import numpy as np
import matplotlib.pyplot as plt
from flask import Flask
from flask import url_for, render_template, request, redirect
import csv

app = Flask(__name__)


@app.route('/')
def index():
    if request.args:
        input_form = {key: value for key, value in request.args.items()}
        print(input_form)
        with open('names.csv', 'a', newline='') as csvfile:
            header_of_table = ['green', 'grue', 'blue', 'mail', 'sex']
            writer = csv.DictWriter(csvfile, fieldnames=header_of_table)
            writer.writerow(input_form)
        return render_template('thanks.html')
    return render_template('question.html')


@app.route('/json')
def json():
    with open('names.csv') as csvfile:
        header_of_table = ['green', 'grue', 'blue', 'mail', 'sex']
        new = []
        table = csv.DictReader(csvfile, fieldnames=header_of_table)
        for row in table:
            new.append(dict(row))
        return str(new)

@app.route('/search')
def search():
    if request.args:
        input_form = {key: value for key, value in request.args.items()}
        with open('names.csv') as csvfile:
            header_of_table = ['green', 'grue', 'blue', 'mail', 'sex']
            table = csv.DictReader(csvfile, fieldnames=header_of_table)
            founded = []
            for row in table:
                for name, value in input_form.items():
                    if (name, value) in row.items():
                        if row not in founded:
                            founded.append(row)
            print(founded)
        return render_template('search.html')
    return render_template('search.html')

@app.route('/stats')
def stats():
    with open('names.csv') as csvfile:
        table = csvfile.read()
    table = table.splitlines()
    table_good=[]
    male = 0
    female = 0
    for line in table:
        values = line.split(',')
        table_good.append(values)
        if values[4] == 'female':
            female += 1
        else:
            male += 1
    informants = len(table)
    graph()
    return render_template('stats.html', data=table_good, informants=informants, males=male, females=female, url ='/static/images/plot.png')


def graph():
    with open('names.csv') as csvfile:
        header_of_table = ['green', 'grue', 'blue', 'mail', 'sex']
        table = csv.DictReader(csvfile, fieldnames=header_of_table)
        grue_names = []
        male_grue_names = {}
        female_grue_names = {}
        for row in table:
            if row['grue'] not in grue_names:
                grue_names.append(row['grue'])
                male_grue_names[row['grue']] = 0
                female_grue_names[row['grue']] = 0
            if row['sex'] == 'male':
                male_grue_names[row['grue']] += 1
            else:
                female_grue_names[row['grue']] += 1
    men = []
    women = []
    for name in grue_names:
        men.append(male_grue_names[name])
        women.append(female_grue_names[name])
    men_means = men
    women_means = women

    ind = np.arange(len(men_means))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(ind - width / 2, men_means, width,
                    color='#00a61e', label='Мужчины')
    rects2 = ax.bar(ind + width / 2, women_means, width,
                    color='#00a4b8', label='Женщины')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Grue')
    ax.set_title('Grue names by gender')
    ax.set_xticks(ind)
    ax.set_xticklabels(grue_names)
    ax.legend()
    plt.savefig("static\images\plot")

if __name__ == '__main__':
    app.run(debug=True)