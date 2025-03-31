import statistics as st
import scipy as scp
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline


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

# Mean and coefficient of variation

def mean_data(data):
     m = np.mean(data)
     std = 






# Bicubic interpolation
def bcb_interp(x_ax, y_ax, z_ax):
    
    # Crear interpolador bicúbico
    interp = RectBivariateSpline(x_ax, y_ax, z_ax)

# Crear una grilla más fina para la interpolación
    x_fine = np.linspace(0, 10, 50)
    y_fine = np.linspace(0, 10, 50)
    X_fine, Y_fine = np.meshgrid(x_fine, y_fine)
    Z_fine = interp(x_fine, y_fine)

# Graficar
    plt.figure(figsize=(8,6))
    plt.pcolormesh(X_fine, Y_fine, Z_fine, shading='auto', cmap='viridis')
    plt.colorbar(label='Interpolación')
    plt.scatter(x_ax, y_ax, color='red', label='Puntos originales')
    plt.legend()    
    plt.title('Interpolación Bicúbica')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()

