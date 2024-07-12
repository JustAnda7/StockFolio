import numpy as np
import matplotlib.pyplot as plt

class LocallyWeightedRegression:
    #maths behind Linear Regression:
    # theta = inv(X.T*W*X)*(X.T*W*Y)this will be our theta whic will 
    # be learnt for each point
    # initializer of LocallyWeighted Regression that stores tau as parameters
    def __init__(self, tau = 0.01):
        self.tau = tau
    def kernel(self, query_point, X):
        Weight_matrix = np.mat(np.eye(len(X)))
        for idx in range(len(X)):
            # check for inf values
            Weight_matrix[idx,idx] = np.exp(-(np.dot(X[idx]-query_point, (X[idx]-query_point).T))/(-2*self.tau*self.tau))
        return Weight_matrix
    # function that makes the predictions of the output of a given query point
    def predict(self, X, Y, query_point):
        q = np.hstack([query_point, 1])
        X = np.hstack((X, np.ones((len(X), 1))))
        W = self.kernel(q, X)
        theta = np.linalg.pinv(X.T*(W*X))*(X.T*(W*Y))
        pred = np.dot(q, theta)
        return pred
    #function that fits and predicts the output of all query points
    def fit_and_predict(self, X, Y, X_test):
        Y_test = np.zeros(shape=(len(X_test), 1))
        i = 0
        for x in X_test:
            pred = self.predict(X, Y, x)
            Y_test[i] = pred[0]
            Y = np.append(Y, pred[0])
            X = np.append(X, x)
            i += 1
#         Y_test = np.array(Y_test)
        return Y_test
    # function that computes the score rmse
    def score(self, Y, Y_pred):
        return np.sqrt(np.mean((Y-Y_pred)**2))
    # function that fits as well as shows the scatter plot of all points
    def fit_and_show(self, X, Y):
        Y_test, X_test = [], np.linspace(-np.max(X), np.max(X), len(X))
        for x in X_test:
            pred = self.predict(X, Y, x)
            Y_test.append(pred[0][0])
        Y_test = np.array(Y_test)
        plt.style.use('seaborn')
        plt.title("The scatter plot for the value of tau = %.5f"% self.tau)
        plt.scatter(X, Y, color = 'red')
        plt.scatter(X_test, Y_test, color = 'green')
        plt.show()