import matplotlib.pyplot as plt
import numpy as np

y = np.array([36, 25, 25, 15])
mylabels = ["Apples", "Bananas", "Cherries", "Dates"]



def create_pie(values, mylabels):
    pie = plt.pie(values, labels = mylabels, autopct='%1.0f%%')
    return pie

# create_pie(y, mylabels)