import sys
import unittest
from unittest import mock
from unittest import skipIf

import mongomock_ng as mongomock


try:
    from bson import codec_options
    from pymongo.read_preferences import ReadPreference
except ImportError:
    pass


class MongoClientApiTest(unittest.TestCase):
    def test__read_preference(self):
        client = mongomock.MongoClient()
        self.assertEqual('Primary', client.read_preference.name)
        self.assertEqual(client.read_preference, client.db.read_preference)
        self.assertEqual(client.read_preference, client.db.coll.read_preference)

        client2 = mongomock.MongoClient(read_preference=client.read_preference)
        self.assertEqual(client2.read_preference, client.read_preference)

        with self.assertRaises(TypeError):
            mongomock.MongoClient(read_preference=0)

    def test__different_read_preference(self):
        client = mongomock.MongoClient(read_preference=ReadPreference.NEAREST)
        self.assertEqual(ReadPreference.NEAREST, client.db.read_preference)
        self.assertEqual(ReadPreference.NEAREST, client.db.coll.read_preference)

    def test__codec_options_with_pymongo(self):
        client = mongomock.MongoClient()
        self.assertEqual(codec_options.CodecOptions(), client.codec_options)
        self.assertFalse(client.codec_options.tz_aware)

    def test__codec_options(self):
        client = mongomock.MongoClient()
        self.assertFalse(client.codec_options.tz_aware)

        client = mongomock.MongoClient(tz_aware=True)
        self.assertTrue(client.codec_options.tz_aware)
        self.assertTrue(client.db.collection.codec_options.tz_aware)

        with self.assertRaises(TypeError):
            mongomock.MongoClient(tz_aware='True')

    def test__codec_options_to_pymongo_forwards_all_params(self):
        from collections import OrderedDict

        from mongomock_ng.codec_options import CodecOptions as MockCodecOptions

        opts = MockCodecOptions(
            document_class=OrderedDict,
            tz_aware=True,
            uuid_representation=3,
            unicode_decode_error_handler='ignore',
        )
        result = opts.to_pymongo()
        self.assertEqual(OrderedDict, result.document_class)
        self.assertTrue(result.tz_aware)
        self.assertEqual(3, result.uuid_representation)
        self.assertEqual('ignore', result.unicode_decode_error_handler)

    def test__codec_options_document_class_cast(self):
        from collections import OrderedDict

        from mongomock_ng.codec_options import CodecOptions as MockCodecOptions

        client = mongomock.MongoClient()
        client.db.collection.with_options(
            codec_options=MockCodecOptions(document_class=OrderedDict)
        ).insert_one({'key': 'value'})
        result = client.db.collection.with_options(
            codec_options=MockCodecOptions(document_class=OrderedDict)
        ).find_one()
        self.assertIsInstance(result, OrderedDict)

    def test__codec_options_custom_type_registry(self):
        from mongomock_ng.codec_options import CodecOptions as MockCodecOptions

        class CustomType:
            pass

        class CustomTypeCodec(codec_options.TypeCodec):
            @property
            def python_type(self):
                return CustomType

            @property
            def bson_type(self):
                return int

            def transform_python(self, value):
                return 42

            def transform_bson(self, value):
                return CustomType()

        registry = codec_options.TypeRegistry([CustomTypeCodec()])
        opts = MockCodecOptions(type_registry=registry)
        result = opts.to_pymongo()
        self.assertIsNotNone(result)

    def test__codec_options_uuid_representation_string(self):
        client = mongomock.MongoClient(uuidRepresentation='standard')
        opts = client.codec_options
        result = opts.to_pymongo()
        self.assertEqual(4, result.uuid_representation)

    def test__parse_url(self):
        client = mongomock.MongoClient('mongodb://localhost:27017/')
        self.assertEqual(('localhost', 27017), client.address)

        client = mongomock.MongoClient('mongodb://localhost:1234,example.com/')
        self.assertEqual(('localhost', 1234), client.address)

        client = mongomock.MongoClient('mongodb://example.com,localhost:1234/')
        self.assertEqual(('example.com', 27017), client.address)

        client = mongomock.MongoClient('mongodb://[::1]:1234/')
        self.assertEqual(('::1', 1234), client.address)

        with self.assertRaises(ValueError):
            mongomock.MongoClient('mongodb://localhost:1234:456/')

        with self.assertRaises(ValueError):
            mongomock.MongoClient('mongodb://localhost:123456/')

        with self.assertRaises(ValueError):
            mongomock.MongoClient('mongodb://localhost:mongoport/')

    def test__equality(self):
        self.assertEqual(
            mongomock.MongoClient('mongodb://localhost:27017/'),
            mongomock.MongoClient('mongodb://localhost:27017/'),
        )
        self.assertEqual(
            mongomock.MongoClient('mongodb://localhost:27017/'),
            mongomock.MongoClient('localhost'),
        )
        self.assertNotEqual(
            mongomock.MongoClient('/var/socket/mongo.sock'),
            mongomock.MongoClient('localhost'),
        )

    @skipIf(sys.version_info < (3,), 'Older versions of Python do not handle hashing the same way')
    def test__hashable(self):
        {mongomock.MongoClient('localhost')}  # pylint: disable=expression-not-assigned

    def test__parse_hosts(self):
        client = mongomock.MongoClient('localhost')
        self.assertEqual(('localhost', 27017), client.address)

        client = mongomock.MongoClient('localhost:1234,example.com')
        self.assertEqual(('localhost', 1234), client.address)

        client = mongomock.MongoClient('example.com,localhost:1234')
        self.assertEqual(('example.com', 27017), client.address)

        client = mongomock.MongoClient('[::1]:1234')
        self.assertEqual(('::1', 1234), client.address)

        client = mongomock.MongoClient('/var/socket/mongo.sock')
        self.assertEqual(('/var/socket/mongo.sock', None), client.address)

        with self.assertRaises(ValueError):
            mongomock.MongoClient('localhost:1234:456')

        with self.assertRaises(ValueError):
            mongomock.MongoClient('localhost:123456')

        with self.assertRaises(ValueError):
            mongomock.MongoClient('localhost:mongoport')

    def test_list_database_names(self):
        client = mongomock.MongoClient()
        self.assertEqual([], client.list_database_names())

        # Query a non existant collection.
        client.one_db.my_collec.find_one()
        self.assertEqual([], client.list_database_names())

        client.one_db.my_collec.insert_one({})
        self.assertEqual(['one_db'], client.list_database_names())

    def test_client_implements_context_managers(self):
        with mongomock.MongoClient() as client:
            client.one_db.my_collec.insert_one({})
            result = client.one_db.my_collec.find_one({})
            self.assertTrue(result)

    def test_start_session(self):
        client = mongomock.MongoClient()
        session = client.start_session()
        self.assertIsNotNone(session)
        self.assertFalse(session.has_ended)
        self.assertFalse(session.in_transaction)
        session.end_session()
        self.assertTrue(session.has_ended)

    @mock.patch('mongomock.SERVER_VERSION', '3.6')
    def test_server_version(self):
        client = mongomock.MongoClient()
        server_info = client.server_info()
        self.assertEqual('3.6', server_info['version'])
        self.assertEqual([3, 6, 0, 0], server_info['versionArray'])

    def test_consistent_server_version(self):
        client = mongomock.MongoClient()
        server_info = client.server_info()
        with mock.patch('mongomock.SERVER_VERSION', '3.6'):
            self.assertEqual(server_info, client.server_info())

    def test_close_clears_data(self):
        client = mongomock.MongoClient()
        client.db.col.insert_one({'x': 1})
        self.assertEqual(['db'], client.list_database_names())
        client.close()
        self.assertEqual([], client._store.list_created_database_names())
        self.assertEqual({}, client._database_accesses)

    def test_close_raises_on_subsequent_use(self):
        client = mongomock.MongoClient()
        client.close()
        with self.assertRaises(mongomock.InvalidOperation):
            client.get_database('test')
        with self.assertRaises(mongomock.InvalidOperation):
            client.list_database_names()
        with self.assertRaises(mongomock.InvalidOperation):
            client.drop_database('test')
        with self.assertRaises(mongomock.InvalidOperation):
            client.server_info()
        with self.assertRaises(mongomock.InvalidOperation):
            client.alive()
        with self.assertRaises(mongomock.InvalidOperation):
            client.start_session()

    def test_close_via_context_manager(self):
        with mongomock.MongoClient() as client:
            client.db.col.insert_one({'x': 1})
        with self.assertRaises(mongomock.InvalidOperation):
            client.list_database_names()

    def test_close_frees_memory(self):
        client = mongomock.MongoClient()
        db = client.db
        col = db.col
        col.insert_one({'x': 1})
        self.assertIn('db', client._database_accesses)
        self.assertIn('col', db._collection_accesses)
        client.close()
        self.assertNotIn('db', client._database_accesses)
        self.assertEqual({}, client._store._databases)
