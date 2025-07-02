import os
from graph_coloring.graph_coloring_solver import *
from max_cut.max_cut_solver import *
from max_cut.exact_max_cut import exact_max_cut_multi_n
import pandas as pd
import time
import multiprocessing
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools import read_from_csv_file

# .\venv\Scripts\Activate

def target_func(result, type, graph, n, opt, folder_path, min_num_colors, max_num_colors):
    if type == 1:
        coloring, chromatic_number = run_solving_graph_coloring(graph, n, opt, folder_path, False, min_num_colors, max_num_colors)
        result[0] = (coloring, chromatic_number)
    else:
        if opt == 1:
            result[0] = exact_max_cut_multi_n(graph)
        else:
            max_cut_size, best_partition = run_solving_max_cut(graph, n, opt, folder_path)
            result[0] = (max_cut_size, best_partition)


def run_with_timeout(type, graph, n, opt, timeout=120, full_file_path=None, min_num_colors=None, max_num_colors=None):
    manager = multiprocessing.Manager()
    result = manager.list([None])

    process = multiprocessing.Process(target=target_func, args=(result, type, graph, n, opt, full_file_path, min_num_colors, max_num_colors))
    process.start()
    process.join(timeout)

    if process.is_alive():
        print("Timeout! Stopping execution.")
        process.terminate()
        process.join()
        return None

    return result[0]

def save_results_to_files(results, file_path, opt, type):
    base_name = os.path.basename(file_path)
    folder = os.path.dirname(file_path)
    json_name_base = base_name.replace(".csv", "")
    suffix = "_h" if opt == 0 else "_o"

    for diff in sorted(results.keys(), key=lambda x: (x == -1, x)):  # Save -1 (None) last
        result_data = results[diff]
        partition = result_data["partition"]
        cut_size = result_data["cut_size"]

        if diff == -1:
            file_suffix = f"{suffix}_n_None_max_cut.json"
        else:
            file_suffix = f"{suffix}_n_{diff}_max_cut.json"

        json_name = f"{json_name_base}{file_suffix}"
        output_path = os.path.join(folder, json_name)

        if not os.path.exists(output_path):
            with open(output_path, "w") as f:
                json.dump({
                    "partition": partition,
                    "max_cut_size": cut_size
                }, f, indent=4)
            print("------------------------------------")
            print(f"Partition is saved to {output_path}")
        else:
            print("------------------------------------")
            print(f"Partition file already exists: {output_path}")

        if partition is None:
            print("------------------------------------")
            print(f"Partition with difference {diff} is impossible")

        print("------------------------------------")
        print(f"MAX CUT is {cut_size}")

        if partition is not None:
            nodes_counts = Counter(partition.values())
            print("------------------------------------")
            print(f"First set: {max(nodes_counts.values())}, second set: {min(nodes_counts.values())}")
            print(f"Difference is {max(nodes_counts.values()) - min(nodes_counts.values())}")


def main():
    parser = argparse.ArgumentParser(description="Starts solvers for a specific folder with graphs.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input folder with data.")
    parser.add_argument("-t", "--type", type=int, choices=[0, 1], required=True,
                        help="Set to 1 if graph coloring are required, otherwise 0 for max cut.")
    parser.add_argument("-f", "--folder_names", type=str, required=True, nargs="+",
                        help="Folders names to be chosen to work with. Please save this folder in current directory.")

    args = parser.parse_args()
    print(args)

    type = args.type
    data_folder = args.input
    folder_names = args.folder_names
    opt = 1

    process = "Coloring" if type == 1 else "Max Cut Size"
    print(f"Start: {process}")

    folder_file_count = 0
    counter = 0
    for folder_name in sorted(os.listdir(data_folder)):
        if folder_name not in folder_names:
            continue
        folder_path = os.path.join(data_folder, folder_name)
        file_count = sum(
            f.endswith('.csv') and os.path.isfile(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
        ) * 7
        folder_file_count += file_count

    for folder_name in sorted(os.listdir(data_folder)):
        if folder_name not in folder_names:
            continue
        folder_path = os.path.join(data_folder, folder_name)

        if os.path.isdir(folder_path):
            for file_name in sorted(f for f in os.listdir(folder_path) if f.endswith('.csv')):
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

                    if type == 0:
                        suffix = "_h" if opt == 0 else "_o"
                        file_suffix = f"{suffix}_n_None_max_cut.json"
                        base_name = os.path.basename(file_path)
                        json_name_base = base_name.replace(".csv", "")
                        json_name = f"{json_name_base}{file_suffix}"
                        output_path = os.path.join(os.path.dirname(file_path), json_name)
                        if os.path.exists(output_path):
                            print("------------------------------------")
                            print(f"Partition file already exists: {output_path}")
                        else:
                            result = run_with_timeout(
                                type, graph, None, opt, timeout=3600, full_file_path=file_path
                            )
                            #print(result)
                            save_results_to_files(result, file_path, opt, type)
                        counter = counter + 7
                        print(f"Statistic: {(counter / folder_file_count) * 100:.2f}%")
                        continue

                    min_num_colors = 1
                    max_num_colors = nodes
                    prev_diff = 100
                    prev_coloring = None

                    for diff in [-1, 0, 5, 4, 3, 2, 1]:
                        counter = counter + 1

                        if diff == -1:
                            result = run_with_timeout(
                                type, graph, diff, opt, timeout=3600, full_file_path=file_path,
                                min_num_colors=min_num_colors, max_num_colors=max_num_colors
                            )
                            if result is not None:
                                prev_coloring = result[1]
                                min_num_colors = result[0]
                                color_counts = Counter(result[1].values())
                                prev_diff = max(color_counts.values()) - min(color_counts.values())
                            # else:
                            #     break
                        else:
                            if prev_diff > diff or diff == 5:
                                result = run_with_timeout(
                                    type, graph, diff, opt, timeout=3600, full_file_path=file_path,
                                    min_num_colors=min_num_colors, max_num_colors=max_num_colors
                                )
                                if result is not None:
                                    if diff == 0:
                                        max_num_colors = result[0]
                                    else:
                                        min_num_colors = result[0]
                                        prev_coloring = result[1]
                                        color_counts = Counter(prev_coloring.values())
                                        prev_diff = max(color_counts.values()) - min(color_counts.values())
                                else:
                                    break
                            else:
                                base_name = os.path.basename(file_path)
                                json_name = base_name.replace(".csv", "")
                                suffix = "_h" if opt == 0 else "_o"
                                if diff != -1:
                                    json_name = f"{json_name}{suffix}_n_{diff}_coloring.json"
                                else:
                                    json_name = f"{json_name}{suffix}_n_None_coloring.json"
                                output_path = os.path.join(os.path.dirname(file_path), json_name)
                                if not os.path.exists(output_path):
                                    with open(output_path, "w") as f:
                                        json.dump(prev_coloring, f, indent=4)
                                        print("------------------------------------")
                                        print(f"Coloring is saved to {output_path}")
                                else:
                                    print("------------------------------------")
                                    print(f"Coloring file is already exist {output_path}")

                        print(f"Statistic: {(counter / folder_file_count) * 100:.2f}%")


if __name__ == "__main__":
    main()
