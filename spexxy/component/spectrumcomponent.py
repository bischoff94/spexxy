from typing import Callable

from .component import Component
from ..data import LOSVD, Spectrum


class SpectrumComponent(Component):
    """SpectrumComponent is the base Component class for all components that deal with spectra."""

    def __init__(self, name: str, model_func: Callable, losvd_hermite: bool = False, vac_to_air: bool = False,
                 *args, **kwargs):
        """Initializes a new SpectrumComponent.

        Parameters
        ----------
        name : str
            Name of new component
        model_func : Callable
            Method that returns a spectrum for the given parameters, should be implemented by derived classes
        losvd_hermite : bool
            Whether or not Hermite polynomials should be used for the LOSVD
        vac_to_air : bool
            If True, vac_to_air() is called on spectra returned from the model_func
        """
        Component.__init__(self, name, *args, **kwargs)
        self._vac_to_air = vac_to_air
        self._model_func = model_func
        self._losvd_hermite = losvd_hermite

        # add losvd parameters
        self.set('v', min=-2000., max=2000., value=1.)
        self.set('sig', min=0., max=500., value=10.)
        if self._losvd_hermite:
            self.set('h3', min=-0.3, max=0.3, value=0.)
            self.set('h4', min=-0.3, max=0.3, value=0.)
            self.set('h5', min=-0.3, max=0.3, value=0.)
            self.set('h6', min=-0.3, max=0.3, value=0.)

    def __call__(self, **kwargs):
        """Model function that creates a spectrum with the given parameters and shift/convolve it using the given LOSVD.

        Parameters
        ----------
        **kwargs
            Values to overwrite

        Returns
        -------
        Spectrum
            The model from the component
        """

        # overwrite any?
        for key, val in kwargs.items():
            if key in self.parameters:
                self.set(key, value=val)

        # get LOSVD parameters
        losvd_params = ['v', 'sig'] + (['h3', 'h4', 'h5', 'h6'] if self._losvd_hermite else [])
        losvd = [self[p] for p in losvd_params]

        # get  model
        model = self._model_func()

        # apply losvd
        self._apply_losvd(model, losvd)

        # vac2air
        if self._vac_to_air:
            model.vac_to_air()

        # return result
        return model

    @staticmethod
    def _apply_losvd(model, losvd):
        """Apply LOSVD with the given parameters to the given model.

        WARNING: We will NOT FIT line broadening, if model spectra are in LAMBDA mode!

        Parameters
        ----------
        model
            Model to apply LOSVD to.
        losvd : list
            LOSVD parameters (v, sig, <h3, h4, h5, h6>)
        """
        if losvd[1] < 1e-5 or model.wave_mode == Spectrum.Mode.LAMBDA:
            # in LAMBDA mode, no LOSVD is supported
            model.redshift(losvd[0])
        else:
            # full LOSVD for sig>0 and LOG mode
            if model.wave_step == 0:
                # resample to const, if necessary
                model = model.resample_const()
            # apply losvd
            losvd = LOSVD(losvd)
            model.flux = losvd(model)


__all__ = ['SpectrumComponent']
