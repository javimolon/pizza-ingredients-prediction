import pandas as pd
import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def main():
    orders = pd.read_csv('data/order_details.csv')
    df_orders = pd.read_csv('data/orders_original.csv')
    df_ingredients = pd.read_csv('data/pizza_types.csv',encoding = "ISO-8859-1")
    df_pizzas = pd.read_csv('data/pizzas.csv')



    for date in range(len(df_orders['date'])):
    
        
        df_orders['date'][date] = pd.to_datetime(df_orders['date'][date]).date()
        
    # Getting the sizes of each pizza
    pizza_id = []
    pizza_type = []
    for pizza in list(orders['pizza_id']):
        temp = pizza.split('_')
        pizza_type.append(temp[-1].upper())
        temp.remove(temp[-1])
        pizza_id.append('_'.join(temp))
    orders['pizza_id'] = pizza_id
    orders['pizza_size'] = pizza_type

    # Merging datasets



    orders = orders.groupby('order_id').agg(list)
    orders = orders.drop(columns=['order_details_id'])
    orders = orders.merge(df_orders, on='order_id')
    orders = orders.drop(columns=['order_id'])

    
    pizza_orders = orders[['pizza_id','quantity', 'pizza_size','date']]
    pizza_orders = pizza_orders.groupby('date').sum()
    
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

    return pizza_orders

if __name__ == '__main__':
    print(main())
