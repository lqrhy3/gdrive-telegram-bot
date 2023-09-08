import os
from collections import defaultdict
from typing import List

from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GDriveFolderTraverser:
    def __init__(self, service):
        self._service = service

        self._root_folder = None
        self._current_folder = None
        self._folder_name_to_children = None
        self._folder_name_to_parent = None
        self._folder_name_to_id = None

    def init_folder_structure(self):
        folder_list = self._query_folder_list()
        folder_id_to_name = self._make_folder_id_to_name_map(folder_list)
        adjacency_lists = self._make_forward_and_backward_adjacency_lists(folder_list, folder_id_to_name)
        root_folder = self._find_root_folder(*adjacency_lists)

        self._root_folder = self._current_folder = root_folder
        self._folder_name_to_children = adjacency_lists[0]
        self._folder_name_to_parent = adjacency_lists[1]
        self._folder_name_to_id = {v: k for k, v in folder_id_to_name.items()}

    def get_current_children(self) -> List[str]:
        assert self._current_folder is not None
        children = self._folder_name_to_children[self._current_folder]
        return sorted(children)

    def move_to(self, folder_name):
        assert self._current_folder is not None
        self._current_folder = folder_name

    def move_back(self):
        assert self._current_folder is not None
        self._current_folder = self._folder_name_to_parent[self._current_folder]

    def is_in_root(self) -> bool:
        assert self._current_folder is not None
        return self._current_folder == self._root_folder

    def get_current_folder_id(self) -> str:
        return self._folder_name_to_id[self._current_folder]

    def get_current_path(self) -> str:
        assert self._current_folder is not None
        path = []
        folder = self._current_folder
        while folder != self._root_folder:
            path.append(folder + '/')
            folder = self._folder_name_to_parent[folder]

        path.append('/')  # root
        path = path[::-1]
        return ''.join(path)

    def _query_folder_list(self):
        try:
            files = []
            page_token = None
            while True:
                response = self._service.files().list(
                    q="mimeType = 'application/vnd.google-apps.folder'",
                    spaces='drive',
                    fields='nextPageToken, files(id, name, parents)',
                    pageToken=page_token
                ).execute()

                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken', None)
                if page_token is None:
                    break

        except HttpError as error:
            print(F'An error occurred: {error}')
            files = None

        return files

    @staticmethod
    def _make_folder_id_to_name_map(folder_list):
        id_to_name = dict()
        for folder in folder_list:
            id_, name = folder.get('id', None), folder.get('name', None)
            if not (id_ or name) or id_ in id_to_name:
                continue
            id_to_name[id_] = name

        return id_to_name

    @staticmethod
    def _make_forward_and_backward_adjacency_lists(folder_list, id_to_name_map):
        parent_to_children = defaultdict(list)
        children_to_parent = dict()
        for folder in folder_list:
            id_, name = folder.get('id', None), folder.get('name', None)

            if not id_ or not name:
                continue
            parent_ids = folder.get('parents', [])

            if parent_ids:
                parent_id = parent_ids[0]
                parent_name = id_to_name_map[parent_id]
                name = id_to_name_map[id_]
                parent_to_children[parent_name].append(name)
                children_to_parent[name] = parent_name

        return parent_to_children, children_to_parent

    @staticmethod
    def _find_root_folder(parent_to_children, children_to_parent):
        for folder_name in parent_to_children:
            if folder_name not in children_to_parent:
                return folder_name
        raise RuntimeError('No root directory found.')


def create_service(service_account_file: str):
    scopes = ['https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)
    service = build('drive', 'v3', credentials=credentials)
    return service


def upload_file_to_gdrive(service, local_path: str, upload_folder_id: str, upload_file_name: str):
    file_metadata = {
        'name': upload_file_name,
        'parents': [upload_folder_id]
    }
    media = MediaFileUpload(local_path, resumable=True)
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
