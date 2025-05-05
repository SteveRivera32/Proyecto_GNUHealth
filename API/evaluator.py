
from premsql.executors import SQLiteExecutor
from premsql.evaluator import Text2SQLEvaluator
import pandas as pd
from premsql.datasets import Text2SQLDataset


class Evaluator:
    """"
        Constructor:
        - eval_dataset: path to test dataset
        - database_url: path to database location
        - results_path: path generated sqls file.

    """


    def __init__ (self, eval_dataset, database_url,results_path):
        #we can build a custome  excecutor with BaseExecutor to use PostgreSQL instead
        self.database_url=database_url
        self.executor = SQLiteExecutor()
        self.evaluator = Text2SQLEvaluator(
                         executor=self.executor,
                         experiment_path="path to results ")
        if eval_dataset=="bird":
            self.bird_dataset = Text2SQLDataset(
            dataset_name='bird', split="validation", force_download=False,
            dataset_folder="/path/to/the/dataset"
            ).setup_dataset(num_rows=10)
        return 
    


    def run_single_test(self,generated_sql, groun_truth_sql):
          
       # Set a sample dataset path 
   
       sql = generated_sql
       # execute the SQL
       result = executor.execute_sql(
           sql=sql,
           dsn_or_db_path=self.database_url
       )

        # The purpose of this function run a single test or evaluation
    

    def run_full_test(self,dataset:str):
        if  str.lower(dataset)=="bird":

            # Now evaluate the models 

            # Initialize the generator 
           generator = Text2SQLGeneratorHF(
               model_or_name_or_path="premai-io/prem-1B-SQL",
               experiment_name="test_generators",
               device="cuda:0",
               type="test"
           )



           responses = generator.generate_and_save_results(
               dataset=bird_dataset,
               temperature=0.1,
               max_new_tokens=256
           )
           results = evaluator.execute(
           metric_name="accuracy",
           model_responses=response,
           filter_by="db_id",
           meta_time_out=10)


    




    


        