import math

D = 1.7


def prob_3pl(theta, a, b, c):
    exp_term = math.exp(D * a * (theta - b))
    return c + (1 - c) * (exp_term / (1 + exp_term))


def fisher_information(theta, a, b, c):

    p = prob_3pl(theta, a, b, c)
    q = 1 - p

    return (D ** 2) * (a ** 2) * ((q / (1 - c)) ** 2) * ((p - c) / p)


def update_theta_mle(theta, items, responses):

    for _ in range(8):

        num = 0
        den = 0

        for item in items:

            iid = item["id"]

            if iid not in responses:
                continue

            u = responses[iid]

            a = item["a"]
            b = item["b"]
            c = item["c"]

            p = prob_3pl(theta, a, b, c)

            num += a * (u - p)
            den += (a ** 2) * p * (1 - p)

        if den != 0:
            theta += num / den

    return theta
