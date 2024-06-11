import mlflow
import pickle

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data(train_model, **kwargs):

    mlflow.set_tracking_uri("http://mlflow:5000")  #sqlite:///mlflow/mlflow.db
    mlflow.set_experiment("orchestration_hw3")

    dicVec, linReg = train_model

        
    mlflow.sklearn.log_model(linReg, artifact_path="hw3_lin_reg_mod")

    filename = "dict_vectorizer.pkl"
    with open(filename, "wb") as f_out:
        pickle.dump(dicVec, f_out)
    mlflow.log_artifact(filename, artifact_path="hw3_lin_reg_dv")
