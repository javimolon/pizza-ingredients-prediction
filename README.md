# Pizza ingredients prediction
In this pipeline we take datasets of various data such as order details, pizza ingredients or date of order and we try to predict the ingredients we will need to buy for the following week.

## Before running the code
You need to have python 3.6+ installed on your machine. You can download it [here](https://www.python.org/downloads/).
For this program to run you need to install the packages listed in the requirements.txt file. You can do this by running the following command in your terminal:
```bash
pip3 install -r requirements.txt
```

## How to run the code
To run the code you need to run the following command in your directory terminal:
```bash
python3 code/all_orders.py
```

# Documentation
The program is based in an ETL pipeline. The data is extracted from the csv files, transformed into a pandas dataframe and loaded into a images.

## Data
The data is stored in the data folder. There are 7 csv files: 1 which describes the other csv files, 2 for information about the pizzas; 2 for the orders of 2015, which are used in the `orders_2015.py` file; and 2 for the orders of 2016, which are used in the `all_orders.py` file. These last two files haven't been cleaned, so they get cleaned in the `all_orders.py`. For information about the csv files, check the `data_dictionary.csv` file.

## How the prediction is made
The prediction is based on all the previous weeks, taking the average of the ingredients we sold each week. We then round the result to the closest integer, and, to make   sure we always have enough stock of ingredients, we buy 60% more than the average. This way we are sure to have enough ingredients for the next week. 

## Where to find the results
We offer various results:
- A cleaned csv file with all the information we need to make the prediction for each week of 2016
- A csv file with the ingredients we have ordered each week, predicted by our program
- Three graphs showing the evolution of the quantity of ingredients ordered each week and the stock of ingredients we have each week
- A barplot showing last week's order 
- A json file offering the types of data in each column

They are all found in the directory `code/resources_created` 
