import os
from matplotlib import pyplot as plt
import matplotlib
from glob import glob
import numpy as np

def plot_alpha_completeness(result_folder, data_folder, alpha, ignore_list=None, with_legend=True):
    # Get the models in the data folder
    model_names = ["Aphrodite_of_melos", "Bust_of_roza_loewenfeld", "Sculpture_st_anna", "Carved_perfum_bottle",
                   "Coffin_from_el_hiba", "Dinosaur_footprint", "Fragment_plaque", "Funerary_stela",
                   "Antique_figure", "Wooden_apothecary_vessel", "Baba", "Bike", "Candlestick", "Storm_Bird"]
    
    # Get all global metric result files in the folder
    result_files = glob(result_folder + "/[0-9][0-9][0-9]_*.txt")
    
    # Seperate into metrics
    metric_files = {}
    for txt in result_files:
        # Clean up the name
        cleaned_name = os.path.basename(txt)[4:-6]
        matching_model = ""
        for model in model_names:
            if model in cleaned_name:
                matching_model = model
                break
                
        # Remove the model name from the filename
        cleaned_name = cleaned_name.replace(matching_model, "")
        
        # Remove prefix "_"
        cleaned_name = cleaned_name[1:]
        
        if ignore_list is not None:
            ignored = False
            for ignored_name in ignore_list:
                if ignored_name in cleaned_name:
                    ignored = True
                    break
            
            # Skip this metric
            if ignored:
                continue
        
        if cleaned_name not in metric_files:
            metric_files[cleaned_name] = {matching_model : txt}
        else:
            metric_files[cleaned_name][matching_model] = txt
            
    # Loop over all metrics and read in the completeness and corresponding number of images
    metric_values = {}
    for metric_name in metric_files:
        # Init the dictionary
        metric_values[metric_name] = {}
        
        # Loop over all models for this metric
        for model in metric_files[metric_name]:
            # Read in the file
            images = []
            completeness = []
            
            with open(metric_files[metric_name][model], "r") as f:
                for line in f:
                    # Read in completeness
                    if line.startswith("Completeness"):
                        splitted = line.rstrip().split(";")
                        for val in splitted[1:]:
                            completeness.append(float(val))
                        
                    # Read in Images
                    if line.startswith("Images"):
                        splitted = line.rstrip().split(";")
                        for val in splitted[1:]:
                            images.append(int(val))
                            
            # Add to the value dictionary
            metric_values[metric_name][model] = [images, completeness]
            
            
    # Create the image number array for evaluating alpha recall
    images = range(0, 300)
    completeness_percentage = {}
    
    # Now calculate the "alpha recall"
    for metric_name in metric_values:
        percentage_values = []
        
        # Loop over all alpha values (images)
        for img in images:
            model_fullfills_threshold = []
            
            # Loop over all models of the metric
            for model in metric_values[metric_name]:
                # Find the index of the largest evaluated image number that is smaller than the threshold 
                best_index = -1
                for i in range(len(metric_values[metric_name][model][0])):
                    if metric_values[metric_name][model][0][i] <= img:
                        best_index = i
                    elif metric_values[metric_name][model][0][i] > img:
                        break
                        
                if best_index != -1:
                    # Do the threshold check
                    if metric_values[metric_name][model][1][best_index] > alpha:
                        model_fullfills_threshold.append(1)
                    else:
                        model_fullfills_threshold.append(0)
                else:
                    model_fullfills_threshold.append(0)
                    
            # Calculate the percentage of models that fullfill the threshold
            current_percentage = 100 * (np.sum(model_fullfills_threshold) / len(model_fullfills_threshold))
            
            percentage_values.append(current_percentage)
        
        completeness_percentage[metric_name] = percentage_values
    
    
    colors = [
            "#50B695",
            "#5D85C3",
            "#009CDA",
            "#F8BA3C",
            "#EE7A34",
            "#C9308E",
            "#804597"
        ]
    possible_markers = [".", "o", "x", "v"]
    
    line_styles = ["solid", "dotted", "dashed"]
    
    #plt.figure(figsize=(8, 6), dpi=200)
    
    # Plot
    counter = 0
    for metric in completeness_percentage:
        cleaned_name = metric.replace("_", " ")
        if cleaned_name == "Coverage":
            cleaned_name = "Absolute Coverage"
        if cleaned_name == "Distance To Edge":
            cleaned_name = "Distance-To-Edge"
        if cleaned_name == "Baseline Height Ratio":
            cleaned_name = "Baseline-Height-Ratio"
        if cleaned_name == "RQF V15":
            cleaned_name = "RQF (ours)"
        
        plt.plot(images, completeness_percentage[metric], linestyle=line_styles[counter % len(line_styles)], color=colors[counter % len(colors)], label=cleaned_name, alpha=0.9)
        counter = counter + 1
        
    plt.xlabel("Images added to the reconstruction")
    #plt.ylabel(f"Percentage of models with a completeness greater than {alpha}%")
    plt.ylabel(f"Complete Models [%]")
    #plt.title(f"Percentage of models with a completeness greater than {alpha}% after adding N images.")
    plt.title("Threshold $\\alpha=" + str(alpha) + "$%")
    plt.ylim(0, 101)
    
    if with_legend:
        plt.legend(bbox_to_anchor=(1.05, 1.05))

    
def find_outliers_in_data(folder):
    result_files = glob(folder + "/[0-9][0-9][0-9]_*.txt")
    
    for result in result_files:
        with open(result, "r") as f:
            for line in f:
                # Read in completeness
                if line.startswith("Completeness"):
                    splitted = line.rstrip().split(";")
                    final_completeness = float(splitted[-1])
                    
                    if final_completeness < 90:
                        print("Possible outlier: ", os.path.basename(result))
                    
                    

def plot_joint_alpha_completeness(simulation_folder, output_path):
    
    #folder = "D:\\Users\\kneumann\\002_OrthoSfM\\Simulations\\Results_CulturalHeritage_25_03_24\\Metrics"
    #folder = "D:\\Users\\kneumann\\002_OrthoSfM\\Simulations\\Results_CulturalHeritageV2_26_03_24\\Metrics"
    #folder = "D:\\Users\\kneumann\\002_OrthoSfM\\Simulations\\Results_CulturalHeritage_300Imgs\\Metrics"
    folder = simulation_folder + "/000_Results/Metrics"
    
    #find_outliers_in_data(folder)
    #exit()
    
    #plt.figure(figsize=(12, 5), dpi=150)
    plt.figure(figsize=(8, 5), dpi=150)
    
    #alpha_values = [50, 75, 90]
    alpha_values = [75, 90]
    
    for i in range(len(alpha_values)):
        plt.subplot(len(alpha_values),1,i + 1)
        plot_alpha_completeness(folder, "D:\\Users\\kneumann\\002_OrthoSfM\\Simulations\\SimulationsPython\\data\\CulturalHeritage", alpha_values[i], ["V10", "V14"], i == 0)
        
    
    plt.suptitle(f"Percentage of models with a completeness greater than $\\alpha$ after adding N images.")
    
    plt.tight_layout()
    #plt.show() 
    plt.savefig(output_path)