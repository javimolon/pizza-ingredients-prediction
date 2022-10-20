# Pizza ingredients prediction
In this pipeline we take datasets of various data such as order details, pizza ingredients or date of order and we try to predict the ingredients we will need to buy for the following week.

# Before running the code
You need to have some libraries installed: pandas and numpy. You can install them with the following command:
```bash
pip3 install pandas numpy
```

## How the prediction is made
The prediction is based on all the previous weeks, taking the average of the ingredients we sold each week. We then round the result to the closest integer, and, to make sure we always have enough stock of ingredients, we buy 60% more than the average. This way we are sure to have enough ingredients for the next week. 

## Where to find the results
After running the code, you will find a file called `prediction.csv` in the `data` folder. This file contains the ingredients we needed to buy for each week in 2015.