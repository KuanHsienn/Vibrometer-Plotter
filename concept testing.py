import numpy as np
import data_tools as dt


input_array = np.array([1, 2, 3, 0.0000023, 0.0000017])
print(input_array)

output_array = dt.array_to_decibel(input_array, 1)

print(output_array)







