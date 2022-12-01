# Pizza ingredients prediction
In this pipeline we take datasets of various data such as order details, pizza ingredients or date of order and we try to predict the ingredients we will need to buy for the following week.

### Before running the code
You will need to have a program that runs .ipynb files like VSC. 
You will also need to have some libraries installed: pandas and numpy and matplotlib. You can install them with the following command:
```bash
pip3 install -r requirements.txt
```

## How the prediction is made
The prediction is based on all the previous weeks, taking the average of the ingredients we sold each week. We then round the result to the closest integer, and, to make   sure we always have enough stock of ingredients, we buy 60% more than the average. This way we are sure to have enough ingredients for the next week. 

## Where to find the results
We offer various results:
- A cleaned csv file with all the information we need to make the prediction for each week
- A csv file with the ingredients we have ordered each week, predicted by our program
- Three graphs showing the evolution of the quantity of ingredients ordered each week and the stock of ingredients we have each week
- A barplot showing last week's order 

They are all found in the directory "code/resources_created" 