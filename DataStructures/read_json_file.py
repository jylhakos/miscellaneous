# Pandas can read JavaScript Object Notation (JSON) files using the read_json() function. 
# This function can handle various JSON structures, including single JSON objects, 
# JSON arrays, and line-delimited JSON.
# The read_json() function is used for converting JSON data into a Pandas's DataFrame.
# The read_json() function takes a JSON file and returns a DataFrame or Series. 
# https://pandas.pydata.org/docs/reference/api/pandas.read_json.html

import pandas as pd

# Read a JSON file into a DataFrame
df = pd.read_json('data.json')

# Print the DataFrame
print(df)

# The read_json() function has several parameters that can be used to customize how the JSON data is read. 
# Some common parameters include:

# path_or_buf: The path to the JSON file or a file-like object.

# orient: The expected format of the JSON string. Possible values include:

# 'records' (default): List like [{column: value}, ...].

# 'index': Dict like {index: {column: value}}.

# 'columns': Dict like {column: {index: value}}.

# 'values': Just the raw values array.

# 'split': Dict like {index: [index], columns: [columns], data: [values]}.

# lines: If set to True, reads the file as a JSON object per line.

# compression: If set, decompresses the data on-the-fly.

import pandas as pd

# Read a line-delimited JSON file
df = pd.read_json('data.json', lines=True)

# Read a compressed JSON file
df = pd.read_json('data.json.gz', compression='gzip')

# For reading JSON data present in the remote file, we can use the read_json() function of the Pandas 
# library and then pass the URL of the file as the parameter to the read_json() function. 

# Here is how to read JSON files into NumPy arrays using the Apache Arrow library in Python

# https://arrow.apache.org/docs/python/json.html

# Arrow supports reading columnar data from line-delimited JSON files. 

# Install pyarrow: If you don't have it installed, use pip install pyarrow

    import pyarrow.json as pajson
    import numpy as np

# Read JSON file: 

# Use pyarrow.json.read_json() to read the JSON file into an Arrow table. 

# This function expects a line-delimited JSON format where each line is a separate JSON object.

    file_path = 'your_data.json'
    arrow_table = pajson.read_json(file_path)

# Convert to NumPy array: Convert the Arrow table to a NumPy array using to_numpy(). 

# This method works efficiently for primitive types without nulls. 

# For more complex types or data with nulls, consider using to_pandas() first and then converting to a NumPy array.

    numpy_array = arrow_table.to_numpy()

# If you have mixed data types, you can iterate through the columns and convert them individually:

    numpy_arrays = [col.to_numpy() for col in arrow_table.columns]

# Handle errors: Ensure your JSON file is correctly formatted (line-delimited) and handle potential exceptions during file reading and conversion.

# Here's an  example:

import pyarrow.json as pajson
import numpy as np

# Create a dummy JSON file (line-delimited)
with open('your_data.json', 'w') as f:
    f.write('{"a": 1, "b": 2.0, "c": "foo"}\n')
    f.write('{"a": 4, "b": -5.5, "c": null}\n')

try:
    file_path = 'your_data.json'
    arrow_table = pajson.read_json(file_path)
    numpy_arrays = [col.to_numpy() for col in arrow_table.columns]
    print(numpy_arrays)
except Exception as e:
    print(f"An error occurred: {e}")


# Comma Separated Values (CSV), which is a plain text file containing some list of values.

