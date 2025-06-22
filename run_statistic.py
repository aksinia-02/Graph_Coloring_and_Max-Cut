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
            "colors", "offset_0_colors", "offset_1_colors", "offset_2_colors",
            "offset_3_colors", "offset_4_colors", "offset_5_colors"
        ]
        suffix = "coloring"
    else:
        columns = [
            "nodes", "edges", "density", "name",
            "cut_size", "offset_0_cut_size", "offset_1_cut_size", "offset_2_cut_size",
            "offset_3_cut_size", "offset_4_cut_size", "offset_5_cut_size"
        ]
        suffix = "max_cut"
    os.makedirs("output", exist_ok=True)
    filename = f"output/{suffix}_{filename}"

    if os.path.exists(filename):
        df = pd.read_csv(filename)
        print(f"Loaded existing file: {filename}")
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)
        print(f"File not found. Created new file: {filename}")

    return df

def target_func(result, type, graph, n, opt, folder_path, min_num_colors, max_num_colors):
    if type == 1:
        coloring, chromatic_number = run_solving_graph_coloring(graph, n, opt, folder_path, False, min_num_colors, max_num_colors)
        result[0] = (coloring, chromatic_number)
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


def main():
    parser = argparse.ArgumentParser(description="Generate some random graphs.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output file for results.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input folder with data.")
    parser.add_argument("-t", "--type", type=int, choices=[0, 1], required=True,
                        help="Set to 1 if graph coloring are required, otherwise 0 for max cut.")
    parser.add_argument("-f", "--folder_names", type=str, required=True, nargs="+",
                        help="Folders names to be chosen to work with. Please save this folder in current directory.")
    parser.add_argument("-s", "--save_statistic", type=int, choices=[0, 1], required=False,
                       help="Set 1 to save unsaved statistic.")

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
                    edges = graph.number_of_edges()
                    density = cal_density(graph)

                    result_dict = {
                        "nodes": nodes,
                        "edges": edges,
                        "density": density,
                        "name": file_name
                    }

                    existing_rows = df[df["name"] == file_name]

                    min_num_colors = 1
                    max_num_colors = nodes
                    prev_diff = 100
                    prev_coloring = None
                    prev_max_cut = 0
                    prev_best_partition = None

                    for diff in [-1, 0, 5, 4, 3, 2, 1]:
                        counter = counter + 1

                        if diff == -1:
                            key_color_cut = "colors" if type == 1 else "cut_size"
                        else:
                            key_color_cut = f"offset_{diff}_colors" if type == 1 else f"offset_{diff}_cut_size"

                        # if not existing_rows.empty and pd.notna(existing_rows.iloc[0].get(key_color_cut)):
                        #     print(f"Skipping {file_name}, diff={diff} (already processed)")
                        #     result_dict[key_color_cut] = existing_rows.iloc[0][key_color_cut]
                        #     continue

                        opt = 1
                        if args.save_statistic is None or args.save_statistic == 0:

                            if type == 1:

                                if diff == -1:
                                    result = run_with_timeout(
                                        type, graph, diff, opt, timeout=1800, full_file_path=file_path,
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
                                            type, graph, diff, opt, timeout=1800, full_file_path=file_path,
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


                            else:
                                if diff == -1:
                                    result = run_with_timeout(
                                        type, graph, diff, opt, timeout=1800, full_file_path=file_path, min_num_colors=None
                                    )
                                    if result is not None:
                                        prev_max_cut = result[0]
                                        prev_best_partition = result[1]
                                        if prev_best_partition is not None:
                                            nodes_counts = Counter(prev_best_partition.values())
                                            prev_diff = max(nodes_counts.values()) - min(nodes_counts.values())
                                else:
                                    if prev_diff > diff:
                                        result = run_with_timeout(
                                            type, graph, diff, opt, timeout=1800, full_file_path=file_path, min_num_colors=None
                                        )
                                        if result is not None:
                                            prev_max_cut = result[0]
                                            prev_best_partition = result[1]
                                            if prev_best_partition is not None:
                                                nodes_counts = Counter(prev_best_partition.values())
                                                prev_diff = max(nodes_counts.values()) - min(nodes_counts.values())
                                    else:
                                        base_name = os.path.basename(file_path)
                                        json_name = base_name.replace(".csv", "")
                                        suffix = "_h" if opt == 0 else "_o"
                                        if diff == -1:
                                            json_name = f"{json_name}{suffix}_n_None_max_cut.json"
                                        else:
                                            json_name = f"{json_name}{suffix}_n_{diff}_max_cut.json"
                                        output_path = os.path.join(os.path.dirname(file_path), json_name)
                                        if not os.path.exists(output_path):
                                            with open(output_path, "w") as f:
                                                json.dump({
                                                    "partition": prev_best_partition,
                                                    "max_cut_size": prev_max_cut
                                                }, f, indent=4)
                                            print("------------------------------------")
                                            print(f"Partition is saved to {output_path}")
                                        else:
                                            print("------------------------------------")
                                            print(f"Partition file is already exist {output_path}")
                            print(f"{(counter / folder_file_count) * 100:.2f}%")

                        base_name = os.path.basename(file_path)
                        json_name = base_name.replace(".csv", "")
                        suffix = "_h" if opt == 0 else "_o"
                        suffix_type = "_coloring" if type == 1 else "_max_cut"

                        if diff != -1:
                            json_name = f"{json_name}{suffix}_n_{diff}{suffix_type}.json"
                        else:
                            json_name = f"{json_name}{suffix}_n_None{suffix_type}.json"
                        output_path = os.path.join(os.path.dirname(file_path), json_name)

                        print(json_name)

                        if os.path.exists(output_path):
                            if type == 1:
                                print(f"Found existing coloring file: {output_path}. Loading coloring...")
                                with open(output_path, "r") as f:
                                    coloring = json.load(f)

                                result_dict[key_color_cut] = max(coloring.values()) if coloring else None
                            else:
                                print(f"Found existing partition file: {output_path}. Loading...")
                                with open(output_path, "r") as f:
                                    data = json.load(f)
                                    result_dict[key_color_cut] = data.get("max_cut_size")

                    results.append(result_dict)
                    print(result_dict)

    if results:
        df = pd.concat([df, pd.DataFrame(results)], ignore_index=True)
        if type == 1:
            suffix = "coloring"
        else:
            suffix = "max_cut"
        df.to_csv(f"output/{suffix}_{output_file}", index=False)
        print(f"Results saved to output/{output_file}\n\n")


if __name__ == "__main__":
    main()
