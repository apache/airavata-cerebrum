import zipfile
import os
import random
import string
import shutil

from airavata_sdk.clients.utils.experiment_handler_util import ExperimentHandlerUtil
from ipywidgets import widgets
from IPython.display import display


class CybershuttleHPCRun(object):

    def __init__(self, output='./'):
        configFile = "./settings.ini"
        self.experiment_handler = ExperimentHandlerUtil(configFile)
        self.output = output
        self.input_path = ""
        self.selected_compute_resource_name = ""
        self.selected_queue_name = ""

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            # Capture the decorator arguments and function arguments here

            self.input_path = kwargs['input']

            # Call the decorated function
            print("Executing user provided function...")
            func(*args, **kwargs)
            print("Function execution succeeded...")
            self._select_compute_resources()

        return wrapper

    def _run_on_hpc(self, local_input_path, compute_resource_name, queue_name, output_path):

        allen_v1 = "allen_v1_" + self._generate_random_string(4)

        print("Experiment name: ", allen_v1)
        print("local_data_directory: ", local_input_path)
        print("output_data_directory: ", output_path)
        print("scheduled compute resource: ", compute_resource_name)
        print("scheduled queue: ", queue_name)

        file_mapping = self._create_BMTK_file_mapping(local_input_path)

        print("Creating experiment ....")
        self.experiment_handler.launch_experiment(experiment_name=allen_v1,
                                                  description='allen_v1_experminent',
                                                  local_input_path=local_input_path,
                                                  input_file_mapping=file_mapping,
                                                  computation_resource_name=compute_resource_name,
                                                  queue_name=queue_name, output_path=output_path)

        zip_path = local_input_path + "/all_input.zip"
        self._unzip_and_delete(zip_path)

    def _create_BMTK_file_mapping(self, input_folder_path):
        file_mapping = {}
        self._create_zip(input_folder_path, "all_input.zip")
        input_file_list = self._get_file_list(input_folder_path)
        for x in input_file_list:
            if x.endswith(".zip"):
                file_mapping['Network Inputs'] = x
            elif x.endswith(".json"):
                file_mapping['Simulation Config File'] = x
        return file_mapping

    def _create_zip(self, folder_path, zip_file_name):
        with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=os.path.relpath(file_path, folder_path))

        # Delete subfolders
        for root, dirs, _ in os.walk(folder_path, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                shutil.rmtree(dir_path)

        # Move zip file to root folder
        zip_file_path = os.path.join(folder_path, zip_file_name)
        shutil.move(zip_file_name, zip_file_path)

    def _get_file_list(self, folder_path):
        file_list = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_list.append(file)
        return file_list

    def _generate_random_string(self, length):
        characters = string.ascii_lowercase
        random_string = ''.join(random.choice(characters) for _ in range(length))
        return random_string

    def _select_compute_resources(self):
        exp_conf = self.experiment_handler.experiment_conf
        options = exp_conf.COMPUTE_HOST_DOMAIN.split(',')
        print("select compute resource")
        dropdown = widgets.Dropdown(
            options=options,
            value=options[0],
            description='Select Compute Resources',
            disabled=False,
        )
        dropdown.observe(self._select_compute_resources_queue, names="value")
        display(dropdown)

    def _select_compute_resources_queue(self, compute_resource):
        selected_compute_resource = compute_resource.new
        self.selected_compute_resource_name = selected_compute_resource

        print("Select Compute Resources Queue ", self.selected_compute_resource_name)

        queues = self.experiment_handler.queue_names(selected_compute_resource)
        queue = widgets.Dropdown(
            options=queues,
            value=queues[0],
            description='Select Compute Resources Queue',
            disabled=False,
        )
        queue.observe(self._on_select_compute_queue, names="value")
        display(queue)

    def _on_select_compute_queue(self, queue_name):
        selected_queue_name = queue_name.new
        self.selected_queue_name = selected_queue_name
        print("selected compute resource queue ", self.selected_queue_name)
        self._run_on_hpc(self.input_path, self.selected_compute_resource_name, self.selected_queue_name,
                         output_path=self.output)

    def _unzip_and_delete(self, zip_file_path):
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(zip_file_path))
        os.remove(zip_file_path)
