"""
Pure python imagehash.

Source: https://github.com/bkda/ImageHash/blob/master/imglib.py

Used instead of imagehash package to remove the scipy dependency.
"""

from functools import reduce
from PIL import Image


def dct_coefficients(data, upper_left=8):
    """
    Get the dct.

    :param data:
    :param upper_left: use upper left corner
    :return:
    """
    from math import cos, pi, sqrt

    A, M, N = [], 32, 32
    coefficients = []
    for i in range(32):
        A.append([data.pop(0) for j in range(32)])

    for p in range(upper_left):
        tmp = []
        alpha_p = sqrt(1 / M)
        if p != 0:
            alpha_p = alpha_p * sqrt(2)
        for q in range(upper_left):
            alpha_q = sqrt(1 / N)
            if q != 0:
                alpha_q = alpha_q * sqrt(2)
            b = sum(
                [
                    A[m][n]
                    * cos(pi * (2 * m + 1) * p / 2 / M)
                    * cos(pi * (2 * n + 1) * q / 2 / N)
                    for m in range(M)
                    for n in range(N)
                ]
            )

            tmp.append(alpha_p * alpha_q * b)
        coefficients.append(tmp)
    return coefficients


def perceptiveHash(img):
    """
    Compute the pHash.

    :param img:
    :return: the upper left corner of the DCT,default return 8x8 coefficient matrix
              It can reduce the computational time efficiently.
    """
    if not isinstance(img, Image.Image):
        img = Image.open(img)
    im = img.resize((32, 32), Image.ANTIALIAS).convert("L")
    da = list(im.getdata())
    matrx = dct_coefficients(da)
    avg = sum([e for r in matrx for e in r]) / 64

    binary_list = [0 if e < avg else 1 for r in matrx for e in r]
    hs = reduce(lambda x, y_z: x | (y_z[1] << y_z[0]), enumerate(binary_list), 0)

    return hs
