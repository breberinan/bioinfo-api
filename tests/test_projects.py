async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_create_project(client):
    response = await client.post(
        "/projects/", json={"name": "Exome study", "description": "Pilot cohort"}
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Exome study"
    assert body["description"] == "Pilot cohort"
    assert "created_at" in body


async def test_create_project_requires_name(client):
    response = await client.post("/projects/", json={"description": "no name"})
    assert response.status_code == 422


async def test_list_projects(client):
    assert (await client.get("/projects/")).json() == []
    await client.post("/projects/", json={"name": "A"})
    await client.post("/projects/", json={"name": "B"})
    response = await client.get("/projects/")
    assert response.status_code == 200
    assert [p["name"] for p in response.json()] == ["A", "B"]


async def test_delete_project(client):
    created = (await client.post("/projects/", json={"name": "Temp"})).json()
    response = await client.delete(f"/projects/{created['id']}/")
    assert response.status_code == 204
    assert (await client.get("/projects/")).json() == []


async def test_delete_missing_project_returns_404(client):
    response = await client.delete("/projects/999/")
    assert response.status_code == 404


async def test_list_projects_supports_pagination(client):
    for name in ["A", "B", "C"]:
        await client.post("/projects/", json={"name": name})
    response = await client.get("/projects/", params={"skip": 1, "limit": 1})
    assert [p["name"] for p in response.json()] == ["B"]


async def test_list_projects_rejects_invalid_limit(client):
    response = await client.get("/projects/", params={"limit": 0})
    assert response.status_code == 422
