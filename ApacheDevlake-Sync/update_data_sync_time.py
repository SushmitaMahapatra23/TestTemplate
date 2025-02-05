from devlake_utils import DevLake
import os


def update_data_sync_time_range(devlake, blueprint_id):
    blueprint_details = devlake.blueprint_data.get(blueprint_id)
    if blueprint_details:
        last_successful_sync_time = devlake.resolve_last_sync_time(blueprint_id)
        blueprint_details['timeAfter'] = last_successful_sync_time.replace("+00:00Z", "Z")
        print(f"Updating timeRange for blueprint {blueprint_id}: {last_successful_sync_time}")
        response = devlake.make_api_call(
            f"/api/rest/blueprints/{blueprint_id}",
            method="PATCH",
            payload=blueprint_details
        )
        if response:
            print(f"Successfully updated sync time range for blueprint {blueprint_id}")
        else:
            print(f"Failed to update sync time range for blueprint {blueprint_id}")

if __name__ == "__main__":
    DEVLAKE_INSTANCE = os.getenv('DEVLAKE_INSTANCE')
    DEV_API_TOKEN = os.getenv("DEVLAKE_API_TOKEN")

    devlake = DevLake(DEVLAKE_INSTANCE, DEV_API_TOKEN)
    blueprint_ids = devlake.blueprint_ids
    for blueprint_id in blueprint_ids:
        update_data_sync_time_range(devlake, blueprint_id)
