import os
from matplotlib import pyplot as plt
import matplotlib
from glob import glob
import numpy as np
from plyfile import PlyData, PlyElement, PlyProperty
from tqdm import tqdm
from scipy.stats import spearmanr
from sklearn.manifold import MDS
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from adjustText import adjust_text
import random

def get_metric_names(dense_cloud_path, ignore=None):
    # Init the output list
    metric_names = []

    # Load the dense cloud
    pcl = PlyData.read(os.path.abspath(dense_cloud_path))

    # Loop over all properties of the vertex element
    for elem in pcl.elements:
        elem : PlyElement
        # Skip if the element is not
        if elem.name != "vertex":
            continue

        for prop in elem.properties:
            prop : PlyProperty

            # Skip xyz, rgb and normal
            if prop.name in ["x", "y", "z", "red", "green", "blue", "nx", "ny", "nz", "confidence", "view_id"]:
                continue

            if ignore is not None and prop.name in ignore:
                continue

            metric_names.append(prop.name)

    return metric_names

# Load the metrics from a set of dense clouds into a large vector of values
def load_metric_values(result_folder, maximum_number_of_files=-1):
    dense_clouds = glob(result_folder + "/000_Results/DenseClouds/*/*.ply")

    # Limit the number of files (for testing)
    if maximum_number_of_files != -1:
        random.shuffle(dense_clouds)
        dense_clouds = dense_clouds[:maximum_number_of_files]

    # Get the metric names
    metric_names = get_metric_names(dense_clouds[0], ignore=["view_id", "Depth_Map_Uncertainty", "Brightness_Index", "Distance_To_Vertices", "TSDF_Value", "Viewplanability", "Output", "confidence"])
    #metric_names = get_metric_names(dense_clouds[0])
    #metric_names = metric_names[:5]

    # Store all values in a dict (with the metric name as key)
    metric_dict = {}
    for dense in dense_clouds:
        # Try loading the point clouds
        pcl = PlyData.read(os.path.abspath(dense))

        # Extract the metrics
        for metric in metric_names:
            metric_values = pcl.elements[0].data[metric]

            if metric not in metric_dict:
                metric_dict[metric] = np.array(metric_values)
            else:
                metric_dict[metric] = np.hstack([metric_dict[metric], metric_values])

    print("Loaded", metric_dict[metric_names[0]].shape[0], "points for", len(metric_names), "different metrics")
    return metric_dict

def calculate_correlation_matrix(metric_dict):
    print("Calculating correlation matrix..")

    # Extract the metric names into an array
    metric_names = []
    for name in metric_dict:
        metric_names.append(name)

    # Put all metrics into a large matrix of the size (#points, #variables)
    data_matrix = np.zeros((metric_dict[metric_names[0]].shape[0], len(metric_names)))
    for i in range(len(metric_names)):
        data_matrix[:, i] = metric_dict[metric_names[i]]

    # Calculate spearman correlation
    correlation, p_value = spearmanr(data_matrix)

    # Return the correlation
    return correlation


def visualize_using_mds(metric_dict, correlation, output_path):
    print("Visualizing metrics using multi dimensional scaling (MDS)..")

    # Extract the metric names into an array
    metric_names = []
    for name in metric_dict:
        metric_names.append(name.replace("_"," ").replace("Brightness Index", "Gray Index"))

    # Convert to dissimilarity matrix
    dissimilarity_mat = 1.0 - np.abs(correlation)

    # Create an MDS object
    mds = MDS(n_components=2, metric=True, dissimilarity="precomputed", max_iter=10000, n_init=1000, random_state=1)
    embeddings = mds.fit_transform(dissimilarity_mat)

    # Create a new figure
    #fig = plt.figure(figsize=(8,6), dpi=200)
    # Create a new figure
    fig, ax = plt.subplots(figsize=(8,6), dpi=200)
    
    # Define colors
    # colors = ["tab:blue"] * embeddings.shape[0]
    # sizes = [10] * embeddings.shape[0]
    # for i in range(len(metric_names)):
    #     if metric_names[i] in ["Combined Metrics", "Distance To Edge", "Normalized Density", "Coverage", "Saliency2D"]:
    #         colors[i] = "tab:blue"
    #         sizes[i] = 20

    # Plot in scatter plot
    plt.scatter(embeddings[:,0], embeddings[:,1])
    plt.suptitle("Metric Similarity Visualization through Multi Dimensional Scaling (MDS)")
    plt.axis('off')

    # Draw lines that represent the correlation between two metrics
    for i in range(len(metric_names)):
        for j in range(i + 1, len(metric_names)):
            c = abs(correlation[i,j])
            plt.plot([embeddings[i][0], embeddings[j][0]], [embeddings[i][1], embeddings[j][1]], "-", c="tab:blue", alpha=c*c)

    # Add labels
    texts = []
    for i in range(len(embeddings)):
        # Check if this one of our main metrics
        fontweight = "normal"
        color = "black"
        size = 10
        if metric_names[i] in ["Combined Metrics", "Distance To Edge", "Normalized Density", "Coverage", "Saliency2D"]:
            fontweight = "bold"
            color = "tab:blue"
            if metric_names[i] == "Combined Metrics":
                size = 16
        
        texts.append(plt.text(embeddings[i,0], embeddings[i,1], metric_names[i].replace("Combined Metrics","RQF (ours)").replace("Normalized Density","Relative Density"), ha='center', va='center', fontweight=fontweight, c=color, size=size))

    # Create a blue color map
    N = 256
    vals = np.ones((N, 4))
    vals[:, 0] = np.flip(np.linspace(0.12156862745098039, 1, N))
    vals[:, 1] = np.flip(np.linspace(0.4666666666666667, 1, N))
    vals[:, 2] = np.flip(np.linspace(0.7058823529411765, 1, N))
    newcmp = ListedColormap(vals)

    # Add a color bar
    sm = plt.cm.ScalarMappable(cmap=newcmp, norm=plt.Normalize(vmin=0, vmax=1))
    cb = plt.colorbar(sm, label="Absolute Spearman's rank correlation coefficient", orientation="vertical", shrink=0.8, pad=0.05, anchor=(0.5, 0.5), ax=ax)
    cb.set_label("Absolute Spearman's rank correlation coefficient", labelpad=10)
    
     
    # Adjust the text placing
    adjust_text(texts, embeddings[:,0], embeddings[:,1])


    fig.tight_layout(pad=1.0)
    #plt.show()
    plt.savefig(output_path)



def create_correlation_plot(folder, output_path):
    # Use multi dimensional scaling to visualize the metrics similarity
    metric_dict = load_metric_values(folder, 50)
    correlation = calculate_correlation_matrix(metric_dict)
    visualize_using_mds(metric_dict, correlation, output_path)
