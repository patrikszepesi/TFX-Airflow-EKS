from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import datetime
from random import randint
import tfx
from tfx import v1 as tfx
#from tfx.types import standard_artifacts
from tfx import types
from tfx.types.component_spec import ChannelParameter
from tfx.types.component_spec import ExecutionParameter
from tfx.dsl.components.base import base_component
from tfx.dsl.components.base import base_executor
from typing import Any, Dict, List, Text, Optional
from tfx.dsl.components.base import executor_spec
from tfx.types import channel_utils
from tfx.types import standard_artifacts



import urllib.request
import tempfile
import os
from tfx.orchestration.airflow.airflow_dag_runner import AirflowDagRunner
from tfx.orchestration.airflow.airflow_dag_runner import AirflowPipelineConfig

PIPELINE_NAME = "penguin-simple"
_pipeline_name="penguin-simple"

# Output directory to store artifacts generated from the pipeline.
PIPELINE_ROOT = os.path.join('pipelines', PIPELINE_NAME)
_pipeline_root = os.path.join('pipelines', _pipeline_name)

# Path to a SQLite DB file to use as an MLMD storage.
METADATA_PATH = os.path.join('metadata', PIPELINE_NAME, 'metadata.db')
_metadata_path = os.path.join('metadata', PIPELINE_NAME, 'metadata.db')

# Output directory where created models from the pipeline will be exported.
SERVING_MODEL_DIR = os.path.join('serving_model', PIPELINE_NAME)
_serving_model_dir = os.path.join('serving_model', _pipeline_name)


from absl import logging
logging.set_verbosity(logging.INFO)  # Set default logging level.

DATA_ROOT = tempfile.mkdtemp(prefix='tfx-data')  # Create a temporary directory.
_data_root = tempfile.mkdtemp(prefix='tfx-data')  # Create a temporary directory.

_data_url = 'https://raw.githubusercontent.com/tensorflow/tfx/master/tfx/examples/penguin/data/labelled/penguins_processed.csv'
_data_filepath = os.path.join(DATA_ROOT, "data.csv")
urllib.request.urlretrieve(_data_url, _data_filepath)

_penguin_root = os.path.join(os.environ['HOME'], 'airflow')
#/opt/airflow/dags

#_trainer_module_file = os.path.join(_penguin_root, 'dags', 'penguin_trainer.py')

_trainer_module_file='/opt/airflow/dags/penguin_trainer.py'

#_trainer_module_file = os.path.abspath('penguin_trainer.py')

_airflow_config = {
    'schedule_interval': None,
    'start_date': datetime.datetime(2019, 1, 1),
}


def _create_pipeline(pipeline_name: str, pipeline_root: str, data_root: str,
                     module_file: str, serving_model_dir: str,
                     metadata_path: str) -> tfx.dsl.Pipeline:
  """Creates a three component penguin pipeline with TFX."""
  # Brings data into the pipeline.
  example_gen = tfx.components.CsvExampleGen(input_base=data_root)

  class HelloComponentSpec(types.ComponentSpec):
      """ComponentSpec for Custom TFX Hello World Component."""

      PARAMETERS = {
          # These are parameters that will be passed in the call to
          # create an instance of this component.
          'name': ExecutionParameter(type=str),
      }
      INPUTS = {
          # This will be a dictionary with input artifacts, including URIs
          'input_data': ChannelParameter(type=standard_artifacts.Examples),
      }
      OUTPUTS = {
          # This will be a dictionary which this component will populate
          'output_data': ChannelParameter(type=standard_artifacts.Examples),
      }

  class Executor(base_executor.BaseExecutor):
      """Executor for HelloComponent."""

      def Do(self, input_dict: Dict[Text, List[types.Artifact]],
             output_dict: Dict[Text, List[types.Artifact]],
             exec_properties: Dict[Text, Any]) -> None:


          split_to_instance = "Hello World"
          print(split_to_instance)

  class HelloComponent(base_component.BaseComponent):
      """Custom TFX Hello World Component."""

      SPEC_CLASS = HelloComponentSpec
      EXECUTOR_SPEC = executor_spec.ExecutorClassSpec(Executor)

      def __init__(self,
                   input_data: types.Channel = None,
                   output_data: types.Channel = None,
                   name: Optional[Text] = None):
          if not output_data:
              output_data = channel_utils.as_channel([standard_artifacts.Examples()])

          spec = HelloComponentSpec(input_data=input_data,
                                    output_data=output_data, name=name)
          super(HelloComponent, self).__init__(spec=spec)


  hello = HelloComponent(
          input_data=example_gen.outputs['examples'], name='HelloWorld')


  # Uses user-provided Python function that trains a model.
  trainer = tfx.components.Trainer(
      module_file=module_file,
      examples=example_gen.outputs['examples'],
      train_args=tfx.proto.TrainArgs(num_steps=100),
      eval_args=tfx.proto.EvalArgs(num_steps=5))

  # Pushes the model to a filesystem destination.
  pusher = tfx.components.Pusher(
      model=trainer.outputs['model'],
      push_destination=tfx.proto.PushDestination(
          filesystem=tfx.proto.PushDestination.Filesystem(
              base_directory=serving_model_dir)))

  # Following three components will be included in the pipeline.
  components = [
      example_gen,
      hello,
      trainer,
      pusher,
  ]

  return tfx.dsl.Pipeline(
      pipeline_name=pipeline_name,
      pipeline_root=pipeline_root,
      metadata_connection_config=tfx.orchestration.metadata
      .sqlite_metadata_connection_config(metadata_path),
      components=components)

#nohup kubectl port-forward svc/$RELEASE_NAME-webserver 8080:8080 --namespace $NAMESPACE &

#DAG=tfx.orchestration.LocalDagRunner().run(
 # _create_pipeline(
  #    pipeline_name=PIPELINE_NAME,
   #   pipeline_root=PIPELINE_ROOT,
    #  data_root=DATA_ROOT,
     # module_file=_trainer_module_file,
      #serving_model_dir=SERVING_MODEL_DIR,
      #metadata_path=METADATA_PATH))



DAG = AirflowDagRunner(AirflowPipelineConfig(_airflow_config)).run(
 _create_pipeline(
    pipeline_name=PIPELINE_NAME,
    pipeline_root=PIPELINE_ROOT,
    data_root=DATA_ROOT,
    module_file=_trainer_module_file,
    serving_model_dir=SERVING_MODEL_DIR,
    metadata_path=METADATA_PATH))

