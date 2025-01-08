import os
import shutil
import subprocess
import glob
import argparse
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Point Cloud Metric Simulation Runner',
        description='Run a set of view-planning and reconstruction simulations based on a specified dataset',
        epilog='Text at the bottom of help')
    
    parser.add_argument('--dataset', required=True, help="Path to the downloaded dataset.")
    parser.add_argument('--executable-folder', required=True, help="Path to the downloaded executable folder")
    parser.add_argument('--blender', required=True, help="Path to the blender executable.")
    parser.add_argument('--output-folder', required=True, help="Path to the output folder.")
    parser.add_argument('--fast', required=False, action='store_true', help="Only run a subset of simulations.")
    
    args = parser.parse_args()

    # Get the models from the dataset folder
    models = []
    model_folders = glob.glob(args.dataset + "/[0-9][0-9][0-9]_*")
    for folder in model_folders:
        folder_name = os.path.basename(folder)
        object_name = folder_name[4:]
        models.append([object_name, args.dataset + "/" + folder_name + "/model.obj", args.dataset + "/" + folder_name + "/points.ply", "0;0;0;2;2;2"])
    
    # Only keep aphrodite    
    if args.fast:
        models = [models[0], models[1], models[2]]

    # All Metrics v2
    metrics = ["Distance_To_Sparse_Cloud", "Density", "Normalized_Density", "Coverage", "Initial_Coverage", "Relative_Coverage",
               "Angle_Of_Incidence", "Baseline_Height_Ratio", "Camera_Standoff_Distance", "Triangulation_Uncertainty",
               "Saliency2D", "Mean_Curvature", "Plane_Local_Roughness", "Quadratic_Local_Roughness", "Saliency3D",  
               "Unified", "RQF_V15", "Random"]

    # Set how many repetitions per metric and model we want to run
    repetitions = 1

    # Executable paths
    blender_file = args.executable_folder + "/resources/InteractiveRenderingSceneV2.blend"

    resource_folder = args.executable_folder + "/resources"

    # Define the project folder
    project_folder = args.output_folder

    # Create the project folder
    if os.path.exists(project_folder):
        shutil.rmtree(project_folder)
    os.mkdir(project_folder)

    results_folder = project_folder + "/000_Results"
    resultMetricFolder = results_folder + "/Metrics"
    resultTerminationFolder = results_folder + "/Termination"
    resultRuntimeFolder = results_folder + "/Runtime"
    resultMetricRuntimeFolder = results_folder + "/MetricRuntime"
    resultDenseFolder = results_folder + "/DenseClouds"
    os.mkdir(results_folder)
    os.mkdir(resultMetricFolder)
    os.mkdir(resultTerminationFolder)
    os.mkdir(resultMetricRuntimeFolder)
    os.mkdir(resultRuntimeFolder)
    os.mkdir(resultDenseFolder)

    counter = 0
    for model in models:
        for metric in metrics:
            for i in range(repetitions):
                if counter < 7:
                    counter = counter + 1
                    continue
                
                # Create the run name
                run_name = str(counter).zfill(3) + "_" + model[0] + "_" + metric + "_" + str(i)
                
                print("========= Running Configuration:", run_name, "==========")
                
                # Call the simulation executable
                call_args = [args.executable_folder + "/orthosfm-simulation-executable.exe", 
                        "--currentRunID", str(counter), 
                        "--projectFolder", os.path.abspath(project_folder).replace("\\", "\\\\"),
                        "--tripletName", run_name,
                        "--modelName", model[0],
                        "--modelPath", os.path.abspath(model[1]).replace("\\", "\\\\"),
                        "--modelReferencePath", os.path.abspath(model[2]).replace("\\", "\\\\"),
                        "--scanZone", model[3],
                        "--metricName", metric,
                        "--blenderPath", os.path.abspath(args.blender).replace("\\", "\\\\"),
                        "--blenderFilePath", os.path.abspath(blender_file).replace("\\", "\\\\"),
                        "--resourceFolder", os.path.abspath(resource_folder).replace("\\", "\\\\")
                        ]
                
                subprocess.run(call_args)
                
                # Start the subprocess
                # process = subprocess.Popen(call_args)

                # # Wait for the process to complete or timeout after 60 seconds
                # try:
                #     process.wait(timeout=300)
                # except subprocess.TimeoutExpired:
                #     print("Process exceeded timeout, killing it.")
                #     process.terminate()
                    
                # time.sleep(5.0)
                
                # Copy results
                tripletFolder = project_folder + "/" + run_name
                tripletRecoFolder = tripletFolder + "/Reco"
                
                if os.path.exists(tripletRecoFolder + "/global_metrics.txt"):
                    shutil.copy(tripletRecoFolder + "/global_metrics.txt", resultMetricFolder + "/" + run_name + ".txt")
                    
                if os.path.exists(tripletRecoFolder + "/termination.txt"):
                    shutil.copy(tripletRecoFolder + "/termination.txt", resultTerminationFolder + "/" + run_name + ".txt")
                    
                if os.path.exists(tripletRecoFolder + "/time_measurements.txt"):
                    shutil.copy(tripletRecoFolder + "/time_measurements.txt", resultRuntimeFolder + "/" + run_name + ".txt")
                    
                if os.path.exists(tripletRecoFolder + "/metric_runtimes.txt"):
                    shutil.copy(tripletRecoFolder + "/metric_runtimes.txt", resultMetricRuntimeFolder + "/" + run_name + ".txt")
                
                # Clean up the triplet folder
                try:
                    shutil.rmtree(tripletFolder)
                except:
                    print("Failed to delete triplet folder!")
                
                
                # Increase the counter
                counter = counter + 1