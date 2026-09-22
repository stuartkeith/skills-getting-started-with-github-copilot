from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    # (no setup needed)

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_known_activity_shape(client):
    # Arrange
    # (no setup needed, activities are seeded by default)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    chess_club = body["Chess Club"]
    assert set(["description", "schedule", "max_participants", "participants"]) <= chess_club.keys()


def test_signup_for_activity_succeeds(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_for_activity_duplicate_email_fails(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "User already signed up for this activity"


def test_signup_for_unknown_activity_fails(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Not A Real Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_full_activity_fails(client):
    # Arrange
    activity_name = "Basketball Team"
    activity = activities[activity_name]
    for i in range(activity["max_participants"]):
        client.post(f"/activities/{activity_name}/signup", params={"email": f"student{i}@mergington.edu"})

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup", params={"email": "overflow@mergington.edu"}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_unregister_from_activity_succeeds(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_from_unknown_activity_fails(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Not A Real Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_user_not_signed_up_fails(client):
    # Arrange
    email = "notregistered@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "User is not signed up for this activity"
