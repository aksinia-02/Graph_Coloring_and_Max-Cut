import os
from graph_coloring.graph_coloring_solver import *
from max_cut.max_cut_solver import *
import pandas as pd
import time
import multiprocessing
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools import read_from_csv_file

# .\venv\Scripts\Activate

def cal_density(G):
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    density = 2 * num_edges / num_nodes / (num_nodes - 1)

    return density


def load_or_create_dataframe(filename, type):
    if type == 1:
        columns = [
            "nodes", "edges", "density", "name",
            "colors", "time", "offset_0_colors", "offset_0_time",
            "offset_1_colors", "offset_1_time", "offset_2_colors", "offset_2_time",
        ]
    else:
        columns = [
            "nodes", "edges", "density", "name",
            "cut_size", "time", "offset_0_cut_size", "offset_0_time",
            "offset_1_cut_size", "offset_1_time", "offset_2_cut_size", "offset_2_time",
        ]

    os.makedirs("output", exist_ok=True)
    filename = f"output/{filename}"

    if os.path.exists(filename):
        df = pd.read_csv(filename)
        print(f"Loaded existing file: {filename}")
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)
        print(f"File not found. Created new file: {filename}")

    return df

def target_func(result, type, graph, n, opt, folder_path):
    if type == 1:
        result[0] = run_solving_graph_coloring(graph, n, opt, folder_path)
    else:
        result[0] = run_solving_max_cut(graph, n, opt, folder_path)


def run_with_timeout(type, graph, n, opt, timeout=120, full_file_path=None):
    manager = multiprocessing.Manager()
    result = manager.list([None])

    process = multiprocessing.Process(target=target_func, args=(result, type, graph, n, opt, full_file_path))
    process.start()
    process.join(timeout)

    if process.is_alive():
        print("Timeout! Stopping execution.")
        process.terminate()
        process.join()
        return None

    return result[0]


def main():
    parser = argparse.ArgumentParser(description="Generate some random graphs.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output file for results.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input folder with data.")
    parser.add_argument("-t", "--type", type=int, choices=[0, 1], required=True,
                        help="Set to 1 if graph coloring are required, otherwise 0 for max cut.")
    parser.add_argument("-f", "--folder_names", type=str, required=True, nargs="+",
                        help="Folders names to be chosen to work with. Please save this folder in current directory.")

    args = parser.parse_args()
    print(args)

    type = args.type

    output_file = args.output

    df = load_or_create_dataframe(output_file, type)
    data_folder = args.input
    folder_names = args.folder_names
    results = []

    process = "Coloring" if type == 1 else "Max Cut Size"
    print(f"Start: {process}")

    folder_file_count = 0
    counter = 0
    for folder_name in sorted(os.listdir(data_folder)):
        if folder_name not in folder_names:
            continue
        folder_path = os.path.join(data_folder, folder_name)
        file_count = sum(
            os.path.isfile(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
        ) * 4
        folder_file_count += file_count

    for folder_name in sorted(os.listdir(data_folder)):
        if folder_name not in folder_names:
            continue
        folder_path = os.path.join(data_folder, folder_name)

        if os.path.isdir(folder_path):
            for file_name in sorted(os.listdir(folder_path)):
                file_path = os.path.join(folder_path, file_name)
                print(file_path)

                if os.path.isfile(file_path):
                    file_name_full = f"{data_folder}/{folder_name}/{file_name}"

                    graph = read_from_csv_file(file_name_full)
                    print("--------------------------------------------------------")
                    print("--------------------------------------------------------")
                    print("Graph loaded:", graph)
                    print(f"Name of the File: {file_name}")

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

                    for diff in range(-1, 3):
                        counter = counter + 1

                        if diff == -1:
                            key_color_cut = "colors" if type == 1 else "cut_size"
                            key_time = f"time"
                        else:
                            key_color_cut = f"offset_{diff}_colors" if type == 1 else f"offset_{diff}_cut_size"
                            key_time = f"offset_{diff}_time"

                        if not existing_rows.empty and pd.notna(existing_rows.iloc[0].get(key_color_cut)) and pd.notna(
                                existing_rows.iloc[0].get(key_time)):
                            print(f"Skipping {file_name}, diff={diff} (already processed)")
                            result_dict[key_color_cut] = existing_rows.iloc[0][key_color_cut]
                            result_dict[key_time] = existing_rows.iloc[0][key_time]
                            continue

                        opt = 1

                        if type == 1:
                            start_time = time.time()
                            chromatic_number = run_with_timeout(
                                type, graph, diff, opt, timeout=3600, full_file_path=file_path
                            )
                            end_time = time.time()
                            execution_time = (end_time - start_time) / 60
                            if chromatic_number is None:
                                execution_time = None
                            result_dict[key_color_cut] = chromatic_number
                            result_dict[key_time] = execution_time
                        else:
                            start_time = time.time()
                            cut_size = run_with_timeout(
                                type, graph, diff, opt, timeout=3600, full_file_path=file_path
                            )
                            end_time = time.time()
                            execution_time = (end_time - start_time) / 60
                            if cut_size is None:
                                execution_time = None
                            result_dict[key_color_cut] = cut_size
                            result_dict[key_time] = execution_time
                        print(f"{(counter / folder_file_count) * 100:.2f}%")

                    results.append(result_dict)

    if results:
        df = pd.concat([df, pd.DataFrame(results)], ignore_index=True)
        df.to_csv(f"output/{output_file}", index=False)
        print(f"Results saved to output/{output_file}\n\n")


if __name__ == "__main__":
    main()
