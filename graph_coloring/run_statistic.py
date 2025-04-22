import os
from graph_coloring_solver import *
import pandas as pd
import threading
import time

# .\venv\Scripts\Activate

def cal_density(G):
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = 2 * num_edges / num_nodes / (num_nodes - 1)

    return density

def load_or_create_dataframe(filename):
    columns = [
        "nodes", "edges", "density", "name",
        "ds_colors", "ds_time", "opt_colors", "opt_time",
        "ds_diff_0_colors", "ds_diff_0_time", "opt_diff_0_colors", "opt_diff_0_time",
        "ds_diff_1_colors", "ds_diff_1_time", "opt_diff_1_colors", "opt_diff_1_time",
        "ds_diff_2_colors", "ds_diff_2_time", "opt_diff_2_colors", "opt_diff_2_time",
    ]

    os.makedirs("output_2", exist_ok=True)
    filename = f"output_2/{filename}"

    if os.path.exists(filename):
        df = pd.read_csv(filename)
        print(f"Loaded existing file: {filename}")
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)
        print(f"File not found. Created new file: {filename}")

    return df


def run_with_timeout(graph, n, opt, timeout=120):
    result = [None]

    def target():
        if opt == 1:
            result[0] = run_solving(graph, n, opt)
        else:
            return None

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print("Timeout! Stopping execution.")
        return None
    return result[0]


def main():
    df = load_or_create_dataframe("output.csv")
    data_folder = "data"
    results = []

    for folder_name in sorted(os.listdir(data_folder)):
        if folder_name not in ["n_50_p_50"]:
            continue
        folder_path = os.path.join(data_folder, folder_name)

        if os.path.isdir(folder_path):
            for file_name in sorted(os.listdir(folder_path)):
                file_path = os.path.join(folder_path, file_name)

                if os.path.isfile(file_path):
                    file_name_full = f"data/{folder_name}/{file_name}"

                    graph = read_from_csv_file(file_name_full)
                    print("Graph loaded:", graph)
                    print(f"name of file: {file_name}")

                    nodes = graph.number_of_nodes()
                    edges = graph.number_of_edges()
                    density = cal_density(graph)

                    result_dict = {
                        "nodes": nodes,
                        "edges": edges,
                        "density": density,
                        "name": file_name
                    }

                    existing_rows = df[df["name"] == file_name]

                    for opt in range(0, 2):
                        for diff in range(-1, 3):

                            if diff != -1:
                                key_color = f"ds_diff_{diff}_colors" if opt == 0 else f"opt_diff_{diff}_colors"
                                key_time = f"ds_diff_{diff}_time" if opt == 0 else f"opt_diff_{diff}_time"
                            else:
                                key_color = f"ds_colors" if opt == 0 else f"opt_colors"
                                key_time = f"ds_time" if opt == 0 else f"opt_time"

                            if not existing_rows.empty and pd.notna(existing_rows.iloc[0].get(key_color)) and pd.notna(
                                    existing_rows.iloc[0].get(key_time)):
                                print(f"Skipping {file_name}, opt={opt}, diff={diff} (already processed)")
                                result_dict[key_color] = existing_rows.iloc[0][key_color]
                                result_dict[key_time] = existing_rows.iloc[0][key_time]
                                continue

                            start_time = time.time()
                            chromatic_number = run_with_timeout(graph, diff, opt, timeout=600)
                            end_time = time.time()
                            execution_time = end_time - start_time
                            if chromatic_number is None:
                                execution_time = None

                            result_dict[key_color] = chromatic_number
                            result_dict[key_time] = execution_time

                    results.append(result_dict)

    if results:
        df = pd.concat([df, pd.DataFrame(results)], ignore_index=True)
        df.to_csv("output_2/output.csv", index=False)
        print("Results saved to output.csv")


if __name__ == "__main__":
    main()
