"""Verify relative imports in mongomock_ng/ don't cause circular imports."""

from unittest import TestCase


class ImportRelativeTest(TestCase):
    """Import every source module that was changed."""

    def test__import_mongo_client(self):
        import mongomock_ng.mongo_client  # noqa: F401

    def test__import_database(self):
        import mongomock_ng.database  # noqa: F401

    def test__import_aggregate(self):
        import mongomock_ng.aggregate  # noqa: F401

    def test__import_store(self):
        import mongomock_ng.store  # noqa: F401

    def test__import_gridfs(self):
        import mongomock_ng.gridfs  # noqa: F401

    def test__import_codec_options(self):
        import mongomock_ng.codec_options  # noqa: F401

    def test__import_collection(self):
        import mongomock_ng.collection  # noqa: F401

    def test__import_everything(self):
        import mongomock_ng

        self.assertTrue(hasattr(mongomock_ng, 'SERVER_VERSION'))
        self.assertTrue(hasattr(mongomock_ng, 'utcnow'))

    def test__server_version_accessible(self):
        import mongomock_ng

        self.assertIsInstance(mongomock_ng.SERVER_VERSION, str)

    def test__utcnow_accessible(self):
        import mongomock_ng

        self.assertTrue(callable(mongomock_ng.utcnow))

    def test__gridfs_imports_resolve(self):
        from mongomock_ng.gridfs import _MongoMockGridOutCursor
        from mongomock_ng.gridfs import enable_gridfs_integration

        self.assertTrue(callable(enable_gridfs_integration))
        self.assertTrue(hasattr(_MongoMockGridOutCursor, 'next'))

    def test__relative_imports_match_absolute(self):
        from mongomock_ng import helpers as absolute_helpers
        from mongomock_ng import mongo_client
        from mongomock_ng.collection import Collection
        from mongomock_ng.database import Database

        self.assertIsNotNone(absolute_helpers)
        self.assertIsNotNone(Database)
        self.assertIsNotNone(Collection)
        self.assertTrue(hasattr(mongo_client, 'MongoClient'))
