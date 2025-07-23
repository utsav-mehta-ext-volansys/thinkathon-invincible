# # pylint: disable=import-error
# """Test Cases for Note Module"""
# from fastapi.testclient import TestClient
# from main import app

# client = TestClient(app)

# NOTE_ID = "653b3e22a39a42f8740f41c3"

# def test_home():
#     """Home Screen Route"""
#     response = client.get("/")
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello World"}
# def test_create_note():
#     """POST: Create Note"""
#     sample_payload = {
#         "title": "Title",
#         "desc": "Description",
#         "important": True
#     }
#     response = client.post("/api/note/create", json=sample_payload)
#     assert response.status_code == 201
#     sample_response = response.json()
#     assert response.json() == {
#         "status": "Ok",
#         "data": [
#             {
#                 "id": sample_response['data'][0]['id'],
#                 "title": "Title",
#                 "desc": "Description",
#                 "important": True
#             }
#         ]
#     }
# def test_find_one_note():
#     """GET: Get Particular Note"""
#     response = client.get(f"/api/note/getOne/{NOTE_ID}")
#     assert response.status_code == 200
#     assert response.json() == {
#         "status": "Ok",
#         "data": [
#             {
#                 "id": NOTE_ID,
#                 "title": "Title",
#                 "desc": "Description",
#                 "important": True
#             }
#         ]
#     }
# def test_update_one():
#     """PATCH: Update Note"""
#     updated_payload = {
#         "title": "Updated Title",
#         "desc": "Description",
#         "important": True
#     }
#     response = client.patch(f"/api/note/update/{NOTE_ID}", json=updated_payload)
#     assert response.status_code == 202
#     assert response.json() == {
#         "status": "Ok",
#         "data": [
#             {
#                 "id": NOTE_ID,
#                 "title": "Updated Title",
#                 "desc": "Description",
#                 "important": True
#             }
#         ]
#     }
# def test_delete_note():
#     """DELETE: Delete Note"""
#     response = client.delete(f"/api/note/delete/{NOTE_ID}")
#     assert response.status_code == 200
#     assert response.json() == {"status": "Ok","message": "User Deleted Successfully!"}
