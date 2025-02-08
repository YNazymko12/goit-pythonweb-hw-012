# from unittest.mock import patch

# from conftest import test_user

# def test_get_me(client, get_token):
#     token = get_token
#     headers = {"Authorization": f"Bearer {token}"}
#     response = client.get("api/users/me", headers=headers)
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["username"] == test_user["username"]
#     assert data["email"] == test_user["email"]
#     assert "avatar" in data

# @patch("src.services.upload_file.UploadFileService.upload_file")
# def test_update_avatar_user(mock_upload_file, client, get_token):
#     # Мокаємо відповідь від сервісу завантаження файлів
#     fake_url = "<http://example.com/avatar.jpg>"
#     mock_upload_file.return_value = fake_url

#     # Токен для авторизації
#     headers = {"Authorization": f"Bearer {get_token}"}

#     # Файл, який буде відправлено
#     file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

#     # Відправка PATCH-запиту
#     response = client.patch("/api/users/avatar", headers=headers, files=file_data)

#     # Перевірка, що запит був успішним
#     assert response.status_code == 200, response.text

#     # Перевірка відповіді
#     data = response.json()
#     assert data["username"] == test_user["username"]
#     assert data["email"] == test_user["email"]
#     assert data["avatar"] == fake_url

#     # Перевірка виклику функції upload_file з об'єктом UploadFile
#     mock_upload_file.assert_called_once()
from datetime import date
from src.conf import messages
from fastapi import status

test_contact = {
    "first_name": "Johnny",
    "last_name": "Doe",
    "email": "johnny@example.com",
    "phone_number": "0931234567",
    "birthday": date(2010, 1, 10).isoformat(),
    "additional_data": "additional text",
}

def test_create_contact(client, get_token):
    response = client.post(
        "/api/contacts",
        json=test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_contact(client, get_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["first_name"] == test_contact["first_name"]
    assert "id" in data

def test_get_contact_not_found(client, get_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND

def test_get_contacts(client, get_token):
    response = client.get("/api/contacts", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["first_name"] == test_contact["first_name"]
    assert "id" in data[0]
    assert len(data) > 0

def test_update_contact(client, get_token):
    updated_test_contact = test_contact.copy()
    updated_test_contact["first_name"] = "New-name"
    response = client.put(
        "/api/contacts/1",
        json=updated_test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["first_name"] == updated_test_contact["first_name"]
    assert "id" in data
    assert data["id"] == 1

def test_update_contact_not_found(client, get_token):
    updated_test_contact = test_contact.copy()
    updated_test_contact["first_name"] = "New-name"
    response = client.put(
        "/api/contact/2",
        json=updated_test_contact,
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == "Not Found"

def test_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT, response.text
    data = response.content
    assert data == b""

def test_repeat_delete_contact(client, get_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND