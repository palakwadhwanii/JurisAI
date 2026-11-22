import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.auth_service import AuthService, get_auth_service

@pytest.fixture
def auth_client():
    return TestClient(app)

class TestAuthAndSearchHistory:
    """
    Evaluates Authentication & Search History System:
    - User registration and duplicate prevention
    - User login, credential validation, and token issuance
    - Token authentication and session retrieval
    - Search/Case analysis history logging and restoration
    - History item deletion and clearing
    - Seamless automatic history logging when analyzing cases
    """

    def test_user_registration_and_validation(self, auth_client: TestClient):
        import uuid
        unique_username = f"advocate_{uuid.uuid4().hex[:8]}"
        unique_email = f"{unique_username}@jurisai.in"

        # 1. Successful registration
        payload = {
            "username": unique_username,
            "email": unique_email,
            "password": "SecurePassword123!",
            "full_name": "Senior Advocate Sharma"
        }
        res = auth_client.post("/api/auth/register", json=payload)
        assert res.status_code == 200, res.text
        data = res.json()
        assert "token" in data and len(data["token"]) > 20
        assert data["user"]["username"] == unique_username
        assert data["user"]["email"] == unique_email
        assert data["user"]["full_name"] == "Senior Advocate Sharma"

        # 2. Duplicate registration rejection
        dup_res = auth_client.post("/api/auth/register", json=payload)
        assert dup_res.status_code == 400
        assert "already" in dup_res.json()["detail"].lower()

    def test_user_login_and_logout(self, auth_client: TestClient):
        import uuid
        uname = f"counsel_{uuid.uuid4().hex[:8]}"
        email = f"{uname}@bar.in"
        pwd = "CourtPassword456"

        # Register
        auth_client.post("/api/auth/register", json={
            "username": uname,
            "email": email,
            "password": pwd,
            "full_name": "Counsel Verma"
        })

        # Login with username
        login_res1 = auth_client.post("/api/auth/login", json={
            "username_or_email": uname,
            "password": pwd
        })
        assert login_res1.status_code == 200
        assert "token" in login_res1.json()

        # Login with email
        login_res2 = auth_client.post("/api/auth/login", json={
            "username_or_email": email,
            "password": pwd
        })
        assert login_res2.status_code == 200
        token = login_res2.json()["token"]

        # Invalid password
        fail_res = auth_client.post("/api/auth/login", json={
            "username_or_email": uname,
            "password": "WrongPassword"
        })
        assert fail_res.status_code == 401

        # Check /api/auth/me
        me_res = auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_res.status_code == 200
        assert me_res.json()["username"] == uname

        # Logout
        logout_res = auth_client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_res.status_code == 200

        # After logout, token is invalid
        revoked_res = auth_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert revoked_res.status_code == 401

    def test_search_history_crud_operations(self, auth_client: TestClient):
        import uuid
        uname = f"historian_{uuid.uuid4().hex[:8]}"
        email = f"{uname}@court.in"
        reg_res = auth_client.post("/api/auth/register", json={
            "username": uname,
            "email": email,
            "password": "HistoryPassword789"
        })
        token = reg_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. History initially empty
        empty_res = auth_client.get("/api/history", headers=headers)
        assert empty_res.status_code == 200
        assert empty_res.json() == []

        # 2. Add history record
        save_payload = {
            "query_text": "Seeking divorce under Section 13B mutual consent with cooling off waiver.",
            "case_type": "Mutual Consent Divorce",
            "outcome": "PASS",
            "summary": "Section 13B cooling-off period waiver under Shilpa Sailesh",
            "analysis_id": "trace-test-hist-01",
            "analysis_data": {"test_key": "test_value_restored"}
        }
        add_res = auth_client.post("/api/history", json=save_payload, headers=headers)
        assert add_res.status_code == 200
        history_id = add_res.json()["id"]

        # 3. Retrieve history list
        list_res = auth_client.get("/api/history", headers=headers)
        assert list_res.status_code == 200
        history_list = list_res.json()
        assert len(history_list) == 1
        assert history_list[0]["id"] == history_id
        assert history_list[0]["case_type"] == "Mutual Consent Divorce"

        # 4. Retrieve single history item with full analysis data
        detail_res = auth_client.get(f"/api/history/{history_id}", headers=headers)
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["id"] == history_id
        assert detail["analysis_data"]["test_key"] == "test_value_restored"

        # 5. Delete single history item
        del_res = auth_client.delete(f"/api/history/{history_id}", headers=headers)
        assert del_res.status_code == 200

        # Verify list is empty again
        after_del = auth_client.get("/api/history", headers=headers)
        assert after_del.json() == []

    def test_automatic_history_recording_on_case_analysis(self, auth_client: TestClient):
        import uuid
        uname = f"practitioner_{uuid.uuid4().hex[:8]}"
        email = f"{uname}@delhibar.in"
        reg_res = auth_client.post("/api/auth/register", json={
            "username": uname,
            "email": email,
            "password": "PractitionerPassword789"
        })
        token = reg_res.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Analyze a case as an authenticated user
        case_narrative = (
            "Parties married in 2021 seek mutual consent divorce under section 13B and waiver of 6 months cooling off period."
        )
        an_res = auth_client.post(
            "/api/analyze",
            json={"case_text": case_narrative, "uploaded_documents": []},
            headers=headers
        )
        assert an_res.status_code == 200

        # Check that the analysis was automatically saved to user's history!
        hist_res = auth_client.get("/api/history", headers=headers)
        assert hist_res.status_code == 200
        items = hist_res.json()
        assert len(items) >= 1
        latest = items[0]
        assert "13b" in latest["query_text"].lower()
        assert latest["outcome"] in ["PASS", "RECOVERED"]
        assert len(latest["created_at"]) > 0

        # Fetch full restored record
        restored_res = auth_client.get(f"/api/history/{latest['id']}", headers=headers)
        assert restored_res.status_code == 200
        restored_data = restored_res.json()
        assert "analysis_data" in restored_data
        assert "case_state" in restored_data["analysis_data"]
        assert "final_judgment" in restored_data["analysis_data"]

