"""
Helper classes for comparing the equality of two HoloViews objects.

These classes are designed to integrate with unittest.TestCase (see
the tests directory) while making equality testing easily accessible
to the user.

For instance, to test if two Matrix objects are equal you can use:

Comparison.assertEqual(matrix1, matrix2)

This will raise an AssertionError if the two matrix objects are not
equal, including information regarding what exactly failed to match.

Note that this functionality could not be provided using comparison
methods on all objects as comparison opertors only return Booleans and
thus would not supply any information regarding *why* two elements are
considered different.
"""
import numpy as np
from unittest.util import safe_repr
from unittest import TestCase
from numpy.testing import assert_array_equal, assert_array_almost_equal

from . import *    # noqa (All Elements need to support comparison)
from ..core import (Element, Empty, AdjointLayout, Overlay, Dimension,
                    HoloMap, Dimensioned, Layout, NdLayout, NdOverlay,
                    GridSpace, DynamicMap, GridMatrix)
from ..core.options import Options, Cycle
from ..interface.pandas import DFrame as PandasDFrame
from ..interface.pandas import DataFrameView
from ..interface.seaborn import DFrame, Bivariate, Distribution, \
                                Regression, TimeSeries


class ComparisonInterface(object):
    """
    This class is designed to allow equality testing to work
    seamlessly with unittest.TestCase as a mix-in by implementing a
    compatible interface (namely the assertEqual method).

    The assertEqual class method is to be overridden by an instance
    method of the same name when used as a mix-in with TestCase. The
    contents of the equality_type_funcs dictionary is suitable for use
    with TestCase.addTypeEqualityFunc.
    """

    equality_type_funcs = {}
    failureException = AssertionError

    @classmethod
    def simple_equality(cls, first, second, msg=None):
        """
        Classmethod equivalent to unittest.TestCase method (longMessage = False.)
        """
        if not first==second:
            standardMsg = '%s != %s' % (safe_repr(first), safe_repr(second))
            raise cls.failureException(msg or standardMsg)


    @classmethod
    def assertEqual(cls, first, second, msg=None):
        """
        Classmethod equivalent to unittest.TestCase method
        """
        asserter = None
        if type(first) is type(second):
            asserter = cls.equality_type_funcs.get(type(first))

            try:              basestring = basestring # Python 2
            except NameError: basestring = str        # Python 3

            if asserter is not None:
                if isinstance(asserter, basestring):
                    asserter = getattr(cls, asserter)

        if asserter is None:
            asserter = cls.simple_equality

        if msg is None:
            asserter(first, second)
        else:
            asserter(first, second, msg=msg)


class Comparison(ComparisonInterface):
    """
    Class used for comparing two HoloViews objects, including complex
    composite objects. Comparisons are available as classmethods, the
    most general being the assertEqual method that is intended to work
    with any input.

    For instance, to test if two Image objects are equal you can use:

    Comparison.assertEqual(matrix1, matrix2)
    """

    @classmethod
    def register(cls):

        # Float comparisons
        cls.equality_type_funcs[float] =        cls.compare_floats
        cls.equality_type_funcs[np.float] =     cls.compare_floats
        cls.equality_type_funcs[np.float32] =   cls.compare_floats
        cls.equality_type_funcs[np.float64] =   cls.compare_floats

        #Dictionary comparisons
        cls.equality_type_funcs[dict] =        cls.compare_dictionaries

        # Numpy array comparison
        cls.equality_type_funcs[np.ndarray] =   cls.compare_arrays

        # Dimension objects
        cls.equality_type_funcs[Dimension] =    cls.compare_dimensions
        cls.equality_type_funcs[Dimensioned] =  cls.compare_dimensioned  # Used in unit tests
        cls.equality_type_funcs[Element]     =  cls.compare_elements     # Used in unit tests

        # Composition (+ and *)
        cls.equality_type_funcs[Overlay] =     cls.compare_overlays
        cls.equality_type_funcs[Layout] =      cls.compare_layouttrees
        cls.equality_type_funcs[Empty] =       cls.compare_empties

        # Annotations
        cls.equality_type_funcs[VLine] =       cls.compare_vline
        cls.equality_type_funcs[HLine] =       cls.compare_hline
        cls.equality_type_funcs[Spline] =      cls.compare_spline
        cls.equality_type_funcs[Arrow] =       cls.compare_arrow
        cls.equality_type_funcs[Text] =        cls.compare_text


        # Path comparisons
        cls.equality_type_funcs[Path] =        cls.compare_paths
        cls.equality_type_funcs[Contours] =    cls.compare_contours
        cls.equality_type_funcs[Polygons] =    cls.compare_polygons
        cls.equality_type_funcs[Box] =         cls.compare_box
        cls.equality_type_funcs[Ellipse] =     cls.compare_ellipse
        cls.equality_type_funcs[Bounds] =      cls.compare_bounds

        # Rasters
        cls.equality_type_funcs[Image] =       cls.compare_image
        cls.equality_type_funcs[RGB] =         cls.compare_rgb
        cls.equality_type_funcs[HSV] =         cls.compare_hsv
        cls.equality_type_funcs[Raster] =      cls.compare_raster
        cls.equality_type_funcs[QuadMesh] =    cls.compare_quadmesh
        cls.equality_type_funcs[Surface] =     cls.compare_surface
        cls.equality_type_funcs[HeatMap] =     cls.compare_dataset

        # Charts
        cls.equality_type_funcs[Dataset] =      cls.compare_dataset
        cls.equality_type_funcs[Curve] =        cls.compare_curve
        cls.equality_type_funcs[ErrorBars] =    cls.compare_errorbars
        cls.equality_type_funcs[Spread] =       cls.compare_spread
        cls.equality_type_funcs[Area] =         cls.compare_area
        cls.equality_type_funcs[Scatter] =      cls.compare_scatter
        cls.equality_type_funcs[Scatter3D] =    cls.compare_scatter3d
        cls.equality_type_funcs[Trisurface] =   cls.compare_trisurface
        cls.equality_type_funcs[Histogram] =    cls.compare_histogram
        cls.equality_type_funcs[Bars] =         cls.compare_bars
        cls.equality_type_funcs[Spikes] =       cls.compare_spikes
        cls.equality_type_funcs[BoxWhisker] =   cls.compare_boxwhisker
        cls.equality_type_funcs[VectorField] =  cls.compare_vectorfield

        # Tables
        cls.equality_type_funcs[ItemTable] =    cls.compare_itemtables
        cls.equality_type_funcs[Table] =        cls.compare_tables
        cls.equality_type_funcs[Points] =       cls.compare_points

        # Pandas DFrame objects
        cls.equality_type_funcs[DataFrameView] = cls.compare_dframe
        cls.equality_type_funcs[PandasDFrame] =  cls.compare_dframe
        cls.equality_type_funcs[DFrame] =        cls.compare_dframe

        # Seaborn Views
        cls.equality_type_funcs[Bivariate] =    cls.compare_bivariate
        cls.equality_type_funcs[Distribution] = cls.compare_distribution
        cls.equality_type_funcs[Regression] =   cls.compare_regression
        cls.equality_type_funcs[TimeSeries] =   cls.compare_timeseries

        # NdMappings
        cls.equality_type_funcs[NdLayout] =      cls.compare_gridlayout
        cls.equality_type_funcs[AdjointLayout] = cls.compare_adjointlayouts
        cls.equality_type_funcs[NdOverlay] =     cls.compare_ndoverlays
        cls.equality_type_funcs[GridSpace] =     cls.compare_grids
        cls.equality_type_funcs[GridMatrix] =     cls.compare_grids
        cls.equality_type_funcs[HoloMap] =       cls.compare_holomap
        cls.equality_type_funcs[DynamicMap] =    cls.compare_dynamicmap

        # Option objects
        cls.equality_type_funcs[Options] =     cls.compare_options
        cls.equality_type_funcs[Cycle] =       cls.compare_cycles

        return cls.equality_type_funcs


    @classmethod
    def compare_dictionaries(cls, d1, d2, msg='Dictionaries'):
        keys= set(d1.keys())
        keys2 = set(d2.keys())
        symmetric_diff = keys ^ keys2
        if symmetric_diff:
            msg = ("Dictionaries have different sets of keys: %r\n\n"
                   % symmetric_diff)
            msg += "Dictionary 1: %s\n" % d1
            msg += "Dictionary 2: %s" % d2
            raise cls.failureException(msg)
        for k in keys:
            cls.assertEqual(d1[k], d2[k])

    #=====================#
    # Literal comparisons #
    #=====================#

    @classmethod
    def compare_floats(cls, arr1, arr2, msg='Floats'):
        cls.compare_arrays(arr1, arr2, msg)

    @classmethod
    def compare_arrays(cls, arr1, arr2, msg='Arrays'):
        try:
            assert_array_equal(arr1, arr2)
        except:
            try:
                assert_array_almost_equal(arr1, arr2)
            except AssertionError as e:
                raise cls.failureException(msg + str(e)[11:])

    @classmethod
    def bounds_check(cls, el1, el2, msg=None):
        if el1.bounds.lbrt() != el2.bounds.lbrt():
            raise cls.failureException("BoundingBoxes are mismatched.")


    #=======================================#
    # Dimension and Dimensioned comparisons #
    #=======================================#


    @classmethod
    def compare_dimensions(cls, dim1, dim2, msg=None):
        if dim1.name != dim2.name:
            raise cls.failureException("Dimension names mismatched: %s != %s"
                                       % (dim1.name, dim2.name))
        if dim1.cyclic != dim2.cyclic:
            raise cls.failureException("Dimension cyclic declarations mismatched.")
        if dim1.range != dim2.range:
            raise cls.failureException("Dimension ranges mismatched: %s != %s"
                                       % (dim1.range, dim2.range))
        if dim1.type != dim2.type:
            raise cls.failureException("Dimension type declarations mismatched: %s != %s"
                                       % (dim1.type,dim2.type))
        if dim1.unit != dim2.unit:
            raise cls.failureException("Dimension unit declarations mismatched: %s != %s"
                                       % (dim1.unit , dim2.unit))
        if dim1.values != dim2.values:
            raise cls.failureException("Dimension value declarations mismatched: %s != %s"
                                       % (dim1.values , dim2.values))

    @classmethod
    def compare_labelled_data(cls, obj1, obj2, msg=None):
        cls.assertEqual(obj1.group, obj2.group, "Group labels mismatched.")
        cls.assertEqual(obj1.label, obj2.label, "Labels mismatched.")

    @classmethod
    def compare_dimension_lists(cls, dlist1, dlist2, msg='Dimension lists'):
        if len(dlist1) != len(dlist2):
            raise cls.failureException('%s mismatched' % msg)
        for d1, d2 in zip(dlist1, dlist2):
            cls.assertEqual(d1, d2)

    @classmethod
    def compare_dimensioned(cls, obj1, obj2, msg=None):
        cls.compare_labelled_data(obj1, obj2)
        cls.compare_dimension_lists(obj1.vdims, obj2.vdims,
                                    'Value dimension list')
        cls.compare_dimension_lists(obj1.kdims, obj2.kdims,
                                    'Key dimension list')

    @classmethod
    def compare_elements(cls, obj1, obj2, msg=None):
        cls.compare_labelled_data(obj1, obj2)
        cls.assertEqual(obj1.data, obj2.data)


    #===============================#
    # Compositional trees (+ and *) #
    #===============================#

    @classmethod
    def compare_trees(cls, el1, el2, msg='Trees'):
        if len(el1.keys()) != len(el2.keys()):
            raise cls.failureException("%s have mismatched path counts." % msg)
        if el1.keys() != el2.keys():
            raise cls.failureException("%s have mismatched paths." % msg)
        for element1, element2 in zip(el1.values(),  el2.values()):
            cls.assertEqual(element1, element2)

    @classmethod
    def compare_layouttrees(cls, el1, el2, msg=None):
        cls.compare_dimensioned(el1, el2)
        cls.compare_trees(el1, el2, msg='Layouts')

    @classmethod
    def compare_empties(cls, el1, el2, msg=None):
        if not all(isinstance(el, Empty) for el in [el1, el2]):
            raise cls.failureException("Compared elements are not both Empty()")

    @classmethod
    def compare_overlays(cls, el1, el2, msg=None):
        cls.compare_dimensioned(el1, el2)
        cls.compare_trees(el1, el2, msg='Overlays')


    #================================#
    # AttrTree and Map based classes #
    #================================#

    @classmethod
    def compare_ndmappings(cls, el1, el2, msg='NdMappings'):
        cls.compare_dimensioned(el1, el2)
        if len(el1.keys()) != len(el2.keys()):
            raise cls.failureException("%s have different numbers of keys." % msg)

        if set(el1.keys()) != set(el2.keys()):
            diff1 = [el for el in el1.keys() if el not in el2.keys()]
            diff2 = [el for el in el2.keys() if el not in el1.keys()]
            raise cls.failureException("%s have different sets of keys. " % msg
                                       + "In first, not second %s. " % diff1
                                       + "In second, not first: %s." % diff2)

        for element1, element2 in zip(el1, el2):
            cls.assertEqual(element1, element2)

    @classmethod
    def compare_holomap(cls, el1, el2, msg='HoloMaps'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_ndmappings(el1, el2, msg)


    @classmethod
    def compare_dynamicmap(cls, el1, el2, msg='DynamicMap'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_ndmappings(el1, el2, msg)


    @classmethod
    def compare_gridlayout(cls, el1, el2, msg=None):
        cls.compare_dimensioned(el1, el2)

        if len(el1) != len(el2):
            raise cls.failureException("Layouts have different sizes.")

        if set(el1.keys()) != set(el2.keys()):
            raise cls.failureException("Layouts have different keys.")

        for element1, element2 in zip(el1, el2):
            cls.assertEqual(element1,element2)


    @classmethod
    def compare_ndoverlays(cls, el1, el2, msg=None):
        cls.compare_dimensioned(el1, el2)
        if len(el1) != len(el2):
            raise cls.failureException("NdOverlays have different lengths.")

        for (layer1, layer2) in zip(el1, el2):
            cls.assertEqual(layer1, layer2)

    @classmethod
    def compare_adjointlayouts(cls, el1, el2, msg=None):
        cls.compare_dimensioned(el1, el2)
        for element1, element2 in zip(el1, el1):
            cls.assertEqual(element1, element2)


    #=============#
    # Annotations #
    #=============#

    @classmethod
    def compare_annotation(cls, el1, el2, msg='Annotation'):
        cls.compare_dimensioned(el1, el2)
        cls.assertEqual(el1.data, el2.data)

    @classmethod
    def compare_hline(cls, el1, el2, msg='HLine'):
        cls.compare_annotation(el1, el2, msg=msg)

    @classmethod
    def compare_vline(cls, el1, el2, msg='VLine'):
        cls.compare_annotation(el1, el2, msg=msg)

    @classmethod
    def compare_spline(cls, el1, el2, msg='Spline'):
        cls.compare_annotation(el1, el2, msg=msg)

    @classmethod
    def compare_arrow(cls, el1, el2, msg='Arrow'):
        cls.compare_annotation(el1, el2, msg=msg)

    @classmethod
    def compare_text(cls, el1, el2, msg='Text'):
        cls.compare_annotation(el1, el2, msg=msg)


    #=======#
    # Paths #
    #=======#

    @classmethod
    def compare_paths(cls, el1, el2, msg='Path'):
        cls.compare_dimensioned(el1, el2)

        if len(el1.data) != len(el2.data):
            raise cls.failureException("%s objects do not have a matching number of paths." % msg)
        for arr1, arr2 in zip(el1.data, el2.data):
            cls.compare_arrays(arr1, arr2, '%s data' % msg)

    @classmethod
    def compare_contours(cls, el1, el2, msg='Contours'):
        if el1.level != el2.level:
            raise cls.failureException("Contour levels are mismatched")
        cls.compare_paths(el1, el2, msg=msg)

    @classmethod
    def compare_polygons(cls, el1, el2, msg='Polygons'):
        if el1.level != el2.level:
            raise cls.failureException("Polygon levels are mismatched")
        cls.compare_paths(el1, el2, msg=msg)

    @classmethod
    def compare_box(cls, el1, el2, msg='Box'):
        cls.compare_paths(el1, el2, msg=msg)

    @classmethod
    def compare_ellipse(cls, el1, el2, msg='Ellipse'):
        cls.compare_paths(el1, el2, msg=msg)

    @classmethod
    def compare_bounds(cls, el1, el2, msg='Bounds'):
        cls.compare_paths(el1, el2, msg=msg)


    #========#
    # Charts #
    #========#
    
    @classmethod
    def compare_dataset(cls, el1, el2, msg='Dataset'):
        cls.compare_dimensioned(el1, el2)
        if len(el1) != len(el2):
            raise AssertionError("%s not of matching length." % msg)
        dimension_data = [(d, el1[d], el2[d]) for d in el1.dimensions()]
        for dim, d1, d2 in dimension_data:
            if d1.dtype != d2.dtype:
                cls.failureException("%s %s columns have different type." % (msg, dim)
                                     + " First has type %s, and second has type %s."
                                     % (d1, d2))
            if d1.dtype.kind in 'SUOV':
                if list(d1) == list(d2):
                    cls.failureException("%s along dimension %s not equal." %
                                         (msg, dim))
            else:
                cls.compare_arrays(d1, d2, msg)


    @classmethod
    def compare_curve(cls, el1, el2, msg='Curve'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_errorbars(cls, el1, el2, msg='ErrorBars'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_spread(cls, el1, el2, msg='Spread'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_area(cls, el1, el2, msg='Area'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_scatter(cls, el1, el2, msg='Scatter'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_scatter3d(cls, el1, el2, msg='Scatter3D'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_trisurface(cls, el1, el2, msg='Trisurface'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_histogram(cls, el1, el2, msg='Histogram'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.edges, el2.edges, ' '.join([msg, 'edges']))
        cls.compare_arrays(el1.values, el2.values, ' '.join([msg, 'values']))

    @classmethod
    def compare_points(cls, el1, el2, msg='Points'):
        cls.compare_dataset(el1, el2, msg)


    @classmethod
    def compare_vectorfield(cls, el1, el2, msg='VectorField'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_bars(cls, el1, el2, msg='Bars'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_spikes(cls, el1, el2, msg='Spikes'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_boxwhisker(cls, el1, el2, msg='BoxWhisker'):
        cls.compare_dataset(el1, el2, msg)

    #=========#
    # Rasters #
    #=========#

    @classmethod
    def compare_raster(cls, el1, el2, msg='Raster'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data, el2.data, msg)

    @classmethod
    def compare_quadmesh(cls, el1, el2, msg='QuadMesh'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data[0], el2.data[0], ' '.join([msg, 'x-data']))
        cls.compare_arrays(el1.data[1], el2.data[1], ' '.join([msg, 'y-data']))
        cls.compare_arrays(el1.data[2], el2.data[2], ' '.join([msg, 'z-data']))

    @classmethod
    def compare_heatmap(cls, el1, el2, msg='HeatMap'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data, el2.data, msg)

    @classmethod
    def compare_image(cls, el1, el2, msg='Image'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data, el2.data, msg)
        cls.bounds_check(el1,el2)

    @classmethod
    def compare_rgb(cls, el1, el2, msg='RGB'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data, el2.data, msg=msg)
        cls.bounds_check(el1,el2)

    @classmethod
    def compare_hsv(cls, el1, el2, msg='HSV'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data, el2.data, msg=msg)
        cls.bounds_check(el1,el2)

    @classmethod
    def compare_surface(cls, el1, el2, msg='Surface'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data, el2.data, msg=msg)


    #========#
    # Tables #
    #========#

    @classmethod
    def compare_itemtables(cls, el1, el2, msg=None):
        cls.compare_dimensioned(el1, el2)
        if el1.rows != el2.rows:
            raise cls.failureException("ItemTables have different numbers of rows.")

        if el1.cols != el2.cols:
            raise cls.failureException("ItemTables have different numbers of columns.")

        if [d.name for d in el1.vdims] != [d.name for d in el2.vdims]:
            raise cls.failureException("ItemTables have different Dimensions.")


    @classmethod
    def compare_tables(cls, el1, el2, msg='Table'):
        cls.compare_dataset(el1, el2, msg)

    #========#
    # Pandas #
    #========#

    @classmethod
    def compare_dframe(cls, el1, el2, msg='DFrame'):
        cls.compare_dimensioned(el1, el2)
        from pandas.util.testing import assert_frame_equal
        try:
            df1 = el1.data.reset_index(drop=True)
            df2 = el2.data.reset_index(drop=True)
            assert_frame_equal(df1, df2)
        except AssertionError as e:
            raise cls.failureException(msg+': '+str(e))

    #=========#
    # Seaborn #
    #=========#

    @classmethod
    def compare_distribution(cls, el1, el2, msg='Distribution'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_timeseries(cls, el1, el2, msg='TimeSeries'):
        cls.compare_dimensioned(el1, el2)
        cls.compare_arrays(el1.data, el2.data, msg)

    @classmethod
    def compare_bivariate(cls, el1, el2, msg='Bivariate'):
        cls.compare_dataset(el1, el2, msg)

    @classmethod
    def compare_regression(cls, el1, el2, msg='Regression'):
        cls.compare_dataset(el1, el2, msg)

    #=======#
    # Grids #
    #=======#

    @classmethod
    def _compare_grids(cls, el1, el2, name):

        if len(el1.keys()) != len(el2.keys()):
            raise cls.failureException("%ss have different numbers of items." % name)

        if set(el1.keys()) != set(el2.keys()):
            raise cls.failureException("%ss have different keys." % name)

        if len(el1) != len(el2):
            raise cls.failureException("%ss have different depths." % name)

        for element1, element2 in zip(el1, el2):
            cls.assertEqual(element1, element2)

    @classmethod
    def compare_grids(cls, el1, el2, msg=None):
        cls.compare_dimensioned(el1, el2)
        cls._compare_grids(el1, el2, 'GridSpace')

    #=========#
    # Options #
    #=========#

    @classmethod
    def compare_options(cls, options1, options2, msg=None):
        cls.assertEqual(options1.kwargs, options2.kwargs)

    @classmethod
    def compare_cycles(cls, cycle1, cycle2, msg=None):
        cls.assertEqual(cycle1.values, cycle2.values)

    @classmethod
    def compare_channelopts(cls, opt1, opt2, msg=None):
        cls.assertEqual(opt1.mode, opt2.mode)
        cls.assertEqual(opt1.pattern, opt2.pattern)
        cls.assertEqual(opt1.patter, opt2.pattern)



class ComparisonTestCase(Comparison, TestCase):
    """
    Class to integrate the Comparison class with unittest.TestCase.
    """

    def __init__(self, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        registry = Comparison.register()
        for k, v in registry.items():
            self.addTypeEqualityFunc(k, v)
