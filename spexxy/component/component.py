from typing import Any
from lmfit import Parameters
import numpy as np

from spexxy.object import spexxyObject
from spexxy.data import FitsSpectrum


class Component(spexxyObject):
    """Base class for all Components in spexxy."""

    def __init__(self, name: str, init: list = None, prefix: str = None, *args, **kwargs):
        """Initialize a new component.

        Args:
            name: Name of component
            init: List of Init objects for initializing the component
            prefix: Prefix for parameter name when combined in other model. Automatically derived from name if None.
        """
        spexxyObject.__init__(self, *args, **kwargs)

        # name and prefix
        self.name = name
        self.prefix = prefix if prefix is not None else name

        # weight for params fit
        self.weight = 1.

        # parameters
        self.parameters = {}

        # create init functions
        from spexxy.init import Init
        self._init = [] if init is None else self.get_objects(init, Init, 'init')

    def __call__(self, **params) -> Any:
        """Model function, must be implemented.

        Args:
            params: Parameters to retrieve model for

        Returns:
            The model from the component
        """
        raise NotImplementedError

    @property
    def param_names(self):
        return sorted(self.parameters.keys())

    def set(self, name, **kwargs):
        """Adds a new parameter with the given name or changes values of an existing one.

        Args:
            name(str): Parameter name.
            value (float): (Initial) Value of parameter
            stderr (float): Standard deviation after fit
            vary (bool): Whether or not to vary the parameter in the fit
            min (float): Lower bound for fit (default is `-numpy.inf`, no lower bound)
            max (float): Upper bound for value (default is `numpy.inf`, no upper bound)
            kwargs: Passed to set_param_hint()
        """

        # remove prefix from name if exists
        n = len(self.prefix)
        if n > 0 and name.startswith(self.prefix):
            name = name[n:]

        # add parameter if not exists
        if name not in self.parameters:
            self.parameters[name] = {}

        # set values
        for key, val in kwargs.items():
            if key in ('value', 'stderr', 'vary', 'min', 'max'):
                self.parameters[name][key] = val

    def __getitem__(self, name: str) -> float:
        """Returns the value for an existing parameter.

        Args:
            name: Name of parameter for which to return the value

        Returns:
            Value of given parameter

        Raises:
            KeyError: If given parameter does not exist
        """
        return self.parameters[name]['value'] if 'value' in self.parameters[name] else None

    def __setitem__(self, name: str, value: float):
        """Returns the value for an existing parameter.

        Args:
            name: Name of parameter to set
            value: New value for parameter
        """
        self.set(name, value=value)

    def make_params(self, **kwargs) -> Parameters:
        """Creates a Parameters object with a Parameter for each parameter of this component.

        Args:
            kwargs: Values to overwrite in parameters

        Returns:
            List of Parameters for this component
        """

        # init params
        params = Parameters()

        # remove prefixes from kwargs if exists
        n = len(self.prefix)
        overwrite = {key[n:]: value for key, value in kwargs.items() if n > 0 and key.startswith(self.prefix)}

        # loop all parameters
        for name, p in self.parameters.items():
            # copy p
            param = dict(p)

            # overwrite value?
            if name in overwrite:
                param['value'] = overwrite[name]

            # default values
            for key, val in {'value': None, 'vary': True, 'min': -np.inf, 'max': np.inf}.items():
                if key not in param:
                    param[key] = val

            # remove stderr
            for k in ['stderr']:
                if k in param:
                    del param['stderr']

            # add it to params
            params.add(self.prefix + name, **param)

        # return it
        return params

    def parse_params(self, params: Parameters):
        """Loop all Parameters in a Parameters object and set the values of this component accordingly.

        Args:
            params: Parameters objects, usually return from a lmfit optimization
        """

        # length of prefix
        n = len(self.prefix)

        # loop parameters
        for name, param in params.items():
            # does prefix match?
            if n > 0 and name.startswith(self.prefix):
                # remove prefix
                name = name[n:]

                # does it exist?
                if name in self.parameters:
                    # set it
                    self.set(name, value=param.value, stderr=param.stderr)

    def init(self, filename: str):
        """Calls all Init objects with the given filename in order to initialize this component.

        Args:
            filename: File to initialize with, may be optional for some Init objects
        """
        for fcn in self._init:
            fcn(self, filename)

    def write_results_to_file(self, fits_file: FitsSpectrum):
        """Write results of this component into a given SpectrumFile

        Args:
            fits_file: Opened FitsSpectrum to write results into
        """

        # get results object
        params = fits_file.results(self.prefix)

        # loop parameter names
        for name, param in self.parameters.items():
            # write results into results object
            vary = 'vary' not in param or param['vary'] is True
            params[name] = [param['value'], param['stderr'] if vary else None]


__all__ = ['Component']
