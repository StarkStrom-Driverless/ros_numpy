import unittest
import numpy as np

import ros_numpy
from sensor_msgs.msg import PointCloud2, PointField, Image
from ros_numpy import numpy_msg

class TestPointClouds(unittest.TestCase):
    def makeArray(self, npoints):
        points_arr = np.zeros((npoints,), dtype=[
            ('x', np.float32),
            ('y', np.float32),
            ('z', np.float32),
            ('r', np.uint8),
            ('g', np.uint8),
            ('b', np.uint8)])
        points_arr['x'] = np.random.random((npoints,))
        points_arr['y'] = np.random.random((npoints,))
        points_arr['z'] = np.random.random((npoints,))
        points_arr['r'] = np.floor(np.random.random((npoints,))*255)
        points_arr['g'] = 0
        points_arr['b'] = 255

        return points_arr

    def test_convert_dtype(self):
        fields = [
            PointField(name='x', offset=0, count=1, datatype=PointField.FLOAT32),
            PointField(name='y', offset=4, count=1, datatype=PointField.FLOAT32)
        ]
        dtype = np.dtype([
            ('x', np.float32),
            ('y', np.float32)
        ])
        conv_fields = ros_numpy.msgify(PointField, dtype, plural=True)
        self.assertSequenceEqual(fields, conv_fields, 'dtype->Pointfield Failed with simple values')

        conv_dtype = ros_numpy.numpify(fields, point_step=8)
        self.assertSequenceEqual(dtype, conv_dtype, 'dtype->Pointfield Failed with simple values')

    def test_convert_dtype_inner(self):
        fields = [
            PointField(name='x', offset=0, count=1, datatype=PointField.FLOAT32),
            PointField(name='y', offset=4, count=1, datatype=PointField.FLOAT32),
            PointField(name='vectors', offset=8, count=3, datatype=PointField.FLOAT32)
        ]

        dtype = np.dtype([
            ('x', np.float32),
            ('y', np.float32),
            ('vectors', np.float32, (3,))
        ])

        conv_fields = ros_numpy.msgify(PointField, dtype, plural=True)
        self.assertSequenceEqual(fields, conv_fields, 'dtype->Pointfield with inner dimensions')

        conv_dtype = ros_numpy.numpify(fields, point_step=8)
        self.assertEqual(dtype, conv_dtype, 'Pointfield->dtype with inner dimensions')


    def test_roundtrip(self):

        points_arr = self.makeArray(100)
        cloud_msg = ros_numpy.msgify(PointCloud2, points_arr)
        new_points_arr = ros_numpy.numpify(cloud_msg)

        np.testing.assert_equal(points_arr, new_points_arr)

    def test_roundtrip_numpy(self):

        points_arr = self.makeArray(100)
        cloud_msg = ros_numpy.msgify(numpy_msg(PointCloud2), points_arr)
        new_points_arr = ros_numpy.numpify(cloud_msg)

        np.testing.assert_equal(points_arr, new_points_arr)

class TestImages(unittest.TestCase):
    def test_roundtrip_rgb8(self):
        arr = np.random.randint(0, 256, size=(240, 360, 3)).astype(np.uint8)
        msg = ros_numpy.msgify(Image, arr, encoding='rgb8')
        arr2 = ros_numpy.numpify(msg)

        np.testing.assert_equal(arr, arr2)

    def test_roundtrip_mono(self):
        arr = np.random.randint(0, 256, size=(240, 360)).astype(np.uint8)
        msg = ros_numpy.msgify(Image, arr, encoding='mono8')
        arr2 = ros_numpy.numpify(msg)

        np.testing.assert_equal(arr, arr2)

    def test_bad_encodings(self):
        mono_arr = np.random.randint(0, 256, size=(240, 360)).astype(np.uint8)
        mono_arrf = np.random.randint(0, 256, size=(240, 360)).astype(np.float32)
        rgb_arr = np.random.randint(0, 256, size=(240, 360, 3)).astype(np.uint8)
        rgb_arrf = np.random.randint(0, 256, size=(240, 360, 3)).astype(np.float32)

        with self.assertRaises(TypeError):
            msg = ros_numpy.msgify(Image, rgb_arr, encoding='mono8')
        with self.assertRaises(TypeError):
            msg = ros_numpy.msgify(Image, mono_arrf, encoding='mono8')

        with self.assertRaises(TypeError):
            msg = ros_numpy.msgify(Image, rgb_arrf, encoding='rgb8')
        with self.assertRaises(TypeError):
            msg = ros_numpy.msgify(Image, mono_arr, encoding='rgb8')


if __name__ == '__main__':
    unittest.main()
    # import rostest
    # rostest.rosrun('ros_numpy', 'test_point_cloud', TestPointClouds)