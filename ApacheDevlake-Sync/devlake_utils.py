import requests
from datetime import datetime, timedelta

class DevLake:
    def __init__(self, devlake_instance, devlake_api_token):
        self.DEVLAKE_INSTANCE = devlake_instance
        self.DEVLAKE_API_TOKEN = devlake_api_token
        self.blueprint_data = self.fetch_blueprints()
        self.blueprint_ids = list(self.blueprint_data.keys())
        self.pipeline_data = self.fetch_pipelines()


    def make_api_call(self, endpoint, method="GET", payload=None, params=None):
        """
        Makes an API call to a DevLake endpoint.

        :param endpoint: API endpoint (e.g., "/projects")
        :param method: HTTP method (GET, POST, PUT, DELETE, etc.)
        :param payload: Data to be sent in the request body (for POST/PUT)
        :param params: Query parameters for the request (for GET)
        :return: Response object
        """
        url = f"{self.DEVLAKE_INSTANCE}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.DEVLAKE_API_TOKEN}",
            "accept": "application/json",
        }
        if payload:
            headers["Content-Type"] = "application/json"
        response = requests.request(
            method=method.upper(),
            url=url,
            headers=headers,
            json=payload,
            params=params
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error making API call to {url}: {response.text}")
        
    def fetch_blueprints(self):
        blueprints = {}
        data = self.make_api_call("/api/rest/blueprints", params={"page": 1, "pageSize": 200})
        if data:
            for blueprint in data.get('blueprints', []):
                blueprint_id = blueprint.get('id')
                blueprints[blueprint_id] = blueprint
            return blueprints
        else:
            raise Exception("Failed to fetch blueprints")
        
        
    def fetch_pipelines(self):
        pipelines = {}
        blueprint_ids = self.blueprint_ids
        for blueprint_id in blueprint_ids:
            print(f"Fetching pipelines for blueprint {blueprint_id}")
            pipelines[blueprint_id] = self.make_api_call(f"/api/rest/blueprints/{blueprint_id}/pipelines")
        return pipelines
        

    def resolve_last_sync_time(self, blueprint_id):
        pipeline_data = self.pipeline_data.get(blueprint_id)
        if pipeline_data:
            pipelines = pipeline_data.get('pipelines', [])
            for pipeline in pipelines:
                if pipeline.get('status') == "TASK_COMPLETED":
                    finished_at = pipeline.get('finishedAt')
                    finished_at_datetime = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
                    return (finished_at_datetime - timedelta(days=1)).isoformat(timespec='milliseconds') + 'Z'
        print(f"No successful sync found for blueprint {blueprint_id}; using one week ago timestamp")
        return (datetime.now() - timedelta(weeks=1)).isoformat(timespec='milliseconds') + 'Z'
