import statistics as st
import scipy as scp
import numpy as np

# Necesito hacer ajustes y sacar todos los datos posibles de estos
def fit(x_ax, y_ax, order):
    coef = np.polyfit(x_ax, y_ax, i)
    y_pred = np.polyfit(coef, x_ax)
    return coef, y_pred
    
# Comparing the different fit orders and choosing the best one
def best_fit(x_ax, y_ax, max_order, min_r2):
    best_order = 1

    r2_hist = np.array([])
    order_hist = np.array([])

    for i in range(1, max_order+1):
            fit(x_ax, y_ax, i)

            # Calculation of R^2
            rss = np.sum((y_ax - fit(x_ax, y_ax, i)[1])**2) 
            tss = np.sum((y_ax - np.mean(y_ax))**2)
            r2 = 1 - (rss / tss)

            # Condition to only get fits with a r2 threshold
            if r2 >= min_r2:
                np.append(r2_hist, r2)
                np.append(order_hist, i)

    best = np.index(min(r2_hist))

    best_order = order_hist[best]
    best_r2 = r2_hist[best]

    return np.polyval(x_ax, fit(x_ax, y_ax, best_order)), best_r2 




