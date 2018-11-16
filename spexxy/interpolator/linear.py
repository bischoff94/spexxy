from typing import List, Tuple

from . import Interpolator
from ..grid import Grid, GridAxis
from ..data import Spectrum


class LinearInterpolator(Interpolator):
    """A basic linear interpolator that operates on a given grid."""

    def __init__(self, grid: Grid, *args, **kwargs):
        """Initializes a new linear interpolator.

        Args:
            grid: Grid to interpolate on.
        """
        Interpolator.__init__(self, *args, **kwargs)

        # get grid
        self.log.info('Initializing linear interpolator...')
        self._grid = self.get_objects(grid, Grid, 'grids', single=True)
        self._axes = self._grid.axes()

    @property
    def grid(self) -> Grid:
        """Returns grid used in this interpolator

        Returns:
            Grid used for this interpolator
        """
        return self._grid

    def axes(self) -> List[GridAxis]:
        """Returns information about the axes.

        Returns:
            List of GridAxis objects describing the grid's axes
        """
        return self._axes

    def __call__(self, params: Tuple) -> Spectrum:
        """Interpolates at the given parameter set

        Args:
            params: Parameter set to interpolate at

        Returns:
            Interpolated spectrum at given position
        """
        return self._interpolate(params)

    def _interpolate(self, params: Tuple, axis: int = None):
        """Do the actual interpolation at the given axis, then continue for axis-1.

        Args:
            params: Parameter set to interpolate at.
            axis: Axis to interpolate in - if None, we start at last available axis.

        Returns:
            Interpolated spectrum at given position.
        """

        # no axis given, start at latest
        if axis is None:
            axis = len(self._axes) - 1

        # check boundaries
        if params[axis] < self._axes[axis].min or params[axis] > self._axes[axis].max:
            raise KeyError('Requested parameters are outside the grid.')

        # let's get all possible values for the given axis
        axisValues = self._grid.axis_values(axis)

        # if params[axis] is on axis; return it directly
        if params[axis] in axisValues:
            if axis == 0:
                return self._grid(tuple(params))
            else:
                return self._interpolate(tuple(params), axis - 1)

        # find the next lower and the next higher axis value
        p_lower = self._grid.neighbour(tuple(params), axis, 0)
        p_higher = self._grid.neighbour(tuple(params), axis, 1)
        if p_lower is None or p_higher is None:
            raise KeyError('No direct neighbours found in grid.')

        # get axis values
        x_lower = p_lower[axis]
        x_higher = p_higher[axis]

        # get data for p_lower and p_higher
        if axis == 0:
            lower_data = self._grid(p_lower)
            higher_data = self._grid(p_higher)
        else:
            lower_data = self._interpolate(p_lower)
            higher_data = self._interpolate(p_higher)

        # interpolate
        f = (params[axis] - x_lower) / (x_higher - x_lower)
        ip = lower_data * (1. - f) + higher_data * f

        # return data
        return ip


__all__ = ['LinearInterpolator']