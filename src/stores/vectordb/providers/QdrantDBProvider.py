from ..VectorDBInterface import VectorDBInterface
import logging
from ..VectorDBEnums import DistanceMethodEnums
from qdrant_client import QdrantClient, models
from typing import List
from models.db_schemes import RetrievedDocument


class QdrantDBProvider(VectorDBInterface):

    def __init__(self, db_path: str, DistanceMethod: str):

        self.db_path = db_path
        self.DistanceMethod = None
        self.client = None
        if DistanceMethod == DistanceMethodEnums.COSINE.value:
            self.DistanceMethod = models.Distance.COSINE
        elif DistanceMethod == DistanceMethodEnums.DOT_PRODUCT.value:
            self.DistanceMethod = models.Distance.DOT_PRODUCT

        self.logger = logging.getLogger("QdrantDB")

    def connect(self):
        self.client = QdrantClient(path=self.db_path)
        self.logger.info("Connected to QdrantDB at path: %s", self.db_path)

    def disconnect(self):
        self.client = None
        self.logger.info("Disconnected from QdrantDB")

    def is_collection_exists(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name)

    def list_all_collections(self) -> List:
        return self.client.get_collections()

    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name)

    def delete_collection(self, collection_name):
        if self.is_collection_exists(collection_name):
            return self.client.delete_collection(collection_name)

    def create_collection(
        self, collection_name: str, vector_size: int, do_reset: bool = False
    ):
        if do_reset:
            _ = self.delete_collection(collection_name)

        if not self.is_collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size, distance=self.DistanceMethod
                ),
            )
            return True
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List,
        metadata: dict = None,
        record_id: str = None,
    ):

        if not self.is_collection_exists(collection_name):
            self.logger.error(
                "Collection %s does not exist. Please create it before inserting data.",
                collection_name,
            )
            return False
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={"text": text, "metadata": metadata},
                    )
                ],
            )
        except Exception as e:
            self.logger.error("Error inserting record: %s", str(e))
            return False
        return True

    def insert_many(
        self,
        collection_name: str,
        texts: List,
        vectors: List,
        metadata: List = None,
        record_ids: List = None,
        batch_size: int = 50,
    ):

        if not self.is_collection_exists(collection_name):
            self.logger.error(
                "Collection %s does not exist. Please create it before inserting data.",
                collection_name,
            )
            return False

        if metadata is None:
            metadata = [None] * len(texts)
        if record_ids is None:
            record_ids = range(0, len(texts))

        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_vectors = vectors[i : i + batch_size]
            batch_metadata = metadata[i : i + batch_size]
            batch_record_ids = record_ids[i : i + batch_size]

            batch_records = [
                models.Record(
                    id=batch_record_ids[x] if batch_record_ids[x] else uuid.uuid4().hex,
                    vector=batch_vectors[x],
                    payload={"text": batch_texts[x], "metadata": batch_metadata[x]},
                )
                for x in range(len(batch_texts))
            ]
            try:
                _ = self.client.upload_records(
                    collection_name=collection_name, records=batch_records
                )
            except Exception as e:
                self.logger.error(f"Error inserting batch:{e}")
                return False
        return True

    def search_by_vector(self, collection_name: str, query_vector: List, limit: int):
        results = self.client.search(
            collection_name=collection_name, query_vector=query_vector, limit=limit
        )
        if not results or len(results) == 0:
            return None

        return [
            RetrievedDocument(**{"text": result.payload["text"], "score": result.score})
            for result in results
        ]
