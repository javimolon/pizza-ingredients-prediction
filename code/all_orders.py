import pandas as pd
import os, sys, time, signal, warnings
import numpy as np
from datetime import datetime
import re
import json
import random
import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')

def handle_exit(signal, frame):
    
    print('Exiting', end='', flush=True)
    for _ in range(10):

        print('.', end='', flush=True)
        time.sleep(0.15)
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)


# ETL 
def extract():

    orders = pd.read_csv('data/orders_formatted/order_details.csv', sep=';')
    df_orders = pd.read_csv('data/orders_formatted/orders.csv', sep=';')
    df_ingredients = pd.read_csv('data/pizza_types.csv',encoding = "ISO-8859-1")
    df_pizzas = pd.read_csv('data/pizzas.csv')


    # dtypes of each dataset to json
    types = {'object': 'str', 'int64': 'int', 'float64': 'float', 'datetime64[ns]': 'datetime'}
    df_list = [orders, df_orders, df_ingredients, df_pizzas]
    df_names = ['order_details.csv', 'orders.csv', 'pizza_types.csv', 'pizzas.csv']
    dtypes = {'dtypes': {}}
    for dataset in range(len(df_list)):
        dtypes['dtypes'][df_names[dataset]] = df_list[dataset].dtypes.apply(lambda x: types[x.name]).to_dict()
    json.dump(dtypes, open('resources_created/dtypes.json', 'w'))

    return orders, df_orders, df_ingredients, df_pizzas

def transform(orders: pd.DataFrame, df_orders: pd.DataFrame, df_ingredients: pd.DataFrame, df_pizzas: pd.DataFrame):

    #date to datetime
    for date in range(len(df_orders['date'])):
        try:
            df_orders['date'][date] = pd.to_datetime(df_orders['date'][date], errors='ignore').date()
        except:
            df_orders['date'][date] = datetime.fromtimestamp(float(df_orders['date'][date])).date()


    # data quality check
    print('Data quality check:')
    print('Number of nulls in orders:',orders.isnull().sum().sum())
    print('Number of nulls in df_orders:',df_orders.isnull().sum().sum())
    print('Number of nulls per column in...')
    datas = {'orders': orders, 'df_orders': df_orders}
    for ds_name, ds in datas.items():
        print(ds_name.upper() + ':')
        for column in ds.columns:
            print('\t- ',column,':',ds[column].isnull().sum())

    df_orders = df_orders[df_orders['date'].isnull() == False]
    df_orders.sort_values(by=['date','order_id'], inplace=True)
    orders = orders[orders['pizza_id'].isnull() == False]


    # Getting the sizes of each pizza
    pizza_id = []
    pizza_type = []
    for pizza in list(orders['pizza_id']):
        pizza = pizza.replace('@', 'a').replace('3', 'e').replace('0', 'o')
        temp = re.split('[\_\-\s]',pizza)
        pizza_type.append(temp[-1].upper())
        temp.remove(temp[-1])
        pizza_id.append('_'.join(temp))
    orders['pizza_id'] = pizza_id
    orders['pizza_size'] = pizza_type

    quantity = []
    for i in orders['quantity']: 
        if i != '1' and i != 'One' and i != 'one' and type(i) != float and i != '-1' and i != '2' and i != '3' and i != 'two' and i != '4' and i != '-2':
            print(i)
        if type(i) != float:       
            i = i.replace('One', '1').replace('one', '1').replace('two', '2').replace('three', '3').replace('four', '4')
            i = abs(int(i))
        else:
            i = 1 # if the quantity is null, we assume it's 1 because it's the most common case (calculated with the mean)
        quantity.append(i)
    orders['quantity'] = quantity



    # Merging datasets
    orders = orders.groupby('order_id').agg(list)
    orders = orders.drop(columns=['order_details_id'])
    orders = orders.merge(df_orders, on='order_id')
    orders = orders.drop(columns=['order_id'])


    # Ordering values by date
    pizza_orders = orders[['pizza_id','quantity', 'pizza_size','date']]
    pizza_orders = pizza_orders.groupby('date').sum().sort_values(by='date')


    # Grouping pizzas by type

    # Getting the ingredients for each pizza size
    ingredients = []
    sizes= {'S':1, 'M':1.5, 'L':2, 'XL':2.5, 'XXL':3}

    for day in range(len(pizza_orders['pizza_id'])):
        pizza_list = pizza_orders['pizza_id'][day]

        temp1 = []
        temp2 = []
        temp3 = []

        for i in range(len(pizza_list)):
            if pizza_list[i] not in temp1 or (pizza_list[i] in temp1 and temp3[temp1.index(pizza_list[i])]) != pizza_orders['pizza_size'][day][i]:
                temp1.append(pizza_list[i])
                temp2.append(pizza_orders['quantity'][day][i])
                temp3.append(pizza_orders['pizza_size'][day][i])
            else:
                temp2[temp1.index(pizza_list[i])] += pizza_orders['quantity'][day][i]
        
        # Getting the ingredients for each day
        day_ingredients = {}
        for pizza in range(len(pizza_list)):
            t = list(df_ingredients[df_ingredients['pizza_type_id'] == pizza_list[pizza]]['ingredients'])[0]
            for i in t.split(', '):
                if i in day_ingredients:
                    day_ingredients[i] += sizes[pizza_orders['pizza_size'][day][pizza]]*temp2[temp1.index(pizza_list[pizza])]
                else:
                    day_ingredients[i] = sizes[pizza_orders['pizza_size'][day][pizza]]*temp2[temp1.index(pizza_list[pizza])]
            for key,value in day_ingredients.items():
                day_ingredients[key] = int(round(value, 0))
        ingredients.append(day_ingredients)
    

        pizza_orders['pizza_id'][day] = temp1
        pizza_orders['quantity'][day] = temp2
        pizza_orders['pizza_size'][day] = temp3
        

    pizza_orders['ingredients'] = ingredients
    

    # Getting the week number of each day
    week = []
    for i in range(len(pizza_orders)):
        doy = pizza_orders.iloc[i].name.timetuple().tm_yday
        w = (doy) // 7
        week.append(w)
    pizza_orders['week'] = week
    pizza_orders.insert(0, 'week', pizza_orders.pop('week'))

    # We take all the ingredients and put them in a list
    total_ingredients = []
    for i in df_ingredients['ingredients']:
        total_ingredients += i.split(', ')
    total_ingredients = list(set(total_ingredients))
    ingredients_w = ingredients_per_week(pizza_orders)
    return pizza_orders, total_ingredients, ingredients_w
    
def load(pizza_orders, total_ingredients, ingredients_w):
    pizza_orders.to_csv('resources_created/pizza_orders.csv')
    weekly_ing = prediction_week(total_ingredients, ingredients_w)
    return weekly_ing

def merge_data(pizza_orders, total_ingredients, ingredients_w):
    import orders_2015 as o15
    ords15 = o15.main()
    all_orders = pd.concat([ords15,pizza_orders])
    all_orders['date'] = all_orders.index

    all_orders.drop(columns=['week'], inplace=True)
    week = []
    for i in range(len(all_orders)):
        doy = all_orders.iloc[i].name.timetuple().tm_yday
        if all_orders['date'][i].year == 2015:
            w = (doy-1) // 7
        else:
            w = (doy) // 7 + 52
        
        week.append(w)
    all_orders['week'] = week
    all_orders.insert(0, 'week', all_orders.pop('week'))
    all_orders.set_index('date', inplace=True)
    

    ingredients_w = ingredients_per_week(all_orders)
    return all_orders, total_ingredients, ingredients_w

# PLOTTING THE DATA
def ingredients_per_week(pizza_orders: pd.DataFrame):
    # Creating a list of dictionaries with the ingredients and their quantities per week

    ingredients_w = []
    for week in range(pizza_orders['week'].max()+1):
        ingredients_w.append({})
        for day in pizza_orders[pizza_orders['week']==week].iterrows(): 
            for key, value in day[1]['ingredients'].items():
                if key in ingredients_w[week]:
                    ingredients_w[week][key] += value
                else:
                    ingredients_w[week][key] = value
    return ingredients_w


def graphing_ingredients_week(total_ingredients: list, weekly_ing: list, week: int):
    # graph of ingredients per week
    plt.figure(figsize=(10,14))
    plt.xlabel('Weeks')
    plt.ylabel('Quantity')
    x = np.array(total_ingredients)
    y = np.array([weekly_ing[i][week] for i in total_ingredients])
    plt.barh(x, y, color='green')
    plt.show()


def prediction_week(total_ingredients: list, ingredients_w: list):
    #Initialize the stock for each ingredient
    stock = {}
    for i in total_ingredients:
        stock[i] = [0,0] # [quantity left, average consumption per week]

    # For plotting a random ingredient
    x_axis = np.array(range(len(ingredients_w)))
    stock_ing = []
    ing = random.randint(0, len(total_ingredients)-1)

    weekly_ing = pd.DataFrame()
    weekly_ing['week'] = range(len(ingredients_w))
    for i in total_ingredients:
        weekly_ing[i] = [0 for _ in range(len(ingredients_w))]

    # An example of how we would predict for more data
    for week in range(len(ingredients_w)):
        for i in range(len(total_ingredients)):
            # We update the average of all the weeks before 
            stock[total_ingredients[i]][1] = stock[total_ingredients[i]][1]*week + ingredients_w[week][total_ingredients[i]]
            stock[total_ingredients[i]][1] = stock[total_ingredients[i]][1]/(week+1)
            if week == 0:
                stock[total_ingredients[i]][1] = int(ingredients_w[week][total_ingredients[i]]*1.2)

            # The week passes and ingredients are taken
            stock[total_ingredients[i]][0] -= ingredients_w[week][total_ingredients[i]]

            # The stock is updated to 1.6 times the average of the past weeks
            p = 1.6 - stock[total_ingredients[i]][0]/stock[total_ingredients[i]][1]
            stock[total_ingredients[i]][0] += stock[total_ingredients[i]][1]*p # adding the stock for the next week
            
            # For graphing
            weekly_ing[total_ingredients[i]][week] = round(stock[total_ingredients[i]][1]*p)
            if i == ing:
                stock_ing.append(stock[total_ingredients[ing]][0])

    # Graph of stock of one random ingredient
    plt.figure(figsize=(14,5))
    plt.title('Ingredients per week')
    plt.xlabel('Weeks')
    plt.ylabel('Quantity')
    ing = total_ingredients[ing]
    x = np.array(range(len(ingredients_w)))
    y = np.array([ingredients_w[i][ing] for i in range(len(ingredients_w))])
    plt.ylim(0, y.max()*1.7)
    plt.plot(x_axis, stock_ing, label=f'stock of {ing}')
    plt.plot(x, y, label=ing)

    plt.legend()
    plt.show()
    weekly_ing.set_index('week', inplace=True)
    weekly_ing.to_csv('resources_created/weekly_ing.csv')

    return weekly_ing

if __name__ == '__main__':
    orders, df_orders, df_ingredients, df_pizzas = extract()
    pizza_orders, total_ingredients, ingredients_w  = transform(orders, df_orders, df_ingredients, df_pizzas)
    all_orders, total_ingredients, ingredients_w = merge_data(pizza_orders, total_ingredients, ingredients_w)
    weekly_ing = load(all_orders, total_ingredients, ingredients_w)
    os.system('clear||cls')
    wish = ''
    while wish != 'y' or wish != 'n':
        wish = input('Do you wish to know what to order for the next week (y/n)? ')
        if wish == 'y':
            print('What is today\'s date?')
            date = input('Enter a date in the format YYYY-MM-DD: ')
            
            if date.split('-')[0] != '2015' and date.split('-')[0] != '2016':
                print('Year not valid')
                continue
          
            try:
                date = datetime.strptime(date, '%Y-%m-%d')
            except:
                print('Wrong date format')
                continue

            doy = date.timetuple().tm_yday
            if date.year == 2015:
                w = (doy-1) // 7
            else:
                w = (doy) // 7 + 52
            with open(f'resources_created/order-w{w}.txt','w') as f:
                for ingredient in weekly_ing.columns:
                    f.write(f'{ingredient}: {weekly_ing[ingredient][w]}\n')
                    
                print('The order has been saved in the file order.txt')
                f.close()
        elif wish == 'n':
            exit()
        else:
            print('Please enter a valid input')

