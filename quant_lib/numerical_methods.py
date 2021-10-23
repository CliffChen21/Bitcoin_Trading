from functools import reduce
import numpy as np


def taylor_expansion_approximation(r, t, order):
    max_iter = 10
    r = np.matrix(r)
    t_mat = np.matrix([[ti ** i for ti in t] for i in range(order)])
    params_vector = np.matrix([[0.01]] * order)
    for i in range(max_iter):
        derivative = 2 * np.dot(t_mat, t_mat.T).dot(params_vector)
        derivative = derivative / sum(derivative)
        params_vector = params_vector - derivative
        error = t_mat.T.dot(params_vector) - r
        print("derivatives: {}".format(derivative))
        print("params: {}".format(params_vector))
        print("error: {}".format((sum(error))))
    print(params_vector)
    return params_vector


taylor_expansion_approximation([0.1, 0.21, 0.321], [1, 2, 3], 1)
