import pandas


def load_indexed_csv(index_column, file_path):
    """
    Loads a CSV file and converts it into a dictionary indexed by the specified column.

    :param index_column: Name of the column to be used as the index.
    :param file_path: Path to the CSV file.
    :return: A dictionary indexed by the specified column.
    """
    try:
        # Load the CSV file into a pandas DataFrame
        df = pandas.read_csv(file_path)

        # Check if the column exists in the DataFrame
        if index_column not in df.columns:
            raise ValueError(f"The column '{index_column}' does not exist in the CSV file.")

        # Convert the DataFrame into a dictionary indexed by the specified column
        meta_dict = df.set_index(index_column).to_dict(orient='index')

        return meta_dict
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{file_path}' was not found.")
    except Exception as e:
        raise Exception(f"Error loading the CSV file: {e}")