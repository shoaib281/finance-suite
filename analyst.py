# go through top n stocks
# compute score
# get actual performance
# plot this on a scatter graph?


import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

from utils import top_n_tickers
from price_updater import percent_change_close_dataframe


def compute_recommendation_score(recommendation):
    res = 0

    count = (recommendation.strongBuy +
             recommendation.buy + recommendation.hold + recommendation.sell + recommendation.strongSell)

    if count == 0:
        return False

    res += (recommendation.strongBuy * 2) / count
    res += (recommendation.buy * 1) / count
    res += (recommendation.hold * -1) / count
    res += (recommendation.sell * -2) / count
    res += (recommendation.strongSell * -3) / count

    if count == 0:
        return False

    return res

def main(n=1000):

    top_stocks = top_n_tickers(n)

    scores = np.array([])
    price_changes = np.array([])

    for i in range(n):
        ticker = top_stocks[i]

        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations_summary

        if len(recommendations) >= 4:


            recommendation = recommendations.loc[0]

            score = compute_recommendation_score(recommendation)
            if score is False:
                print("Invalid recommendation scores", recommendation)
                continue

            scores = np.append(scores, [score])

            price_change = percent_change_close_dataframe(stock.history(period="3mo")) * 100
            price_changes = np.append(price_changes, [price_change])

    plt.figure(figsize=(8, 6))  # Optional: Adjusting figure size
    plt.scatter(scores, price_changes, color='blue', marker='o', label='Data Points')

    # Adding labels and title
    plt.title('Scatter Plot Example')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.axhline(y=0, color='k', linewidth=0.5)  # Draw horizontal axis
    plt.axvline(x=0, color='k', linewidth=0.5)  # Draw vertical axis

    slope, intercept, r_value, p_value, std_err = linregress(scores, price_changes)
    line = (slope * scores) + intercept
    plt.plot(scores, line, color='red', label='Line of best fit')

    correlation_strength = r_value ** 2

    print("Correlation string ", correlation_strength)

    plt.show()

if __name__ == "__main__":
    main()
