import json
import os
import re
import shutil
from typing import Dict, List
from backend.data.models import UserQueryRecord, ScientificAbstract
from backend.data.interface import UserQueryDataStore
import logging


class LocalJSONStore(UserQueryDataStore):
    """ 
    For local testing, to simulate database via local JSON files. 
    """

    def __init__(self, storage_folder_path: str):
        self.storage_folder_path = storage_folder_path
        self.index_file_path = os.path.join(storage_folder_path, 'index.json')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Đảm bảo thư mục lưu trữ tồn tại
        os.makedirs(self.storage_folder_path, exist_ok=True)
        
        # Kiểm tra và tạo file index nếu cần
        if not os.path.exists(self.index_file_path):
            with open(self.index_file_path, 'w', encoding='utf-8') as file:
                json.dump({}, file, ensure_ascii=False, indent=4)
                
        self.metadata_index = self._rebuild_index()  # Initialize the index on startup

    def get_new_query_id(self) -> str:
        """
        Compute a new query ID by incrementing previous query ID integer suffix by 1.
        """
        try:
            with open(self.index_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
            # Tạo file index mới nếu không tồn tại hoặc bị lỗi
            with open(self.index_file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                
        keys = [k for k in data.keys() if k.startswith('query_')]
        if not keys:
            return 'query_1'
        numbers = [int(k.split('_')[-1]) for k in keys]
        max_number = max(numbers) if numbers else 0
        return f'query_{max_number + 1}'

    def read_dataset(self, query_id: str) -> List[ScientificAbstract]:
        """ 
        Read dataset containing abstracts from local storage. 
        """
        try:
            with open(f'{self.storage_folder_path}/{query_id}/abstracts.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                return [ScientificAbstract(**abstract_record) for abstract_record in data]
        except FileNotFoundError:
            self.logger.error(f'The JSON file for this query: {query_id} was not found.')
            raise FileNotFoundError('JSON file was not found.')
        except json.JSONDecodeError as e:
            self.logger.error(f'Error decoding JSON from file for query {query_id}: {e}')
            raise ValueError(f'JSON decode error: {e}')

    def save_dataset(self, abstracts_data: List[ScientificAbstract], user_query: str) -> str:
        """ 
        Save abstract dataset and query metadata to local storage, rebuild index, and return query ID.
        """
        query_id = None
        try:
            query_id = self.get_new_query_id()
            user_query_details = UserQueryRecord(
                user_query_id=query_id, 
                user_query=user_query
            )

            # Tạo thư mục cho query mới
            query_dir = os.path.join(self.storage_folder_path, query_id)
            os.makedirs(query_dir, exist_ok=True)
            
            # Chuyển đổi authors từ list thành string trước khi lưu
            list_of_abstracts = []
            for model in abstracts_data:
                abstract_dict = model.model_dump()
                if isinstance(abstract_dict.get("authors"), list):
                    abstract_dict["authors"] = ", ".join(abstract_dict["authors"])
                list_of_abstracts.append(abstract_dict)
            
            # Lưu danh sách abstract
            abstracts_path = os.path.join(query_dir, "abstracts.json")
            with open(abstracts_path, "w", encoding='utf-8') as file:
                json.dump(list_of_abstracts, file, indent=4, ensure_ascii=False)

            # Lưu chi tiết query
            query_details_path = os.path.join(query_dir, "query_details.json")
            with open(query_details_path, "w", encoding='utf-8') as file:
                # Sử dụng ensure_ascii=False để bảo toàn ký tự Unicode
                # Chuyển model_dump_json thành dict trước, rồi sau đó dump
                json_dict = user_query_details.model_dump()
                json.dump(json_dict, file, indent=4, ensure_ascii=False)

            self.logger.info(f"Data for query ID {query_id} saved successfully.")
            self._rebuild_index()  # Rebuild index after saving new data

            return query_id

        except Exception as e:
            self.logger.error(f"Failed to save dataset for query ID {query_id}: {e}")
            if query_id:
                # Xóa thư mục đã tạo nếu có lỗi xảy ra
                query_dir = os.path.join(self.storage_folder_path, query_id)
                if os.path.exists(query_dir):
                    try:
                        shutil.rmtree(query_dir)
                        self.logger.info(f"Cleaned up directory '{query_dir}' after error.")
                    except Exception as cleanup_err:
                        self.logger.error(f"Failed to clean up after error: {cleanup_err}")
            raise RuntimeError(f"Failed to save dataset due to an error: {e}")
        
    def delete_dataset(self, query_id: str) -> None:
        """ 
        Delete abstracts dataset and query metadata from local storage. 
        """
        path_to_data = os.path.join(self.storage_folder_path, query_id)
        if os.path.exists(path_to_data):
            shutil.rmtree(path_to_data)
            self.logger.info(f"Directory '{path_to_data}' has been deleted.")
            self._rebuild_index()  # Rebuild index after deleting data
        else:
            self.logger.warning(f"Directory '{path_to_data}' does not exist and cannot be deleted.")

    def get_list_of_queries(self) -> Dict[str, str]:
        """ 
        Get a dictionary containing query ID (as a key) and original user query (as a value) from the index. 
        """
        return self.metadata_index

    def _rebuild_index(self) -> Dict[str, str]:
        """ 
        Rebuild the index from all query details files, to serve for a lookup purposes.
        """
        index = {}
        
        # Kiểm tra thư mục tồn tại trước khi liệt kê
        if not os.path.exists(self.storage_folder_path):
            os.makedirs(self.storage_folder_path, exist_ok=True)
            self.logger.info(f"Created storage folder at {self.storage_folder_path}")
            return {}
            
        try:
            # Lọc các thư mục khớp với mẫu query_X
            subdirs = [name for name in os.listdir(self.storage_folder_path) 
                      if os.path.isdir(os.path.join(self.storage_folder_path, name)) 
                      and re.match(r'query_\d+', name)]
            
            query_data_paths = [os.path.join(self.storage_folder_path, name) for name in subdirs]
            
            for query_data_path in query_data_paths:
                metadata_path = os.path.join(query_data_path, 'query_details.json')
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as file:
                            metadata = json.load(file)
                            index[metadata['user_query_id']] = metadata['user_query']
                    except json.JSONDecodeError as e:
                        self.logger.warning(f"Error decoding JSON from {metadata_path}: {e}")
                        continue
                    except Exception as e:
                        self.logger.warning(f"Error processing {metadata_path}: {e}")
                        continue
                else:
                    self.logger.warning(f"No query_details.json file found in {query_data_path}")
            
            # Lưu index đã cập nhật
            with open(self.index_file_path, 'w', encoding='utf-8') as file:
                json.dump(index, file, indent=4, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error rebuilding index: {e}")
            # Nếu không thể rebuild index, trả về dict trống hoặc index hiện tại
            if hasattr(self, 'metadata_index'):
                return self.metadata_index
            return {}
            
        self.metadata_index = index
        return index