from mage_ai.orchestration.triggers.api import trigger_pipeline

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom


@custom
def retrain(*args, **kwargs):
    trigger_pipeline(
        'pl_train_xgboost',
        check_status=True,
        error_on_failure=True,
        schedule_name='tg_retrain_model_xgboost',
        verbose=True,
    )