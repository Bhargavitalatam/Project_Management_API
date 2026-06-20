import pytest
from fastapi.testclient import TestClient

def test_full_auth_and_project_lifecycle(client: TestClient):
    # 1. Register a user
    reg_response = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "password123"}
    )
    assert reg_response.status_code == 201
    assert reg_response.json()["email"] == "alice@example.com"
    assert "id" in reg_response.json()
    
    # Try duplicate registration (assert 409 Conflict exception handler is triggered)
    dup_response = client.post(
        "/api/auth/register",
        json={"email": "alice@example.com", "password": "password123"}
    )
    assert dup_response.status_code == 409
    assert dup_response.json()["error"] == "Email already in use"

    # 2. Login to get JWT
    login_response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "password123"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify protected profile endpoints (Requirement 3)
    profile_response = client.get("/api/auth/profile", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "alice@example.com"

    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "alice@example.com"
    
    # Missing token -> should raise 401
    profile_no_auth = client.get("/api/auth/profile")
    assert profile_no_auth.status_code == 401
    
    # Invalid token -> should raise 401
    profile_bad_auth = client.get("/api/auth/profile", headers={"Authorization": "Bearer badtoken"})
    assert profile_bad_auth.status_code == 401

    # 3. Create a project
    proj_response = client.post(
        "/api/projects",
        json={"name": "Alpha Project", "description": "Alice's primary project"},
        headers=headers
    )
    assert proj_response.status_code == 201
    project = proj_response.json()
    assert project["name"] == "Alpha Project"
    assert project["description"] == "Alice's primary project"
    project_id = project["id"]

    # 4. List projects (should include Alpha Project)
    list_response = client.get("/api/projects", headers=headers)
    assert list_response.status_code == 200
    projects = list_response.json()
    assert len(projects) == 1
    assert projects[0]["id"] == project_id

    # 5. Create a task under Alpha Project
    task_response = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Write unit tests", "description": "Make sure everything works", "status": "TODO"},
        headers=headers
    )
    assert task_response.status_code == 201
    task = task_response.json()
    assert task["title"] == "Write unit tests"
    assert task["status"] == "TODO"
    assert task["project_id"] == project_id
    task_id = task["id"]

    # 6. Update task status (PUT /api/tasks/{id})
    update_task_response = client.put(
        f"/api/tasks/{task_id}",
        json={"status": "IN_PROGRESS", "description": "Writing tests now"},
        headers=headers
    )
    assert update_task_response.status_code == 200
    assert update_task_response.json()["status"] == "IN_PROGRESS"
    assert update_task_response.json()["description"] == "Writing tests now"

    # 7. Access project under another user session
    # Register and login Bob
    bob_reg = client.post(
        "/api/auth/register",
        json={"email": "bob@example.com", "password": "password456"}
    )
    assert bob_reg.status_code == 201
    bob_login = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "password456"}
    )
    bob_token = bob_login.json()["access_token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # Bob lists projects (should be empty)
    bob_list = client.get("/api/projects", headers=bob_headers)
    assert len(bob_list.json()) == 0

    # Bob attempts to get Alice's project (should be 403 Forbidden)
    bob_get_alice_proj = client.get(f"/api/projects/{project_id}", headers=bob_headers)
    assert bob_get_alice_proj.status_code == 403

    # Bob attempts to create task on Alice's project (should be 403 Forbidden)
    bob_create_task = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Malicious Task"},
        headers=bob_headers
    )
    assert bob_create_task.status_code == 403

    # Bob attempts to update Alice's task (should be 403 Forbidden)
    bob_update_task = client.put(
        f"/api/tasks/{task_id}",
        json={"status": "DONE"},
        headers=bob_headers
    )
    assert bob_update_task.status_code == 403

    # 8. Test input validation logic (400 structured responses)
    # Empty project name
    bad_proj = client.post(
        "/api/projects",
        json={"name": "", "description": "Invalid project name"},
        headers=headers
    )
    assert bad_proj.status_code == 400
    assert "Validation Error" in bad_proj.json()["error"]
    
    # Invalid task status
    bad_task = client.post(
        f"/api/projects/{project_id}/tasks",
        json={"title": "Valid Title", "status": "INVALID_STATUS"},
        headers=headers
    )
    assert bad_task.status_code == 400
    assert "Validation Error" in bad_task.json()["error"]

    # 9. Delete Alice's project (cascades task deletion)
    del_proj = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert del_proj.status_code == 204

    # Try to access deleted project
    get_del = client.get(f"/api/projects/{project_id}", headers=headers)
    assert get_del.status_code == 404

    # Try to access deleted task (should be 404 since it cascaded)
    get_del_task = client.put(
        f"/api/tasks/{task_id}",
        json={"title": "Accessing deleted task"},
        headers=headers
    )
    assert get_del_task.status_code == 404
