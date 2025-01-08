import os
import shutil
import subprocess
import glob
import argparse

from src.time_dependent_behaviour import plot_metrics_over_time_with_averaging
from src.evaluate_correlation import create_correlation_plot
from src.metric_runtime_table import evaluate_average_metric_runtime
from src.completeness_over_time import summarize_simulation_global_metrics
from src.alpha_completeness import plot_joint_alpha_completeness

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Point Cloud Metric Simulation Evaluator',
        description='Creates all figures and tables based on a set of run simulations',
        epilog='Text at the bottom of help')
    
    parser.add_argument('--simulation-folder', required=True, help="Path to the generated simulation folder.")
    
    args = parser.parse_args()
    
    # Check if the folder exists
    if not os.path.exists(args.simulation_folder):
        print("Invalid input folder!")
        
    # Create the figure folder
    figure_folder = args.simulation_folder + "/001_Figures"
    if os.path.exists(figure_folder):
        shutil.rmtree(figure_folder)
    os.mkdir(figure_folder)
    
    # Time dependent behaviour
    plot_metrics_over_time_with_averaging(args.simulation_folder, figure_folder + "/time_dependent_behaviour.png")
    
    # MDS Plot (Metric correlation)
    create_correlation_plot(args.simulation_folder, figure_folder + "/mds_plot.png")
    
    # Metric Runtime Table
    evaluate_average_metric_runtime(args.simulation_folder, figure_folder + "/metric_runtime.csv")
    
    # Completeness for a single model
    summarize_simulation_global_metrics(args.simulation_folder, figure_folder + "/completeness_single_model.png")
    
    # Alpha completeness plot over all models
    plot_joint_alpha_completeness(args.simulation_folder, figure_folder + "/alpha_completeness_plot.png")