from dataforseo_client.api_client import RestClient
from dotenv import load_dotenv

load_dotenv()

# You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
client = RestClient(LOGIN, PASSWORD)
post_data = dict()
# simple way to set a task
post_data[len(post_data)] = dict(
    location_name="United States",
    language_name="English (United States)",
    keyword="shoes"
)
# after a task is completed, we will send a GET request to the address you specify
# instead of $id and $tag, you will receive actual values that are relevant to this task
post_data[len(post_data)] = dict(
    location_name="United States",
    language_name="English (United States)",
    keyword="shoes",
    priority=2,
    tag="some_string_123",
    pingback_url="https://your-server.com/pingscript?id=$id&tag=$tag"
)
# after a task is completed, we will send a GET request to the address you specify
# instead of $id and $tag, you will receive actual values that are relevant to this task
post_data[len(post_data)] = dict(
    location_name="United States",
    language_name="English (United States)",
    keyword="shoes",
    postback_data="html",
    postback_url="https://your-server.com/postbackscript"
)
# POST /v3/merchant/amazon/products/task_post
response = client.post("/v3/merchant/amazon/products/task_post", post_data)
# you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
if response["status_code"] == 20000:
    print(response)
    # do something with result
else:
    print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))



# from client import RestClient
# from dotenv import load_dotenv

# load_dotenv()
# # You can download this file from here https://cdn.dataforseo.com/v3/examples/python/python_Client.zip
# client = RestClient(LOGIN, PASSWORD)
# # 1 - using this method you can get a list of completed tasks
# # GET /v3/merchant/amazon/products/tasks_ready
# response = client.get("/v3/merchant/amazon/products/tasks_ready")
# # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
# if response['status_code'] == 20000:
#     results = []
#     for task in response['tasks']:
#         if (task['result'] and (len(task['result']) > 0)):
#             for resultTaskInfo in task['result']:
#                 # 2 - using this method you can get results of each completed task
#         # GET /v3/merchant/amazon/products/task_get/advanced/$id
#                 if(resultTaskInfo['endpoint_advanced']):
#                     results.append(client.get(resultTaskInfo['endpoint_advanced']))
#                 '''
#                 # 3 - another way to get the task results by id
#                 # GET /v3/merchant/amazon/products/task_get/advanced/$id              
#                 if(resultTaskInfo['id']):
#                     results.append(client.get("/v3/merchant/amazon/products/task_get/advanced/" + resultTaskInfo['id']))
#                 '''
#     print(results)
#     # do something with result
# else:
#     print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))
