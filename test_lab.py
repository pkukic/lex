import os
import subprocess
import shutil

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INTEGRATION_TESTS_DIR = os.path.join(SCRIPT_DIR, "integration_tests")
ANALIZATOR_DIR = os.path.join(SCRIPT_DIR, "analizator")

# Iterate over the files in the integration_tests directory
for file in os.listdir(INTEGRATION_TESTS_DIR):
    file_path = os.path.join(INTEGRATION_TESTS_DIR, file)
    
    # Check if the file is a .lan file
    if file.endswith(".lan"):
        print(file_path)
        
        # Remove the 'tablice' directory if it exists
        tablice_dir = os.path.join(ANALIZATOR_DIR, "tablice")
        if os.path.exists(tablice_dir):
            shutil.rmtree(tablice_dir)
        
        # Execute GLA.py with the .lan file as input
        gla_process = subprocess.run(
            ["python3", os.path.join(SCRIPT_DIR, "GLA.py")],
            input=open(file_path, "r").read(),
            text=True
        )

        # Remove target.lan
        target_lan = os.path.join(SCRIPT_DIR, "target.lan")
        if os.path.exists(target_lan):
            os.remove(target_lan)

        # Execute LA.py with the corresponding .in file and compare its output to the .out file
        input_file = file_path[:-4] + ".in"
        expected_output_file = file_path[:-4] + ".out"
        
        with open(input_file, "r") as infile:
            la_process = subprocess.run(
                ["python3", os.path.join(ANALIZATOR_DIR, "LA.py")],
                input=infile.read(),
                text=True,
                capture_output=True
            )

        with open(expected_output_file, "r") as expected_output:
            # Compare LA.py output with expected .out file using diff
            diff_process = subprocess.run(
                ["diff", "-B"],
                input=la_process.stdout,
                text=True,
                capture_output=True
            )
            
            # Check if there is any difference
            if diff_process.stdout == "":
                print("OK")
            else:
                print(diff_process.stdout)

        print("*************************************************************")

        # Remove the 'tablice' directory again if it exists
        if os.path.exists(tablice_dir):
            shutil.rmtree(tablice_dir)
