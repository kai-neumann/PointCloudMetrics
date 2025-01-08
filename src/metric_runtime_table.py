import numpy as np
import os
import glob

def evaluate_average_metric_runtime(simulation_directory, output_path):
    # Check if the metric runtime sudirectory exists
    runtime_dir = simulation_directory + "\\000_Results\\MetricRuntime"
    if not os.path.exists(simulation_directory):
        print("Error: Invalid directory for evaluating metric runtime")
        
    # Get all files
    runtime_files = glob.glob(runtime_dir + "/*.txt")
    
    # Assemble the metric runtimes in a dict
    metrics = {}
    for runtime_file in runtime_files:
        # Read in the runtimes line by line
        with open(runtime_file, "r") as f:
            for line in f:
                splitted = line.rstrip().split(";")
                
                # Get the metric name
                metric_name = splitted[0].replace(" [s]", "").replace("_", " ").replace("Brightness Index", "Gray Index").replace("Combined Metrics", "RQF (ours)").replace("Normalized Density", "Relative Density")
                
                # Check if this is the total or images entry
                if metric_name == "TOTAL" or metric_name == "Images" or metric_name == "Output":
                    continue
                
                # Also ignore some of the less important metrics
                if metric_name in ["Depth Map Uncertainty", "Brightness Index", "Distance To Vertices", "TSDF Value", "Viewplanability", "Gray Index"]:
                    continue
                
                # Init the dict entry if necessary
                if metric_name not in metrics:
                    metrics[metric_name] = []
                
                # Collect the runtimes
                for value in splitted[1:]:
                    metrics[metric_name].append(float(value))
                    
                    
    # Calculate RQF based on its four component metrics ("Coverage", "Saliency2D", "Distance To Edge", "Relative Density")
    measurements_count = len(metrics["Coverage"])
    metrics["RQF (ours)"] = []
    for i in range(measurements_count):
        metrics["RQF (ours)"].append(metrics["Coverage"][i] + metrics["Saliency2D"][i] + metrics["Distance To Edge"][i] + metrics["Relative Density"][i])
        metrics["Unified"][i] += metrics["Density"][i] + metrics["Triangulation Uncertainty"][i] + metrics["Saliency2D"][i] + metrics["Saliency3D"][i]
        
    print("Data points: ", len(metrics["Coverage"]))
    
                    
    # Calculate the mean and standard deviation per metric
    names = []
    means = []
    stds = []
    for metric in metrics:
        mean = np.mean(metrics[metric])
        std = np.std(metrics[metric])
        
        names.append(metric)
        means.append(mean)
        stds.append(std)
        
    # Assemble the three lines for writing out
    line_name = ""
    line_mean = ""
    line_std = ""
    for i in range(len(names)):
        line_name += names[i] + ";"
        line_mean += str(means[i]) + ";"
        line_std += str(stds[i]) + ";"
        
    # Save out into a table
    with open(output_path, "w") as f:
        f.write(line_name[:-1] + "\n")    
        f.write(line_mean[:-1] + "\n")  
        f.write(line_std[:-1] + "\n")  