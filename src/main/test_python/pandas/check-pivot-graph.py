import pymongo
from datetime import datetime, timezone, timedelta
import pytz
import os
import argparse
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    png_file_path = os.environ['HOME'] + os.path.sep + "Desktop" + os.path.sep + "output.png"
    df = pd.DataFrame({"A": ["foo", "foo", "foo", "foo", "foo",
                             "bar", "bar", "bar", "bar"],
                       "B": ["one", "one", "one", "two", "two",
                             "one", "one", "two", "two"],
                       "C": ["small", "large", "large", "small",
                             "small", "large", "small", "small",
                             "large"],
                       "D": [1, 2, 2, 3, 3, 4, 5, 6, 7],
                       "E": [2, 4, 5, 5, 6, 6, 8, 9, 9],
                       "F": ["a", "a", "a", "a", "a", "a", "a", "a", "a"]
                       })
    print(df)
    print("")
    table = pd.pivot_table(df, values='D', index=['A', 'B'], columns=[
                           'C'], aggfunc=np.sum, fill_value=0)
    print(table)
    #x = np.linspace(0, 20, 100)
    #plt.plot(x, np.sin(x))       # Plot the sine of each x point
    #plt.show()                   # Display the plot
    table.plot()
    print("Write a graph to " + png_file_path)
    plt.savefig(png_file_path)

