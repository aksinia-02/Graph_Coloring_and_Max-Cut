import os
import json
import pandas as pd
import argparse
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from tools import read_from_csv_file

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
    path = f"output/{suffix}_{filename}"
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"Loaded existing file: {path}")
    else:
        df = pd.DataFrame(columns=columns)
        df.to_csv(path, index=False)
        print(f"Created new file: {path}")
    return df



def save_results_to_csv(results, filename, type):
    suffix = "coloring" if type == 1 else "max_cut"
    path = f"output/{suffix}_{filename}"
    if results:
        df = pd.DataFrame(results)
        if os.path.exists(path):
            existing = pd.read_csv(path)
            df = pd.concat([existing, df], ignore_index=True)
        df.to_csv(path, index=False)
        print(f"Results saved to {path}")

def main():
    parser = argparse.ArgumentParser(description="Saves statistic.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Output file for results.")
    parser.add_argument("-i", "--input", type=str, required=True,
                        help="Input folder with data.")
    parser.add_argument("-t", "--type", type=int, choices=[0, 1], required=True,
                        help="Set to 1 if graph coloring are required, otherwise 0 for max cut.")
    parser.add_argument("-f", "--folder_names", type=str, required=True, nargs="+",
                        help="Folders names to be chosen to work with. Please save this folder in current directory.")

    args = parser.parse_args()
    print(args)

    opt = 1
    type = args.type
    output_file = args.output

    df = load_or_create_dataframe(output_file, type)

    data_folder = args.input
    folder_names = args.folder_names
    results = []

    process = "Coloring" if type == 1 else "Max Cut Size"
    print(f"Saving: {process}")

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

                    for diff in [-1, 0, 5, 4, 3, 2, 1]:

                        if diff == -1:
                            key_color_cut = "colors" if type == 1 else "cut_size"
                        else:
                            key_color_cut = f"offset_{diff}_colors" if type == 1 else f"offset_{diff}_cut_size"

                        if not existing_rows.empty and pd.notna(existing_rows.iloc[0].get(key_color_cut)):
                            print(f"Skipping {file_name}, diff={diff} (already processed)")
                            result_dict[key_color_cut] = existing_rows.iloc[0][key_color_cut]
                            continue

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

    save_results_to_csv(results, output_file, type)

if __name__ == "__main__":
    main()