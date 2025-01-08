import os
from matplotlib import pyplot as plt
import matplotlib
from glob import glob
import numpy as np


def summarize_simulation_global_metrics(result_folder, output_path):
    
    # Get all global metric result files in the folder
    result_files = glob(result_folder + "/000_Results/Metrics/[0-9][0-9][0-9]_*.txt")
    #termination_files = glob(result_folder + "/../Termination/[0-9][0-9][0-9]_*.txt")

    # Define a list of valid models we want to evaluate in this run
    #valid_models = ["Suzanne"]
    #valid_models = ["Sphere"]
    #valid_models = ["Dragon"]
    valid_models = ["Aphrodite_of_melos", "Aphrodite"]
    #valid_models = ["Carved_perfum_bottle"]
    #valid_models = ["Sculpture_st_anna"]
    #valid_models = ["Funerary_stela"]
    #valid_models = ["Antique_figure"]


    #ignored_metrics = ["Relative Coverage"]
    ignored_metrics = []

    # Filter by valid models
    filtered_files = []
    for file in result_files:
        for model in valid_models:
            if model in os.path.basename(file):
                filtered_files.append(file)
                break

    # Loop over all files and get the available local metrics
    files_per_metric = {}
    for file in filtered_files:
        name = os.path.basename(file)
        
        # Remove model names
        for model_name in valid_models:
            name = name.replace(model_name, "")
        
        splitted = name[4:-4].split("_")
        
        metricNameComponents = splitted[1:-1]

        metricName = metricNameComponents[0]
        for component in metricNameComponents[1:]:
            metricName += " " + component

        if metricName not in files_per_metric:
            files_per_metric[metricName] = [file]
        else:
            files_per_metric[metricName].append(file)

    # Now average all global metrics per metric
    global_metric_values = {}
    for metric in files_per_metric:
        print("Parsing '" + metric + "'")

        if metric in ignored_metrics:
            continue

        # Read in all lines of the global metric file into a dict
        metric_values = {}

        # For each file of this metric
        for file in files_per_metric[metric]:
            with open(file, "r") as file:
                for line in file:
                    splitted = line.split(";")

                    # Extract the name
                    metric_name = splitted[0]

                    # Extract the values
                    values = []
                    for val in splitted[1:]:
                        values.append(float(val))

                    if metric_name not in metric_values:
                        metric_values[metric_name] = [values]
                    else:
                        metric_values[metric_name].append(values)
                        
        print("   - Read in Metric values")

        for name in metric_values:
            max_len = 0
            for filearray in metric_values[name]:
                if len(filearray) > max_len:
                    max_len = len(filearray)
                    
            # Initialize the mean and std arrays
            mean_array = np.zeros((max_len,))
            std_array = np.zeros((max_len,))
            
            # Loop over all value entries
            for i in range(max_len):
                values = []
                
                # Collect all values for that entry
                for filearray in metric_values[name]:
                    if i <= len(filearray) - 1:
                        values.append(filearray[i])
                
                # Calculate the mean and standard deviation
                mean_array[i] = np.mean(np.array(values))
                std_array[i] = np.std(np.array(values))
            
            metric_values[name] = [mean_array, std_array]

        # Add to list of global values
        for name in metric_values:
            if name not in global_metric_values:
                global_metric_values[name] = {metric: metric_values[name]}
            else:
                print("Adding '" + name + "' (" + metric + ")")
                global_metric_values[name][metric] = metric_values[name]
    
    our_metrics = ["RQF", "RQF V15", "Distance To Edge", "Normalized Density", "Coverage", "Initial Coverage", "Relative Coverage",  "Relative Density"]
    
    # Get an order for plotting (based on the end value)
    name_value_pairs = []
    for local_metric in global_metric_values["Completeness [%]"]:
        percentage = global_metric_values["Completeness [%]"][local_metric][0][-1]
        
        if local_metric in our_metrics:
            percentage += 100
        
        if local_metric == "RQF V15":
            percentage = 1000
        
        name_value_pairs.append([local_metric, percentage])
        
    
        
    sorted_pairs = sorted(name_value_pairs, key=lambda x: x[1], reverse=True)
    
    #print(global_metric_values["Completeness [%]"])
    
    plt.figure(figsize=(9, 5), dpi=150)
    
    colors = [
        "#50B695",
        "#5D85C3",
        #"#009CDA",
        "#F8BA3C",
        "#EE7A34",
        "#C9308E",
        "#804597",
        "#E9503E"
    ]
    possible_markers = [".", "o", "x", "v", "s", "*"]
    
    line_styles = ["solid", "dotted", "dashed"]
    
    name = "Completeness [%]"
    
    metric_counter = 0
    for metric_pair in sorted_pairs:
        local_metric = metric_pair[0]
        
        # Get the images array for the metric with the most entries
        images = global_metric_values["Images"][local_metric][0]
        for i in range(len(global_metric_values["Images"][local_metric])):
            if len(global_metric_values["Images"][local_metric][i]) > len(images):
                images = global_metric_values["Images"][local_metric][i]
                
                
        print("Plotting", local_metric)
        
        color = colors[metric_counter % len(colors)]
        if local_metric in our_metrics:
            color = "#009CDA"
        
        alpha = 0.5
        label = local_metric
        label = label.replace(" V15","")
        label = label.replace("Normalized Density","Relative Density")
        if label in our_metrics:
            label += " (ours)"
            alpha = 1.0
            
        
            
        
        
        
        # Plot the mean
        plt.plot(images[:len(global_metric_values[name][local_metric][0])], global_metric_values[name][local_metric][0], linestyle=line_styles[metric_counter % len(line_styles)], lw=1, label=label, marker=possible_markers[metric_counter % len(possible_markers)], c=color, alpha=alpha)

        # Plot the std
        """plt.fill_between(images,
                        global_metric_values[name][local_metric][0] - global_metric_values[name][local_metric][1],
                        global_metric_values[name][local_metric][0] + global_metric_values[name][local_metric][1],
                        alpha=0.1, color=colors[metric_counter % len(colors)])"""
                        #color=colors[local_metric])
                        
        metric_counter += 1

    plt.legend(bbox_to_anchor=(1.025, 0.97), loc='upper left')
    plt.xlabel("Total number of images")
    plt.ylabel("Reconstruction completeness [%]")
    #plt.rcParams["figure.subplot.right"] = 0.5
    plt.subplots_adjust(right=0.675, left=0.08, top=0.95, bottom=0.1)
    plt.title("Reconstruction Completeness over Time")
    
    #plt.show()
    plt.savefig(output_path)
