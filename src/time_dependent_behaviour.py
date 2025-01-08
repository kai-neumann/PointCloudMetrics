import os
from glob import glob
from plyfile import PlyData, PlyElement, PlyProperty
import numpy as np
from matplotlib import pyplot as plt

def plot_metrics_over_time_with_averaging(project_folder, output_path):
    # First get all sub folders
    sub_folders = glob(project_folder + "/000_Results/DenseClouds/*")
    
    # Ignore list
    ignore_list = ["view_id", "Depth_Map_Uncertainty", "Brightness_Index", "Distance_To_Vertices", "TSDF_Value", "Viewplanability", "Output", "confidence", "Combined_Metrics"]
    
    # Accumulate the values in a recursive dictionary. The first key is always the metric name, the second one is the number of images, which includes the actual data points
    metric_values = {}
    
    # Loop over all of them
    for sub in sub_folders:
        # Get all plys in the folder
        dense_clouds = glob(sub + "/*.ply")
        
        # Loop over all dense clouds
        for cloud in dense_clouds:
            # Extract the image number
            image_number = int(str(os.path.basename(cloud)).replace("dense_cloud_","").replace(".ply",""))

            # Load the dense cloud
            pcl = PlyData.read(os.path.abspath(cloud))

            # Loop over all properties of the vertex element
            for elem in pcl.elements:
                elem : PlyElement
                # Skip if the element is not
                if elem.name != "vertex":
                    continue

                for prop in elem.properties:
                    prop : PlyProperty

                    # Skip xyz, rgb and normal
                    if prop.name in ["x", "y", "z", "red", "green", "blue", "nx", "ny", "nz"]:
                        continue
                    
                    if prop.name in ignore_list:
                        continue

                    # Get the data
                    values = np.array(elem.data[prop.name])

                    # Calculate the minkowski pooling for the values
                    power = 3
                    minkowski = np.power(np.sum(np.power(values, power)) / len(values), 1/power)
                    #minkowski = np.mean(values)
                    #std = np.std(values)

                    # Check for validity
                    if minkowski > 1 or minkowski < 0:
                        continue
                    
                    # Initialize the sub dict if necessary
                    if prop.name not in metric_values:
                        metric_values[prop.name] = {}
                        
                    # Initialize the sub sub dict if necessary
                    if str(image_number) not in metric_values[prop.name]:
                        # Add to dict
                        metric_values[prop.name][str(image_number)] = []
                        
                    # Add to list of values
                    metric_values[prop.name][str(image_number)].append(minkowski)
                    
                    
    # Loop over all termination files to get the pooled RQF metric from there
    termination_files = glob(project_folder + "/000_Results/Termination/*.txt")
    for termi in termination_files:
        with open(termi, "r") as f:
            # Collect the images and values
            images = []
            values = []
            
            for line in f:
                # Get images
                if line.startswith("Images"):
                    images = line.rstrip().split(";")[1:]
                
                # Get the pooled value
                if line.startswith("Pooled Value"):
                    values = line.rstrip().split(";")[1:]
                    
            if "RQF (ours)" not in metric_values:
                metric_values["RQF (ours)"] = {}
                
            for img, val in zip(images, values):
                if img not in metric_values["RQF (ours)"]:
                    metric_values["RQF (ours)"][img] = []
                
                metric_values["RQF (ours)"][img].append(float(val))
                
                    
        
    # Figure out how many sub plots we need
    cols = 6
    rows = len(metric_values.values()) // cols
    if rows * cols < len(metric_values.values()):
        rows += 1

    # Create an new figure
    fig = plt.figure(figsize=(4.5*3.2,4.5*1.7),dpi=150)

    # Plot all metrics
    counter = 0
    for name in metric_values:
        # Increase the counter
        counter += 1
        
        # Create lists for images and values
        images = []
        values = []
        std = []
        for img_str in metric_values[name]:
            if len(img_str) != 0:
                images.append(int(img_str))
                values.append(np.mean(metric_values[name][img_str]))
                std.append(np.std(metric_values[name][img_str]))
        

        # Define which subplots
        plt.subplot(rows, cols, counter)
        plt.grid(alpha=0.5)
        plt.plot(images, values, "-o", lw=2)
        plt.fill_between(images,np.array(values)-std, np.array(values)+std, alpha=0.2)
        plt.ylim([0, 1])
        plt.xlabel("Images")
        plt.ylabel("Global Response")
        plt.title(name.replace("_", " ").replace("Brightness Index", "Gray Index").replace("Combined Metrics", "RQF (ours)").replace("Normalized Density", "Relative Density"))

    plt.suptitle("Global Metric Response after Minkowski Pooling", fontsize=24)
    fig.tight_layout(pad=1.0)
    #plt.show()
    
    plt.savefig(output_path)