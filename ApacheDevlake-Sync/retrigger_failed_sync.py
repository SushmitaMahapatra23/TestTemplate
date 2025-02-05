from devlake_utils import DevLake
import os

def retrigger_project_sync(devlake, blueprint_id):
    last_successful_sync_time = devlake.resolve_last_sync_time(blueprint_id)
    payload = {
        "fullSync": True,
        "skipCollectors": False,
        "skipOnFail": True,
        "timeAfter": last_successful_sync_time
    }
    response = devlake.make_api_call(f"/api/rest/blueprints/{blueprint_id}/trigger", method="POST", payload=payload)
    if response:
        print(f"Blueprint {blueprint_id} re-triggered successfully with timeAfter {last_successful_sync_time}")
    else:
        print(f"Failed to re-trigger blueprint {blueprint_id}: {response}")

def retrigger_task_sync(devlake, task_id):
    response = devlake.make_api_call(f"/api/rest/tasks/{task_id}/rerun", method="POST")
    if response:
        print(f"Task {task_id} re-triggered successfully")
    else:
        print(f"Failed to re-trigger task {task_id}: {response}")


def retrigger_failed_sync(devlake, blueprint_id):
    pipeline_data = devlake.pipeline_data.get(blueprint_id)
    if pipeline_data:
        pipelines = pipeline_data.get('pipelines', [])
        if pipelines:
            latest_pipeline = pipelines[0]
            pipeline_status = latest_pipeline.get('status')

            if pipeline_status in ["TASK_COMPLETED", "TASK_RUNNING","TASK_CREATED"]:
                print(f"Pipeline for blueprint {blueprint_id} is in status: {pipeline_status}; skipping.")
                return
            else:
                subtasks_data = devlake.make_api_call(f"/api/rest/pipelines/{latest_pipeline['id']}/subtasks")
                if subtasks_data:
                    tasks_ids = [task['id'] for task in subtasks_data.get('subtasks', [])
                                if task.get('status') in ("TASK_FAILED", "TASK_CREATED")]
                    if len(tasks_ids) == 1:
                        retrigger_task_sync(devlake, tasks_ids[0])
                    elif len(tasks_ids) > 1:
                        retrigger_project_sync(devlake, blueprint_id)
        else:
            print(f"No pipelines found for blueprint {blueprint_id}. Triggering sync.")
            retrigger_project_sync(devlake, blueprint_id)

if __name__ == "__main__":
    DEVLAKE_INSTANCE = os.getenv('DEVLAKE_INSTANCE')
    DEV_API_TOKEN = os.getenv("DEVLAKE_API_TOKEN")
    
    devlake = DevLake(DEVLAKE_INSTANCE, DEV_API_TOKEN)
    blueprint_ids = devlake.blueprint_ids
    for blueprint_id in blueprint_ids:
        retrigger_failed_sync(devlake, blueprint_id)
