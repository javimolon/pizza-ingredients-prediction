from datetime import date
from genericpath import exists
import pandas as pd
import os
# Read the data
def extract(e):
    orders = pd.read_csv('order_details.csv')
    df_orders = pd.read_csv('orders_original.csv')
    df_ingredients = pd.read_csv('pizza_types.csv',encoding = "ISO-8859-1")
    df_pizzas = pd.read_csv('pizzas.csv')
    
    
    if not e:

        # Merge the data
        pizza_id = []
        pizza_type = []
        for pizza in list(orders['pizza_id']):
            temp = pizza.split('_')
            pizza_type.append(temp[-1].upper())
            temp.remove(temp[-1])
            pizza_id.append('_'.join(temp))

            
        orders['pizza_id'] = pizza_id
        orders['pizza_type'] = pizza_type

        orders = orders.groupby('order_id').agg(list)
        orders = orders.drop(columns=['order_details_id'])
        orders = orders.merge(df_orders, on='order_id')
        orders = orders.drop(columns=['order_id'])

        ingredients = []
        for pizzas in list(orders['pizza_id']):
            temp = ''
            a = list(orders['pizza_id']).index(pizzas)
            for pizza in pizzas:
                t = list(df_ingredients[df_ingredients['pizza_type_id'] == pizza]['ingredients'])[0]
                temp += t + ', '
            ingredients.append(temp[:-2])
        orders['ingredients'] = ingredients
        orders.to_csv('orders.csv', index=False)
            
    else:
        orders = pd.read_csv('orders.csv')
        for i in orders['quantity']:
            i = eval(i)
        for i in orders['pizza_type']:
            i = eval(i)
    
    pizza_orders = orders[['pizza_id','quantity', 'pizza_type','date']]

    pizza_orders = pizza_orders.groupby('date').sum().sort_values(by='date')
    print(pizza_orders.head())
        

    return orders, df_ingredients, df_pizzas
        

            
    
    


if __name__ == '__main__':
    # check if a file doesn't exist in the directory
    e = os.path.exists('orders.csv')
    orders, df_orders, df_ingredients = extract(e)
    